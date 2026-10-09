# Order matching level 3

Orders can expire, and market orders trade at any price.

- `place_order_with_ttl(timestamp, order_id, side, price, quantity, ttl)`
  works like `place_order`, but the order is open only while the
  current timestamp is below `timestamp + ttl`. From `timestamp + ttl`
  on, whatever is left of it is expired: it never trades, no query
  counts it, `order_status` is `"expired"` and `cancel_order` returns
  null. `ttl <= 0` returns false. An order that was filled or cancelled
  before its expiry keeps that status.
- `place_market_order(timestamp, order_id, side, quantity)` matches
  like a limit order with no price limit: best price first, then
  longest waiting. It never rests. Returns the quantity traded, which
  may be 0. Its status is `"filled"` if all of it traded, otherwise
  `"cancelled"`. Returns null if `order_id` was accepted before, the
  side is unknown, or `quantity` is not positive. An accepted market
  order uses up its id even when it trades nothing.

Every call first expires the orders whose time has come, using its own
timestamp.

## Example

```
place_order_with_ttl(1, "s1", "sell", 100, 5, 10) -> true
place_order_with_ttl(2, "s2", "sell", 101, 5, 0) -> false
place_order(3, "s2", "sell", 101, 5) -> true
best_price(10, "sell") -> 100
best_price(11, "sell") -> 101
order_status(12, "s1") -> "expired"
cancel_order(13, "s1") -> null
place_order(14, "s3", "sell", 103, 2) -> true
place_market_order(15, "m1", "buy", 6) -> 6
last_trades(16, 2) -> ["m1:s3:103:1", "m1:s2:101:5"]
order_status(17, "m1") -> "filled"
place_market_order(18, "m2", "buy", 4) -> 1
order_status(19, "m2") -> "cancelled"
place_market_order(20, "m3", "sell", 2) -> 0
place_market_order(21, "m3", "sell", 2) -> null
place_market_order(22, "m4", "sell", 0) -> null
```

`s1` is open through timestamp 10 and expired from 11. `m2` wanted
four but only one unit was left, so it trades one and is cancelled.
`m3` trades nothing but still uses up its id.
