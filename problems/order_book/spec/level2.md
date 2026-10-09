# Order book level 2

Matching. A new order trades against the other side before it rests.

- A buy at `p` matches sells priced `<= p`, cheapest first. A sell at `p` matches buys priced `>= p`, highest first.
- At the same price, the order that has waited longest goes first.
- Each trade is at the resting order's price, for the smaller of the two quantities.
- The new order keeps matching until it is filled or nothing crosses. Any remainder rests.
- `place` returns that remaining quantity, 0 if fully filled.

`trades(timestamp, n)` returns the last `n` trades, newest first, as
`buyId/sellId qty@price`.

`best(timestamp, side)` returns the best resting price on that side as
`price(totalQty)`, where `totalQty` adds up every order at that price.
Highest price for buys, lowest for sells. Null if that side is empty.

## Example

```
place(1, "s1", "ann", "sell", 101, 3) -> 3
place(2, "s2", "bob", "sell", 100, 2) -> 2
place(3, "s3", "cid", "sell", 100, 4) -> 4
place(4, "b1", "dan", "buy", 101, 7) -> 0
trades(5, 5) -> ["b1/s1 1@101", "b1/s3 4@100", "b1/s2 2@100"]
get_order(6, "s1") -> "sell 2@101"
best(7, "sell") -> "101(2)"
best(7, "buy") -> null
```

b1 takes s2 and s3 at 100 first, oldest first, then 1 of s1 at 101.

```
place(1, "s1", "ann", "sell", 101, 2) -> 2
place(2, "b1", "bob", "buy", 102, 5) -> 3
place(4, "b2", "cid", "buy", 102, 1) -> 1
best(5, "buy") -> "102(4)"
place(6, "s2", "dan", "sell", 90, 4) -> 0
trades(7, 10) -> ["b2/s2 1@102", "b1/s2 3@102", "b1/s1 2@101"]
```

s2 asked 90 but trades at the resting price of 102.
