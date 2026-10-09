# Auction house level 1

Sellers run timed auctions.

- `create_auction(timestamp, auction_id, seller, start_price, end_time)`
  opens an auction. Returns true if created. False if the id exists,
  `start_price <= 0`, or `end_time <= timestamp`.
- `bid(timestamp, auction_id, bidder, amount)` returns true if the bid
  is accepted. It is rejected if the auction is unknown or has ended,
  the bidder is the seller, or the amount is too low: the first bid
  must be at least `start_price`, every later bid must be higher than
  the current highest bid.
- `highest_bid(auction_id)` returns `"bidder:amount"` for the highest
  bid, or null if there is none or the auction is unknown.
- `winner(timestamp, auction_id)` returns null if the auction is
  unknown or still open. Once ended it returns `"bidder:amount"` for
  the highest bid, or `""` if nobody bid.

An auction is open while `timestamp < end_time` and has ended from
`end_time` on. Call timestamps never decrease.

## Example

```
create_auction(0, "lamp", "sam", 20, 100) -> true
create_auction(1, "lamp", "kim", 5, 100) -> false
create_auction(1, "vase", "kim", 5, 1) -> false
bid(2, "lamp", "ann", 15) -> false
bid(3, "lamp", "ann", 20) -> true
bid(4, "lamp", "bob", 20) -> false
bid(5, "lamp", "sam", 50) -> false
bid(6, "lamp", "bob", 35) -> true
highest_bid("lamp") -> "bob:35"
winner(50, "lamp") -> null
bid(100, "lamp", "ann", 90) -> false
winner(100, "lamp") -> "bob:35"
```
