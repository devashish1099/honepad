# Hotel booking level 1

Rooms are booked by night. `check_in` and `check_out` are day numbers,
and a stay covers the nights `[check_in, check_out)`. Day numbers have
nothing to do with `timestamp`.

- `add_room(timestamp, room_id, room_type, price)` returns true if added. False if the id exists or `price` is not positive. `price` is per night.
- `book(timestamp, guest_id, room_id, check_in, check_out)` returns `"bookingN"`. Null if the room is missing, `check_out <= check_in`, or another booking on that room overlaps. `N` is a global counter that starts at 1, and only successful bookings use a number.
- `cancel(timestamp, booking_id)` returns true if the booking existed and was not already cancelled. A cancelled booking frees its nights.

## Example

```
add_room(1, "r1", "single", 100) -> true
book(4, "g1", "r1", 10, 12) -> "booking1"
book(5, "g2", "r1", 11, 13) -> null
book(6, "g2", "r1", 12, 14) -> "booking2"
book(7, "g2", "r1", 8, 10) -> "booking3"
book(9, "g2", "r1", 5, 5) -> null
```

Stays that only touch at a day do not overlap.

```
book(2, "g1", "r1", 10, 12) -> "booking1"
cancel(3, "booking1") -> true
cancel(4, "booking1") -> false
book(5, "g3", "r1", 10, 12) -> "booking2"
```
