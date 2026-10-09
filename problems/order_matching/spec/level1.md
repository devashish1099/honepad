# Order matching level 1

An exchange keeps limit orders for one instrument. A buy order offers
to buy `quantity` units at `price` or lower. A sell order offers to
sell at `price` or higher. An order that is waiting in the book is
open.

- `place_order(timestamp, order_id, side, price, quantity)` adds an
  open order. `side` is `"buy"` or `"sell"`. Returns true if accepted.
  Returns false if `order_id` was accepted before (even if that order
  is gone now), the side is unknown, or `price` or `quantity` is not
  positive. A rejected call does not use up its id.
- `cancel_order(timestamp, order_id)` removes an open order. Returns
  the quantity removed. Returns null if the order is unknown or not
  open.
- `best_price(timestamp, side)` returns the highest price among open
  buy orders, or the lowest price among open sell orders. Returns null
  if that side has no open order or the side is unknown.
- `depth(timestamp, side, price)` returns the total quantity of open
  orders on that side at exactly that price. Nothing there, or an
  unknown side, is 0.

Call timestamps never decrease. In this level no buy price reaches a
sell price, so orders never trade.

## Example

```
place_order(1, "b1", "buy", 99, 5) -> true
place_order(2, "b2", "buy", 97, 3) -> true
place_order(3, "s1", "sell", 101, 4) -> true
place_order(4, "s2", "sell", 101, 6) -> true
place_order(5, "b1", "buy", 98, 1) -> false
place_order(6, "x1", "hold", 98, 1) -> false
place_order(7, "x1", "buy", 0, 1) -> false
best_price(8, "buy") -> 99
best_price(9, "sell") -> 101
depth(10, "sell", 101) -> 10
depth(11, "buy", 101) -> 0
cancel_order(12, "b1") -> 5
cancel_order(13, "b1") -> null
best_price(14, "buy") -> 97
cancel_order(15, "nope") -> null
place_order(16, "b1", "buy", 98, 1) -> false
place_order(17, "x1", "buy", 98, 1) -> true
```

`x1` was rejected twice, so the id is still free at timestamp 17.
`b1` was accepted once, so it can never be reused.
