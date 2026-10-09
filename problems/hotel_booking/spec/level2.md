# Hotel booking level 2

`available(timestamp, room_type, check_in, check_out)` returns every
room of that type that is free for the whole stay, as `roomId(price)`.
Sort by price, low to high, then id A to Z. An invalid range returns
`[]`.

`book_any(timestamp, guest_id, room_type, check_in, check_out)` books
the first room `available` would list. Null if there is none or the
range is invalid.

## Example

```
add_room(1, "s2", "single", 80) -> true
add_room(1, "s1", "single", 80) -> true
add_room(1, "s3", "single", 60) -> true
available(2, "single", 1, 3) -> ["s3(60)", "s1(80)", "s2(80)"]
book(3, "g1", "s3", 2, 4) -> "booking1"
available(4, "single", 1, 3) -> ["s1(80)", "s2(80)"]
available(5, "single", 4, 6) -> ["s3(60)", "s1(80)", "s2(80)"]
```

```
add_room(1, "b", "single", 80) -> true
add_room(1, "a", "single", 80) -> true
book_any(2, "g1", "single", 1, 3) -> "booking1"
book_any(3, "g2", "single", 2, 4) -> "booking2"
book_any(4, "g3", "single", 2, 3) -> null
```

booking1 got room a, the lower id at the same price. booking2 got b.
