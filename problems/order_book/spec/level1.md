# Order book level 1

Limit orders on one stock. In this level orders only rest in the book.
Level 2 adds matching, and the level 1 tests never cross.

- `place(timestamp, order_id, trader, side, price, qty)` adds an order. `side` is `"buy"` or `"sell"`. Returns the quantity resting in the book. Null if `order_id` was ever used before (even by a cancelled order), the side is unknown, or `price` or `qty` is not positive.
- `cancel(timestamp, order_id)` removes a resting order and returns its remaining quantity. Null if it is not resting.
- `get_order(timestamp, order_id)` returns `"side qty@price"`, such as `"buy 5@100"`. Null if it is not resting.

## Example

```
place(1, "o1", "alice", "buy", 100, 5) -> 5
place(2, "o2", "bob", "sell", 105, 3) -> 3
place(3, "o1", "bob", "buy", 99, 1) -> null
place(4, "o3", "bob", "hold", 100, 1) -> null
get_order(6, "o1") -> "buy 5@100"
cancel(7, "o1") -> 5
get_order(8, "o1") -> null
cancel(9, "o1") -> null
place(10, "o1", "alice", "buy", 100, 5) -> null
```

Once o1 is used, the id cannot come back.
