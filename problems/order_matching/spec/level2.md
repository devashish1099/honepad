# Order matching level 2

Orders now trade. When `place_order` accepts an order, it is matched
against the open orders of the other side before it rests:

- A buy matches open sells priced at or below its price. A sell
  matches open buys priced at or above its price.
- The best price goes first: the lowest sell for an incoming buy, the
  highest buy for an incoming sell. At the same price, the order that
  has waited longest goes first.
- Each match is a trade for the smaller of the two remaining
  quantities, at the price of the order that was already in the book.
- Matching repeats until the incoming order is fully traded or nothing
  matches. What is left of it becomes an open order.

An order whose quantity is fully traded is filled and leaves the book.
`cancel_order` returns the quantity still remaining. `best_price` and
`depth` count remaining quantity only.

- `order_status(timestamp, order_id)` returns `"open(R)"` where R is
  the remaining quantity, `"filled"`, or `"cancelled"`. Unknown is
  null.
- `last_trades(timestamp, n)` returns the most recent `n` trades,
  newest first. A trade is `"buy_id:sell_id:price:quantity"`. Fewer
  trades than `n` returns them all. `n <= 0` is an empty list.
- `top_levels(timestamp, side, n)` returns the best `n` prices of one
  side, best first, each as `"price(total)"` where total is the
  remaining quantity of every open order at that price. Unknown side
  or `n <= 0` is an empty list.

## Example

```
place_order(1, "s1", "sell", 101, 4) -> true
place_order(2, "s2", "sell", 100, 3) -> true
place_order(3, "s3", "sell", 100, 2) -> true
place_order(4, "b1", "buy", 101, 6) -> true
last_trades(5, 2) -> ["b1:s1:101:1", "b1:s3:100:2"]
order_status(6, "b1") -> "filled"
order_status(7, "s1") -> "open(3)"
order_status(8, "s2") -> "filled"
place_order(9, "b2", "buy", 99, 5) -> true
place_order(10, "b3", "buy", 98, 2) -> true
top_levels(11, "buy", 5) -> ["99(5)", "98(2)"]
top_levels(12, "sell", 1) -> ["101(3)"]
place_order(13, "s4", "sell", 98, 6) -> true
last_trades(14, 1) -> ["b3:s4:98:1"]
order_status(15, "b3") -> "open(1)"
cancel_order(16, "b3") -> 1
order_status(17, "b3") -> "cancelled"
order_status(18, "zz") -> null
last_trades(19, 0) -> []
```

`b1` takes `s2` first (price 100, placed earlier), then `s3`, then one
unit of `s1` at 101. `s4` sells five to `b2` at 99 and one to `b3` at
98: the trade price is always the resting order's price.
