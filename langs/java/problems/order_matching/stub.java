import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Place a limit order. {@code side} is {@code "buy"} or {@code "sell"}.
     * Returns true if accepted, false if the id was used before, the side
     * is unknown, or price or quantity is not positive.
     */
    public boolean placeOrder(int timestamp, String orderId, String side, int price, int quantity) {
        return false;
    }

    /**
     * Cancel an order that is still waiting. Returns the quantity
     * removed, or null if the order is unknown or no longer waiting.
     */
    public Integer cancelOrder(int timestamp, String orderId) {
        return null;
    }

    /**
     * Highest open buy price or lowest open sell price. Null if that
     * side is empty or the side is unknown.
     */
    public Integer bestPrice(int timestamp, String side) {
        return null;
    }

    /**
     * Total open quantity on one side at one price. 0 if none.
     */
    public int depth(int timestamp, String side, int price) {
        return 0;
    }

    /**
     * {@code "open(remaining)"}, {@code "filled"}, {@code "cancelled"},
     * {@code "expired"}, {@code "pending"}, or null if unknown.
     */
    public String orderStatus(int timestamp, String orderId) {
        return null;
    }

    /**
     * The most recent {@code n} trades, newest first, each as
     * {@code "buyId:sellId:price:quantity"}.
     */
    public List<String> lastTrades(int timestamp, int n) {
        return null;
    }

    /**
     * The best {@code n} price levels of one side, best first, each as
     * {@code "price(quantity)"}.
     */
    public List<String> topLevels(int timestamp, String side, int n) {
        return null;
    }

    /**
     * Place a limit order that expires at {@code timestamp + ttl}.
     * False as for placeOrder, or if ttl is not positive.
     */
    public boolean placeOrderWithTtl(
            int timestamp, String orderId, String side, int price, int quantity, int ttl) {
        return false;
    }

    /**
     * Trade at any price right now. Returns the quantity filled, or null
     * if the id was used before, the side is unknown, or quantity is not
     * positive. The unfilled rest is dropped.
     */
    public Integer placeMarketOrder(int timestamp, String orderId, String side, int quantity) {
        return null;
    }

    /**
     * Change the remaining quantity of an open limit order. Returns true
     * if changed. Growing an order sends it to the back of its price.
     */
    public boolean amendOrder(int timestamp, String orderId, int newQuantity) {
        return false;
    }

    /**
     * Place a stop order that turns into a market order once the last
     * trade price reaches {@code stopPrice}. False as for placeOrder.
     */
    public boolean placeStopOrder(
            int timestamp, String orderId, String side, int stopPrice, int quantity) {
        return false;
    }
}
