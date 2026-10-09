import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Order {
    final String id;
    final String trader;
    final boolean buy;
    int price;
    int qty;
    long seq;
    final Integer expiresAt;

    Order(String id, String trader, boolean buy, int price, int qty, long seq, Integer expiresAt) {
        this.id = id;
        this.trader = trader;
        this.buy = buy;
        this.price = price;
        this.qty = qty;
        this.seq = seq;
        this.expiresAt = expiresAt;
    }

    boolean expiredAt(int t) {
        return expiresAt != null && t >= expiresAt;
    }
}

class Trade {
    final int time;
    final String buyId;
    final String sellId;
    final int qty;
    final int price;

    Trade(int time, String buyId, String sellId, int qty, int price) {
        this.time = time;
        this.buyId = buyId;
        this.sellId = sellId;
        this.qty = qty;
        this.price = price;
    }
}

/** A frozen copy of the resting book after one call. */
class Snapshot {
    final int time;
    final List<Order> orders;

    Snapshot(int time, List<Order> orders) {
        this.time = time;
        this.orders = orders;
    }
}

public class Simulation {
    private final Map<String, Order> book = new LinkedHashMap<>();
    private final Set<String> usedIds = new HashSet<>();
    private final List<Trade> tradeLog = new ArrayList<>();
    private final Map<String, long[]> positions = new HashMap<>();
    private final List<Snapshot> snapshots = new ArrayList<>();
    private long seq = 0;

    public Simulation() {}

    public Integer place(int timestamp, String orderId, String trader, String side, int price, int qty) {
        return submit(timestamp, orderId, trader, side, price, qty, null);
    }

    public Integer cancel(int timestamp, String orderId) {
        expire(timestamp);
        Order o = book.remove(orderId);
        snapshot(timestamp);
        return o == null ? null : o.qty;
    }

    public String getOrder(int timestamp, String orderId) {
        expire(timestamp);
        snapshot(timestamp);
        Order o = book.get(orderId);
        if (o == null) {
            return null;
        }
        return (o.buy ? "buy " : "sell ") + o.qty + "@" + o.price;
    }

    public List<String> trades(int timestamp, int n) {
        expire(timestamp);
        snapshot(timestamp);
        List<String> out = new ArrayList<>();
        for (int i = tradeLog.size() - 1; i >= 0 && out.size() < n; i--) {
            Trade t = tradeLog.get(i);
            out.add(t.buyId + "/" + t.sellId + " " + t.qty + "@" + t.price);
        }
        return out;
    }

    public String best(int timestamp, String side) {
        expire(timestamp);
        snapshot(timestamp);
        return bestLevel(book.values(), side.equals("buy"), null);
    }

    public Integer placeGtt(
            int timestamp, String orderId, String trader, String side, int price, int qty, int ttl) {
        if (ttl <= 0) {
            expire(timestamp);
            snapshot(timestamp);
            return null;
        }
        return submit(timestamp, orderId, trader, side, price, qty, timestamp + ttl);
    }

    public Integer modify(int timestamp, String orderId, int price, int qty) {
        expire(timestamp);
        Order o = book.get(orderId);
        if (o == null || price <= 0 || qty <= 0) {
            snapshot(timestamp);
            return null;
        }
        if (price == o.price && qty <= o.qty) {
            o.qty = qty;
            snapshot(timestamp);
            return qty;
        }
        o.price = price;
        o.qty = qty;
        o.seq = ++seq;
        int left = match(timestamp, o);
        snapshot(timestamp);
        return left;
    }

    public String position(int timestamp, String trader) {
        expire(timestamp);
        snapshot(timestamp);
        long[] p = positions.get(trader);
        return p == null ? null : p[0] + " " + p[1];
    }

    public Integer vwap(int timestamp, int from, int to) {
        expire(timestamp);
        snapshot(timestamp);
        long volume = 0;
        long notional = 0;
        for (Trade t : tradeLog) {
            if (from <= t.time && t.time < to) {
                volume += t.qty;
                notional += (long) t.qty * t.price;
            }
        }
        return volume == 0 ? null : (int) (notional / volume);
    }

    public String bestAt(int timestamp, String side, int timeAt) {
        expire(timestamp);
        snapshot(timestamp);
        Snapshot chosen = null;
        for (Snapshot s : snapshots) {
            if (s.time <= timeAt) {
                chosen = s;
            }
        }
        return chosen == null ? null : bestLevel(chosen.orders, side.equals("buy"), timeAt);
    }

    private Integer submit(
            int timestamp,
            String orderId,
            String trader,
            String side,
            int price,
            int qty,
            Integer expiresAt) {
        expire(timestamp);
        boolean known = side.equals("buy") || side.equals("sell");
        if (usedIds.contains(orderId) || !known || price <= 0 || qty <= 0) {
            snapshot(timestamp);
            return null;
        }
        usedIds.add(orderId);
        positions.putIfAbsent(trader, new long[2]);
        Order o = new Order(orderId, trader, side.equals("buy"), price, qty, ++seq, expiresAt);
        book.put(orderId, o);
        int left = match(timestamp, o);
        snapshot(timestamp);
        return left;
    }

    /** Trade o against the other side. Returns o's remaining quantity. */
    private int match(int timestamp, Order o) {
        while (o.qty > 0) {
            Order best = null;
            for (Order r : book.values()) {
                if (r.buy == o.buy) {
                    continue;
                }
                boolean crosses = o.buy ? r.price <= o.price : r.price >= o.price;
                if (!crosses) {
                    continue;
                }
                if (best == null || better(r, best)) {
                    best = r;
                }
            }
            if (best == null) {
                break;
            }
            int qty = Math.min(o.qty, best.qty);
            o.qty -= qty;
            best.qty -= qty;
            Order buyer = o.buy ? o : best;
            Order seller = o.buy ? best : o;
            tradeLog.add(new Trade(timestamp, buyer.id, seller.id, qty, best.price));
            long[] bp = positions.get(buyer.trader);
            bp[0] += qty;
            bp[1] -= (long) qty * best.price;
            long[] sp = positions.get(seller.trader);
            sp[0] -= qty;
            sp[1] += (long) qty * best.price;
            if (best.qty == 0) {
                book.remove(best.id);
            }
        }
        if (o.qty == 0) {
            book.remove(o.id);
        }
        return o.qty;
    }

    /** Price priority for the resting side, then time priority. */
    private static boolean better(Order a, Order b) {
        if (a.price != b.price) {
            return a.buy ? a.price > b.price : a.price < b.price;
        }
        return a.seq < b.seq;
    }

    private void expire(int timestamp) {
        book.values().removeIf(o -> o.expiredAt(timestamp));
    }

    private void snapshot(int timestamp) {
        List<Order> copy = new ArrayList<>();
        for (Order o : book.values()) {
            copy.add(new Order(o.id, o.trader, o.buy, o.price, o.qty, o.seq, o.expiresAt));
        }
        if (!snapshots.isEmpty() && snapshots.get(snapshots.size() - 1).time == timestamp) {
            snapshots.remove(snapshots.size() - 1);
        }
        snapshots.add(new Snapshot(timestamp, copy));
    }

    private static String bestLevel(Iterable<Order> orders, boolean buy, Integer timeAt) {
        Integer top = null;
        for (Order o : orders) {
            if (o.buy != buy || (timeAt != null && o.expiredAt(timeAt))) {
                continue;
            }
            if (top == null || (buy ? o.price > top : o.price < top)) {
                top = o.price;
            }
        }
        if (top == null) {
            return null;
        }
        int total = 0;
        for (Order o : orders) {
            if (o.buy == buy && o.price == top && (timeAt == null || !o.expiredAt(timeAt))) {
                total += o.qty;
            }
        }
        return top + "(" + total + ")";
    }
}
