# Hotel booking level 4

`merge_guests(timestamp, keep, drop)` moves every booking and waitlist
request of `drop` to `keep`. Waitlist requests keep their positions.
Afterwards `drop` is unknown. Returns false if either guest is unknown
or they are the same.

`revenue_at(timestamp, time_at)` returns `price * nights` summed over
the bookings that existed at `time_at`. A booking exists from the
timestamp of the call that created it, and stops existing at the
timestamp of its cancel. Waitlist bookings are created by the
`cancel` or `add_room` call that processed them.

## Example

```
add_room(1, "r1", "single", 100) -> true
book(2, "g1", "r1", 10, 12) -> "booking1"
book(4, "g2", "r1", 12, 14) -> "booking2"
cancel(7, "booking1") -> true
revenue_at(20, 1) -> 0
revenue_at(20, 3) -> 200
revenue_at(20, 4) -> 400
revenue_at(20, 7) -> 200
```

```
add_room(1, "r1", "single", 100) -> true
add_room(1, "r2", "single", 100) -> true
book(2, "a", "r1", 5, 7) -> "booking1"
book(3, "b", "r2", 1, 3) -> "booking2"
merge_guests(4, "a", "b") -> true
guest_bookings(5, "a") -> ["booking2(r2)", "booking1(r1)"]
guest_bookings(5, "b") -> null
loyalty(6, "a") -> 4
merge_guests(7, "a", "b") -> false
```

booking2 checks in on day 1, so it comes first.
