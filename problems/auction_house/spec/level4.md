# Auction house level 4

- `set_budget(user_id, budget)` limits what a user may have at stake.
  Returns false if `budget < 0`. Users without a budget have no
  limit.
- `settle(timestamp, auction_id)` closes an ended auction once.
  Returns what `winner` returns. Returns null if the auction is
  unknown, still open, or already settled. A sale (a non-empty result)
  adds the amount to the seller's earnings and, if the winner has a
  budget, subtracts the amount from it.
- `earnings(user_id)` returns the total of the user's settled sales.

A user is at stake in every auction that is not settled (open or
ended) where they hold the highest bid, for that bid's amount. A bid
by a user with a budget is rejected if its amount plus their stake in
all other auctions is more than the budget.

## Example

```
create_auction(0, "lamp", "sam", 10, 50) -> true
create_auction(0, "rug", "sam", 10, 80) -> true
set_budget("ann", 100) -> true
bid(1, "lamp", "ann", 60) -> true
bid(2, "rug", "ann", 50) -> false
bid(3, "rug", "ann", 40) -> true
bid(4, "lamp", "bob", 70) -> true
bid(5, "rug", "ann", 90) -> true
settle(49, "lamp") -> null
settle(50, "lamp") -> "bob:70"
settle(51, "lamp") -> null
earnings("sam") -> 70
bid(60, "rug", "bob", 95) -> true
settle(80, "rug") -> "bob:95"
earnings("sam") -> 165
```
