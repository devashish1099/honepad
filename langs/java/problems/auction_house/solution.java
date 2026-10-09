import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

class Bid {
    String bidder;
    int amount;
}

class Auction {
    String id;
    String seller;
    int startPrice;
    int endTime;
    int reserve = 0;
    Integer buyNow = null;
    boolean settled = false;
    List<Bid> bids = new ArrayList<>();

    Bid top() {
        return bids.isEmpty() ? null : bids.get(bids.size() - 1);
    }
}

public class Simulation {
    private final Map<String, Auction> auctions = new LinkedHashMap<>();
    private final Map<String, Integer> budgets = new HashMap<>();
    private final Map<String, Integer> earned = new HashMap<>();

    public Simulation() {}

    private boolean open(Auction a, int timestamp) {
        return timestamp < a.endTime;
    }

    private int committed(String user, String except) {
        int total = 0;
        for (Auction a : auctions.values()) {
            Bid top = a.top();
            if (!a.settled && !a.id.equals(except) && top != null && top.bidder.equals(user)) {
                total += top.amount;
            }
        }
        return total;
    }

    public boolean createAuction(int timestamp, String auctionId, String seller, int startPrice, int endTime) {
        if (auctions.containsKey(auctionId) || startPrice <= 0 || endTime <= timestamp) {
            return false;
        }
        Auction a = new Auction();
        a.id = auctionId;
        a.seller = seller;
        a.startPrice = startPrice;
        a.endTime = endTime;
        auctions.put(auctionId, a);
        return true;
    }

    public boolean bid(int timestamp, String auctionId, String bidder, int amount) {
        Auction a = auctions.get(auctionId);
        if (a == null || !open(a, timestamp) || a.seller.equals(bidder)) {
            return false;
        }
        Bid top = a.top();
        if (top == null ? amount < a.startPrice : amount <= top.amount) {
            return false;
        }
        Integer budget = budgets.get(bidder);
        if (budget != null && amount + committed(bidder, auctionId) > budget) {
            return false;
        }
        Bid b = new Bid();
        b.bidder = bidder;
        b.amount = amount;
        a.bids.add(b);
        if (a.endTime - timestamp < 5) {
            a.endTime = timestamp + 5;
        }
        return true;
    }

    public String highestBid(String auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null || a.top() == null) {
            return null;
        }
        return a.top().bidder + ":" + a.top().amount;
    }

    public String winner(int timestamp, String auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null || open(a, timestamp)) {
            return null;
        }
        Bid top = a.top();
        if (top == null || top.amount < a.reserve) {
            return "";
        }
        return top.bidder + ":" + top.amount;
    }

    public List<String> bidHistory(String auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null) {
            return null;
        }
        List<String> out = new ArrayList<>();
        for (Bid b : a.bids) {
            out.add(b.bidder + ":" + b.amount);
        }
        return out;
    }

    public boolean retractBid(int timestamp, String auctionId, String bidder) {
        Auction a = auctions.get(auctionId);
        if (a == null || !open(a, timestamp)) {
            return false;
        }
        return a.bids.removeIf(b -> b.bidder.equals(bidder));
    }

    public List<String> activeAuctions(int timestamp) {
        List<Auction> live = new ArrayList<>();
        for (Auction a : auctions.values()) {
            if (open(a, timestamp)) {
                live.add(a);
            }
        }
        live.sort((x, y) -> x.endTime != y.endTime ? Integer.compare(x.endTime, y.endTime) : x.id.compareTo(y.id));
        List<String> out = new ArrayList<>();
        for (Auction a : live) {
            out.add(a.id);
        }
        return out;
    }

    public boolean setReserve(int timestamp, String auctionId, String seller, int reserve) {
        Auction a = auctions.get(auctionId);
        if (a == null || !a.seller.equals(seller) || !open(a, timestamp) || reserve <= 0) {
            return false;
        }
        a.reserve = reserve;
        return true;
    }

    public Integer endsAt(String auctionId) {
        Auction a = auctions.get(auctionId);
        return a == null ? null : a.endTime;
    }

    public boolean setBuyNow(int timestamp, String auctionId, String seller, int price) {
        Auction a = auctions.get(auctionId);
        if (a == null || !a.seller.equals(seller) || !open(a, timestamp) || price <= 0) {
            return false;
        }
        if (a.top() != null && price <= a.top().amount) {
            return false;
        }
        a.buyNow = price;
        return true;
    }

    public boolean buyNow(int timestamp, String auctionId, String buyer) {
        Auction a = auctions.get(auctionId);
        if (a == null || !open(a, timestamp) || a.buyNow == null || a.seller.equals(buyer)) {
            return false;
        }
        int price = a.buyNow;
        if ((a.top() != null && a.top().amount >= price) || price < a.reserve) {
            return false;
        }
        Integer budget = budgets.get(buyer);
        if (budget != null && price + committed(buyer, auctionId) > budget) {
            return false;
        }
        Bid b = new Bid();
        b.bidder = buyer;
        b.amount = price;
        a.bids.add(b);
        a.endTime = timestamp;
        return true;
    }

    public boolean setBudget(String userId, int budget) {
        if (budget < 0) {
            return false;
        }
        budgets.put(userId, budget);
        return true;
    }

    public String settle(int timestamp, String auctionId) {
        Auction a = auctions.get(auctionId);
        if (a == null || open(a, timestamp) || a.settled) {
            return null;
        }
        String result = winner(timestamp, auctionId);
        a.settled = true;
        if (!result.isEmpty()) {
            Bid top = a.top();
            earned.merge(a.seller, top.amount, Integer::sum);
            if (budgets.containsKey(top.bidder)) {
                budgets.put(top.bidder, budgets.get(top.bidder) - top.amount);
            }
        }
        return result;
    }

    public int earnings(String userId) {
        return earned.getOrDefault(userId, 0);
    }
}
