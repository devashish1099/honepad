# Auction house level 3

- `set_reserve(timestamp, auction_id, seller, reserve)` sets a hidden
  minimum price. Returns true if set. False if the auction is unknown
  or ended, `seller` is not its seller, or `reserve <= 0`. It can be
  changed while the auction is open. After the end, `winner` returns
  `""` if the highest bid is below the reserve.
- `ends_at(auction_id)` returns the current end time. Unknown is null.

Late bids extend the auction: when a bid is accepted at `timestamp`
and `end_time - timestamp < 5`, the end time becomes `timestamp + 5`.
Rejected bids and retractions never extend it.

- `set_buy_now(timestamp, auction_id, seller, price)` offers an instant
  sale price. Returns true if set. False if the auction is unknown or
  ended, `seller` is not its seller, `price <= 0`, or `price` is not
  above the current highest bid. It can be changed while open.
- `buy_now(timestamp, auction_id, buyer)` buys at that price. Returns
  false if the auction is unknown or ended, has no buy-now price, the
  buyer is the seller, the highest bid has reached the price, or the
  price is below the reserve. Otherwise the purchase is recorded as an
  accepted bid of the buy-now price and the auction ends at once (its
  end time becomes `timestamp`). It never extends the auction.

## Example

```
create_auction(0, "lamp", "sam", 20, 100) -> true
set_reserve(1, "lamp", "bob", 80) -> false
set_reserve(1, "lamp", "sam", 80) -> true
bid(50, "lamp", "ann", 60) -> true
ends_at("lamp") -> 100
bid(97, "lamp", "bob", 70) -> true
ends_at("lamp") -> 102
bid(98, "lamp", "ann", 65) -> false
ends_at("lamp") -> 102
winner(101, "lamp") -> null
winner(102, "lamp") -> ""
create_auction(102, "rug", "sam", 10, 200) -> true
set_buy_now(103, "rug", "sam", 90) -> true
bid(104, "rug", "ann", 50) -> true
buy_now(105, "rug", "bob") -> true
ends_at("rug") -> 105
winner(105, "rug") -> "bob:90"
bid(106, "rug", "cat", 95) -> false
```
