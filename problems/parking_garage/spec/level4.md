# Parking garage level 4

`reserve_spot(timestamp, spot_id, plate, start, end)` holds a spot for
one plate during `[start, end)`. Returns false if the spot is missing,
`end <= start`, or the window overlaps another reservation on that spot.
Windows that only touch do not overlap.

`cancel_reservation(timestamp, spot_id, plate, start)` removes that
plate's reservation that starts at `start`. Returns false if there is
none.

Effect on `park`:

- While a reservation is active, other plates cannot park in that spot.
- When a plate parks inside its own active window and the spot is free,
  it takes that spot, even if a smaller spot would fit. If the spot is
  taken, normal rules apply.
- A car that is already parked is never moved when a window starts.
- A car parked in its own reserved spot pays half the fee for the
  whole stay. Divide the normal fee by 2 and round down.

## Example

```
add_spot(1, "s1", "small") -> true
add_spot(1, "s2", "small") -> true
reserve_spot(1, "s1", "vip", 100, 200) -> true
reserve_spot(2, "s1", "x", 150, 250) -> false
reserve_spot(3, "s1", "x", 200, 300) -> true
park(100, "car1", "small") -> "s2"
park(101, "car2", "small") -> null
park(102, "vip", "small") -> "s1"
current_fee(3702, "vip") -> 1
leave(7303, "vip") -> "s1"
revenue(7304, 0, 7304) -> 3
```

s1 is held for vip at 100, so car1 goes to s2 and car2 finds nothing.
vip pays half: one hour is 2 / 2 = 1, three hours is 6 / 2 = 3.

```
reserve_spot(2, "s1", "vip", 100, 200) -> true
park(50, "z", "small") -> "s1"
park(100, "vip", "small") -> "s2"
current_fee(3700, "vip") -> 2
```

z parked before the window and stays. vip gets a normal spot at the
normal price.
