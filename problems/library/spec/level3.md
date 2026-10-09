# Library level 3

Loans are due 14 days after they start. A day is `86400`, so the due
time is `start + 1209600`.

A loan is late once the time passes the due time. Each started late
day costs 10. At exactly the due time the fine is 0. One second later
it is 10. One day plus one second later it is 20.

- An open loan keeps adding fine as time moves on.
- `return_book` freezes that loan's fine at the return time.

`get_fine(timestamp, member_id)` returns frozen fines plus the fines
on open loans at `timestamp`, minus payments. A member is known after
their first successful loan. An unknown member is null.

`pay_fine(timestamp, member_id, amount)` pays toward the fine and
returns what is still owed. Null if the member is unknown, `amount` is
not positive, or `amount` is more than `get_fine` would return now.

`borrow` now returns null if the member owes any fine.

## Example

```
add_book(1, "b1", 1) -> true
borrow(1, "m1", "b1") -> 0
get_fine(1209601, "m1") -> 0
get_fine(1209602, "m1") -> 10
get_fine(1296001, "m1") -> 10
get_fine(1296002, "m1") -> 20
return_book(1296002, "m1", "b1") -> 1
get_fine(6048000, "m1") -> 20
```

Due time is 1209601. After the return, the fine stays 20 forever.

```
borrow(3, "m1", "b1") -> 0
return_book(1209604, "m1", "b1") -> 1
get_fine(1209605, "m1") -> 10
borrow(1209606, "m1", "b2") -> null
pay_fine(1209607, "m1", 25) -> null
pay_fine(1209609, "m1", 4) -> 6
borrow(1209610, "m1", "b2") -> null
pay_fine(1209611, "m1", 6) -> 0
borrow(1209612, "m1", "b2") -> 0
```

Paying more than is owed is null. A partial payment still blocks
borrowing.

```
borrow(1, "m1", "b1") -> 0
borrow(86401, "m1", "b2") -> 0
get_fine(1468801, "m1") -> 50
```

Two open loans add up. b1 is 3 days late (30), b2 is 2 days late (20).
