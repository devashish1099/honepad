# Order book level 4

`position(timestamp, trader)` returns `"qty cash"`. `qty` is shares
bought minus shares sold. `cash` is money received minus money paid.
Null if the trader never placed an accepted order.

`vwap(timestamp, from, to)` covers the trades whose timestamp is in
`[from, to)`. It returns `sum(price * qty) / sum(qty)` using integer
division, or null if there are none.

`best_at(timestamp, side, time_at)` is `best` as of `time_at`. Use the
book as it stood after the last call at or before `time_at`. Then drop
any order whose expiry is at or before `time_at`, even if no call
happened at that moment. Null if no call had happened yet, or that side
was empty.

## Example

```
place(1, "s1", "bob", "sell", 100, 3) -> 3
place(2, "b1", "alice", "buy", 100, 3) -> 0
position(3, "alice") -> "3 -300"
position(3, "bob") -> "-3 300"
position(3, "zed") -> null
```

```
place(1, "s1", "a", "sell", 100, 2) -> 2
place(5, "b1", "b", "buy", 100, 2) -> 0
place(6, "s2", "a", "sell", 110, 3) -> 3
place(7, "b2", "b", "buy", 110, 3) -> 0
vwap(8, 0, 100) -> 106
vwap(8, 5, 7) -> 100
vwap(8, 8, 100) -> null
```

(2 * 100 + 3 * 110) / 5 is 530 / 5, which is 106.

```
place(1, "s1", "a", "sell", 100, 2) -> 2
place(3, "s2", "a", "sell", 99, 1) -> 1
place(5, "b1", "b", "buy", 99, 1) -> 0
best_at(10, "sell", 2) -> "100(2)"
best_at(10, "sell", 3) -> "99(1)"
best_at(10, "sell", 5) -> "100(2)"
best_at(10, "sell", 0) -> null
place_gtt(20, "g1", "c", "sell", 95, 1, 10) -> 1
best_at(40, "sell", 25) -> "95(1)"
best_at(40, "sell", 30) -> "100(2)"
```

No call happened at 30, but g1 expired then.
