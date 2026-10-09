# Library level 1

Books with a fixed number of copies.

- `add_book(timestamp, book_id, copies)` returns true if added. False if the id exists or `copies` is not positive.
- `borrow(timestamp, member_id, book_id)` returns the copies left after the loan. Null if the book is missing, no copy is free, or the member already holds a copy of that book.
- `return_book(timestamp, member_id, book_id)` returns the free copies after the return. Null if the member does not hold that book.

Members are not created up front. Call timestamps never decrease.

## Example

```
add_book(1, "b1", 2) -> true
add_book(2, "b1", 5) -> false
borrow(4, "m1", "b1") -> 1
borrow(5, "m2", "b1") -> 0
borrow(6, "m3", "b1") -> null
```

Two copies, two loans. The third borrower gets null.

```
borrow(2, "m1", "b1") -> 1
borrow(3, "m1", "b1") -> null
return_book(4, "m2", "b1") -> null
return_book(5, "m1", "b1") -> 2
return_book(6, "m1", "b1") -> null
```

A member holds at most one copy of a book. Returning a book you do not
hold is null, even if the book exists.
