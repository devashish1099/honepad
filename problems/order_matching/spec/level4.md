# Order matching level 4

Open orders can be resized, and stop orders wait for a price.

- `amend_order(timestamp, order_id, new_quantity)` sets the remaining
  quantity of an open limit order. Returns true if changed. Returns
  false if the order is unknown or not open, or `new_quantity` is not
  positive or equals the current remaining quantity. Making an order
  smaller keeps its place in line. Making it larger sends it to the
  back of the line at its price, as if it had just been placed. Its
  expiry does not change.
- `place_stop_order(timestamp, order_id, side, stop_price, quantity)`
  adds a pending stop order. Returns true if accepted, false under the
  same rules as `place_order` (with `stop_price` as the price). A
  pending stop is not in the book: `best_price`, `depth` and
  `top_levels` ignore it, it cannot be amended, and it never expires.
  Its status is `"pending"`. `cancel_order` on a pending stop returns
  its quantity.

A buy stop triggers when the last trade price is at or above its
`stop_price`. A sell stop triggers when the last trade price is at or
below its `stop_price`. Before any trade there is no last price and
nothing triggers.

After every accepted `place_order`, `place_order_with_ttl`,
`place_market_order` and `place_stop_order`, once that order has
finished matching:

1. Find the pending stops that trigger at the current last trade
   price. If there are none, stop.
2. Take the one that was placed first. Run it as a market order under
   its own id. It ends `"filled"` or `"cancelled"`.
3. Go back to step 1 with the new last trade price.

## Example

```
place_order(1, "s1", "sell", 100, 4) -> true
place_order(2, "s2", "sell", 100, 4) -> true
amend_order(3, "s1", 2) -> true
amend_order(4, "s1", 2) -> false
amend_order(5, "s1", 6) -> true
amend_order(6, "s1", 0) -> false
place_order(7, "b1", "buy", 100, 5) -> true
last_trades(8, 2) -> ["b1:s1:100:1", "b1:s2:100:4"]
order_status(9, "s1") -> "open(5)"
place_order(10, "s3", "sell", 102, 3) -> true
place_stop_order(11, "st1", "buy", 102, 2) -> true
order_status(12, "st1") -> "pending"
amend_order(13, "st1", 5) -> false
place_order(14, "b2", "buy", 102, 6) -> true
last_trades(15, 1) -> ["st1:s3:102:2"]
order_status(16, "st1") -> "filled"
place_stop_order(17, "st2", "sell", 105, 1) -> true
order_status(18, "st2") -> "cancelled"
place_stop_order(19, "st3", "sell", 90, 3) -> true
cancel_order(20, "st3") -> 3
order_status(21, "st3") -> "cancelled"
```

Growing `s1` to 6 put it behind `s2`, so `b1` takes `s2` first. `b2`
trades at 100 and then at 102; the last price 102 triggers `st1`,
which buys the rest of `s3`. `st2` triggers the moment it is placed
(102 is at or below 105) but there are no open buys, so it trades
nothing and is cancelled.
