import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class Order {
    String id;
    boolean buy;
    int price;
    int remaining;
    int priority;
    Integer expiresAt = null;
    String state = "open";
}

public class Simulation {
    private final Map<String, Order> orders = new HashMap<>();
    private final List<Order> book = new ArrayList<>();
    private final List<Order> stops = new ArrayList<>();
    private final List<String> trades = new ArrayList<>();
    private Integer lastPrice = null;
    private int nextPriority = 0;

    public Simulation() {}

    private boolean validSide(String side) {
        return "buy".equals(side) || "sell".equals(side);
    }

    private void expire(int timestamp) {
        List<Order> live = new ArrayList<>();
        for (Order order : book) {
            if (order.expiresAt != null && timestamp >= order.expiresAt) {
                order.state = "expired";
            } else {
                live.add(order);
            }
        }
        book.clear();
        book.addAll(live);
    }

    private Order create(String id, String side, int price, int quantity) {
        Order order = new Order();
        order.id = id;
        order.buy = "buy".equals(side);
        order.price = price;
        order.remaining = quantity;
        order.priority = nextPriority;
        nextPriority += 1;
        orders.put(id, order);
        return order;
    }

    /** Resting orders the incoming order may trade with, best first. */
    private List<Order> candidates(Order incoming, Integer limit) {
        List<Order> out = new ArrayList<>();
        for (Order order : book) {
            if (order.buy == incoming.buy) {
                continue;
            }
            if (limit != null && (incoming.buy ? order.price > limit : order.price < limit)) {
                continue;
            }
            out.add(order);
        }
        out.sort(
                (a, b) -> {
                    if (a.price != b.price) {
                        return incoming.buy ? a.price - b.price : b.price - a.price;
                    }
                    return a.priority - b.priority;
                });
        return out;
    }

    private int execute(Order incoming, Integer limit) {
        int filled = 0;
        for (Order resting : candidates(incoming, limit)) {
            if (incoming.remaining == 0) {
                break;
            }
            int quantity = Math.min(incoming.remaining, resting.remaining);
            incoming.remaining -= quantity;
            resting.remaining -= quantity;
            filled += quantity;
            String buyId = incoming.buy ? incoming.id : resting.id;
            String sellId = incoming.buy ? resting.id : incoming.id;
            trades.add(buyId + ":" + sellId + ":" + resting.price + ":" + quantity);
            lastPrice = resting.price;
            if (resting.remaining == 0) {
                resting.state = "filled";
                book.remove(resting);
            }
        }
        return filled;
    }

    private void triggerStops() {
        while (lastPrice != null) {
            Order hit = null;
            for (Order stop : stops) {
                if (stop.buy ? lastPrice >= stop.price : lastPrice <= stop.price) {
                    hit = stop;
                    break;
                }
            }
            if (hit == null) {
                return;
            }
            stops.remove(hit);
            execute(hit, null);
            hit.state = hit.remaining == 0 ? "filled" : "cancelled";
        }
    }

    private boolean placeLimit(
            int timestamp, String orderId, String side, int price, int quantity, Integer expiresAt) {
        expire(timestamp);
        if (orders.containsKey(orderId) || !validSide(side) || price <= 0 || quantity <= 0) {
            return false;
        }
        Order order = create(orderId, side, price, quantity);
        order.expiresAt = expiresAt;
        execute(order, price);
        if (order.remaining == 0) {
            order.state = "filled";
        } else {
            book.add(order);
        }
        triggerStops();
        return true;
    }

    public boolean placeOrder(int timestamp, String orderId, String side, int price, int quantity) {
        return placeLimit(timestamp, orderId, side, price, quantity, null);
    }

    public Integer cancelOrder(int timestamp, String orderId) {
        expire(timestamp);
        Order order = orders.get(orderId);
        if (order == null) {
            return null;
        }
        if ("open".equals(order.state)) {
            book.remove(order);
        } else if ("pending".equals(order.state)) {
            stops.remove(order);
        } else {
            return null;
        }
        order.state = "cancelled";
        return order.remaining;
    }

    public Integer bestPrice(int timestamp, String side) {
        expire(timestamp);
        boolean buy = "buy".equals(side);
        Integer best = null;
        for (Order order : book) {
            if (!validSide(side) || order.buy != buy) {
                continue;
            }
            if (best == null || (buy ? order.price > best : order.price < best)) {
                best = order.price;
            }
        }
        return best;
    }

    public int depth(int timestamp, String side, int price) {
        expire(timestamp);
        int total = 0;
        for (Order order : book) {
            if (validSide(side) && order.buy == "buy".equals(side) && order.price == price) {
                total += order.remaining;
            }
        }
        return total;
    }

    public String orderStatus(int timestamp, String orderId) {
        expire(timestamp);
        Order order = orders.get(orderId);
        if (order == null) {
            return null;
        }
        if ("open".equals(order.state)) {
            return "open(" + order.remaining + ")";
        }
        return order.state;
    }

    public List<String> lastTrades(int timestamp, int n) {
        expire(timestamp);
        List<String> out = new ArrayList<>();
        for (int i = trades.size() - 1; i >= 0 && out.size() < n; i--) {
            out.add(trades.get(i));
        }
        return out;
    }

    public List<String> topLevels(int timestamp, String side, int n) {
        expire(timestamp);
        List<String> out = new ArrayList<>();
        if (!validSide(side)) {
            return out;
        }
        boolean buy = "buy".equals(side);
        TreeMap<Integer, Integer> levels = new TreeMap<>();
        for (Order order : book) {
            if (order.buy == buy) {
                levels.merge(order.price, order.remaining, Integer::sum);
            }
        }
        Map<Integer, Integer> ordered = buy ? levels.descendingMap() : levels;
        for (Map.Entry<Integer, Integer> level : ordered.entrySet()) {
            if (out.size() >= n) {
                break;
            }
            out.add(level.getKey() + "(" + level.getValue() + ")");
        }
        return out;
    }

    public boolean placeOrderWithTtl(
            int timestamp, String orderId, String side, int price, int quantity, int ttl) {
        if (ttl <= 0) {
            return false;
        }
        return placeLimit(timestamp, orderId, side, price, quantity, timestamp + ttl);
    }

    public Integer placeMarketOrder(int timestamp, String orderId, String side, int quantity) {
        expire(timestamp);
        if (orders.containsKey(orderId) || !validSide(side) || quantity <= 0) {
            return null;
        }
        Order order = create(orderId, side, 0, quantity);
        int filled = execute(order, null);
        order.state = order.remaining == 0 ? "filled" : "cancelled";
        triggerStops();
        return filled;
    }

    public boolean amendOrder(int timestamp, String orderId, int newQuantity) {
        expire(timestamp);
        Order order = orders.get(orderId);
        if (order == null || !"open".equals(order.state)) {
            return false;
        }
        if (newQuantity <= 0 || newQuantity == order.remaining) {
            return false;
        }
        if (newQuantity > order.remaining) {
            order.priority = nextPriority;
            nextPriority += 1;
        }
        order.remaining = newQuantity;
        return true;
    }

    public boolean placeStopOrder(
            int timestamp, String orderId, String side, int stopPrice, int quantity) {
        expire(timestamp);
        if (orders.containsKey(orderId) || !validSide(side) || stopPrice <= 0 || quantity <= 0) {
            return false;
        }
        Order order = create(orderId, side, stopPrice, quantity);
        order.state = "pending";
        stops.add(order);
        triggerStops();
        return true;
    }
}
