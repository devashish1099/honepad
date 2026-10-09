import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Place a limit order. side is buy or sell. Returns the resting
     * quantity, or null if the id was ever used or the input is invalid.
     */
    public Integer place(int timestamp, String orderId, String trader, String side, int price, int qty) {
        return null;
    }

    /** Remove a resting order. Returns its remaining quantity, or null. */
    public Integer cancel(int timestamp, String orderId) {
        return null;
    }

    /** {@code "side qty@price"}, such as {@code "buy 5@100"}, or null. */
    public String getOrder(int timestamp, String orderId) {
        return null;
    }

    /** Last n trades, newest first, as {@code buyId/sellId qty@price}. */
    public List<String> trades(int timestamp, int n) {
        return null;
    }

    /** Best price on a side as {@code price(totalQty)}, or null. */
    public String best(int timestamp, String side) {
        return null;
    }

    /** Like place, but the resting part expires at {@code timestamp + ttl}. */
    public Integer placeGtt(
            int timestamp, String orderId, String trader, String side, int price, int qty, int ttl) {
        return null;
    }

    /**
     * Change price and remaining quantity. Same price and no larger quantity
     * keeps priority. Returns the remaining quantity, or null.
     */
    public Integer modify(int timestamp, String orderId, int price, int qty) {
        return null;
    }

    /** {@code "qty cash"} for a trader, or null if unknown. */
    public String position(int timestamp, String trader) {
        return null;
    }

    /** Integer VWAP of trades in {@code [from, to)}, or null. */
    public Integer vwap(int timestamp, int from, int to) {
        return null;
    }

    /** {@code best} as the book stood at {@code timeAt}. */
    public String bestAt(int timestamp, String side, int timeAt) {
        return null;
    }
}
