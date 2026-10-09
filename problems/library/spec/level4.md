# Library level 4

`reserve(timestamp, member_id, book_id)` puts the member in the book's
hold queue and returns their 1-based position. Null if the book is
missing, a copy is free right now (borrow it instead), the member
holds that book, or the member is already in its queue. A reserve
makes the member known.

When a copy comes back and the queue is not empty, the copy goes
straight to the first member in the queue. That is a new loan that
starts at the return time. It counts for `top_books`, and its due date
is 14 days after the handoff. It happens even if that member owes a
fine. `return_book` then reports 0 free copies.

`loans_at(timestamp, member_id, time_at)` returns the ids of the books
the member held at `time_at`, sorted A to Z. A loan covers
`[start, return)`, so at the return time the book is no longer held.
Null if the member is unknown.

## Example

```
add_book(1, "b1", 1) -> true
borrow(2, "m1", "b1") -> 0
reserve(3, "m2", "b1") -> 1
reserve(4, "m3", "b1") -> 2
reserve(5, "m2", "b1") -> null
reserve(6, "m1", "b1") -> null
return_book(10, "m1", "b1") -> 0
loans_at(11, "m2", 10) -> ["b1"]
loans_at(11, "m2", 9) -> []
loans_at(11, "m1", 9) -> ["b1"]
loans_at(11, "m1", 10) -> []
top_books(12, 1) -> ["b1(2)"]
return_book(13, "m2", "b1") -> 0
return_book(14, "m3", "b1") -> 1
reserve(15, "m4", "b1") -> null
```

m1's return hands the copy to m2 at time 10, then m2's goes to m3. When
m3 returns, the queue is empty and the copy is free. So m4 cannot
reserve.

```
borrow(1, "m1", "b1") -> 0
reserve(2, "m2", "b1") -> 1
return_book(1209601, "m1", "b1") -> 0
get_fine(2419201, "m2") -> 0
get_fine(2419202, "m2") -> 10
```

m2's loan starts at the handoff time 1209601, so it is due at 2419201.
