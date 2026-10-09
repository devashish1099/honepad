import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Open an auction until {@code endTime}. Returns true if created.
     */
    public boolean createAuction(int timestamp, String auctionId, String seller, int startPrice, int endTime) {
        return false;
    }

    /**
     * Place a bid. Returns true if accepted.
     */
    public boolean bid(int timestamp, String auctionId, String bidder, int amount) {
        return false;
    }

    /**
     * {@code "bidder:amount"} of the highest bid, or null.
     */
    public String highestBid(String auctionId) {
        return null;
    }

    /**
     * After the end: {@code "bidder:amount"} or {@code ""}. Null while
     * open or unknown.
     */
    public String winner(int timestamp, String auctionId) {
        return null;
    }

    /**
     * Accepted bids, oldest first, as {@code "bidder:amount"}, or null.
     */
    public List<String> bidHistory(String auctionId) {
        return null;
    }

    /**
     * Withdraw all of a bidder's bids from an open auction. Returns true
     * if any were removed.
     */
    public boolean retractBid(int timestamp, String auctionId, String bidder) {
        return false;
    }

    /**
     * Open auctions, soonest end first, then by id.
     */
    public List<String> activeAuctions(int timestamp) {
        return null;
    }

    /**
     * Set a minimum sale price. Returns true if set.
     */
    public boolean setReserve(int timestamp, String auctionId, String seller, int reserve) {
        return false;
    }

    /**
     * Current end time, or null.
     */
    public Integer endsAt(String auctionId) {
        return null;
    }

    /**
     * Offer an instant-sale price. Returns true if set.
     */
    public boolean setBuyNow(int timestamp, String auctionId, String seller, int price) {
        return false;
    }

    /**
     * Buy at the instant-sale price, ending the auction. Returns true if
     * bought.
     */
    public boolean buyNow(int timestamp, String auctionId, String buyer) {
        return false;
    }

    /**
     * Limit how much a user may have at stake. Returns true if valid.
     */
    public boolean setBudget(String userId, int budget) {
        return false;
    }

    /**
     * Close a finished auction once. Returns what winner returns, or
     * null.
     */
    public String settle(int timestamp, String auctionId) {
        return null;
    }

    /**
     * Total a seller received from settled sales.
     */
    public int earnings(String userId) {
        return 0;
    }
}
