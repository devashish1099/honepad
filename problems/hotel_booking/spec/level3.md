# Hotel booking level 3

Each room type has a waitlist.

`waitlist(timestamp, guest_id, room_type, check_in, check_out)` adds a
request to the end of that type's list and returns its 1-based
position. Null if the range is invalid, or if a room of that type is
free for the stay right now (book it instead). A request for a type
with no rooms at all is allowed. A guest can have more than one
request.

The list is processed after every successful `cancel` of a room of
that type, and after every `add_room` of that type:

- Go through the requests in order.
- A request that now fits is booked with `book_any` rules and leaves the list.
- A request that does not fit stays, in the same order.
- Every request is checked once per pass, so a later request can be booked ahead of an earlier one.

`guest_bookings(timestamp, guest_id)` returns the guest's bookings that
are not cancelled, as `bookingN(roomId)`. Sort by `check_in`, then by
booking number (as a number). Null if the guest is unknown. A guest is
known after a successful booking or waitlist request.

`loyalty(timestamp, guest_id)` returns the total nights in the guest's
bookings that are not cancelled. Null if the guest is unknown.

## Example

```
add_room(1, "d1", "double", 200) -> true
book(2, "g1", "d1", 1, 5) -> "booking1"
waitlist(3, "g2", "double", 3, 6) -> 1
waitlist(4, "g3", "double", 6, 8) -> null
waitlist(5, "g4", "double", 2, 4) -> 2
cancel(7, "booking1") -> true
guest_bookings(8, "g2") -> ["booking2(d1)"]
guest_bookings(8, "g4") -> []
loyalty(9, "g2") -> 3
add_room(10, "d2", "double", 150) -> true
guest_bookings(11, "g4") -> ["booking3(d2)"]
```

d1 is free on nights 6 and 7, so g3 is told to book. After the cancel,
g2 gets d1. g4's nights 2 and 3 now clash with g2, so g4 waits. The new
room d2 takes g4.

```
book(2, "g1", "r1", 1, 10) -> "booking1"
book(2, "g1", "r1", 10, 20) -> "booking2"
waitlist(3, "a", "single", 5, 15) -> 1
waitlist(4, "b", "single", 12, 14) -> 2
waitlist(5, "c", "single", 2, 3) -> 3
cancel(6, "booking2") -> true
guest_bookings(7, "b") -> ["booking3(r1)"]
guest_bookings(7, "a") -> []
```

a still clashes with booking1, so b is booked ahead of it.
