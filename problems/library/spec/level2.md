# Library level 2

`top_books(timestamp, n)` returns at most `n` strings `bookId(count)`.

`count` is every successful loan of that book, ever. Returns do not
lower it. The same member borrowing twice counts twice.

Sort by count, high to low, then id A to Z. A book that was never
borrowed still appears as `id(0)` if `n` is large enough.

## Example

```
add_book(1, "b1", 3) -> true
add_book(2, "b2", 3) -> true
add_book(3, "b3", 3) -> true
borrow(4, "m1", "b2") -> 2
borrow(5, "m2", "b2") -> 1
borrow(6, "m1", "b1") -> 2
top_books(7, 2) -> ["b2(2)", "b1(1)"]
top_books(8, 5) -> ["b2(2)", "b1(1)", "b3(0)"]
top_books(9, 0) -> []
```

```
borrow(3, "m1", "zeta") -> 0
return_book(4, "m1", "zeta") -> 1
borrow(5, "m1", "zeta") -> 0
borrow(6, "m2", "alpha") -> 0
top_books(8, 3) -> ["zeta(2)", "alpha(1)"]
```

zeta was borrowed twice by the same member. Both loans count.
