# Order book level 3

`place_gtt(timestamp, order_id, trader, side, price, qty, ttl)` is like
`place`, but any part left resting expires at `timestamp + ttl`. Null
also if `ttl` is not positive.

Before every call, remove each order whose expiry is at or before the
call's timestamp. An expired order acts as if it was cancelled.

`modify(timestamp, order_id, price, qty)` changes a resting order. `qty`
is the new remaining quantity. Returns the remaining quantity after the
change, or null if the order is not resting or `price` or `qty` is not
positive.

- Same price and a quantity no larger than before: the order keeps its place in line.
- Any other change sends the order to the back of the line, as if just placed. If the new price crosses, it matches right away.
- The expiry does not change.

## Example

```
place_gtt(10, "g1", "ann", "sell", 100, 5, 20) -> 5
get_order(29, "g1") -> "sell 5@100"
get_order(30, "g1") -> null
place(31, "b1", "bob", "buy", 100, 1) -> 1
trades(32, 5) -> []
```

```
place(1, "b1", "a", "buy", 100, 5) -> 5
place(2, "b2", "b", "buy", 100, 5) -> 5
modify(3, "b1", 100, 3) -> 3
place(4, "s1", "c", "sell", 100, 4) -> 0
trades(5, 5) -> ["b2/s1 1@100", "b1/s1 3@100"]
place(6, "b3", "d", "buy", 100, 5) -> 5
modify(7, "b2", 100, 6) -> 6
place(8, "s2", "e", "sell", 100, 5) -> 0
trades(9, 1) -> ["b3/s2 5@100"]
```

Shrinking b1 kept it first in line. Growing b2 sent it behind b3.

```
place(1, "b1", "a", "buy", 95, 4) -> 4
place(2, "s1", "b", "sell", 100, 3) -> 3
modify(3, "b1", 100, 4) -> 1
```

Raising b1 to 100 crosses s1, so 3 trade right away.
