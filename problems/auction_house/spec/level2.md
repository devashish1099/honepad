# Auction house level 2

- `bid_history(auction_id)` returns the accepted bids still standing,
  oldest first, as `"bidder:amount"`. Unknown is null.
- `retract_bid(timestamp, auction_id, bidder)` removes every bid the
  bidder has in an open auction. Returns true if any bid was removed.
  The highest remaining bid becomes the current highest, and later
  bids are compared with it.
- `active_auctions(timestamp)` returns the ids of open auctions,
  soonest `end_time` first, ties by id.

## Example

```
create_auction(0, "lamp", "sam", 20, 100) -> true
create_auction(0, "rug", "sam", 5, 60) -> true
bid(1, "lamp", "ann", 20) -> true
bid(2, "lamp", "bob", 30) -> true
bid(3, "lamp", "ann", 40) -> true
bid_history("lamp") -> ["ann:20", "bob:30", "ann:40"]
retract_bid(4, "lamp", "ann") -> true
highest_bid("lamp") -> "bob:30"
bid_history("lamp") -> ["bob:30"]
bid(5, "lamp", "cat", 30) -> false
bid(6, "lamp", "cat", 31) -> true
active_auctions(10) -> ["rug", "lamp"]
active_auctions(60) -> ["lamp"]
```
