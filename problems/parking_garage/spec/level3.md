# Parking garage level 3

Parking is billed per started hour (`3600`), with a minimum of one
hour. The hourly rate depends on the size of the spot, not the car:
small 2, medium 3, large 5.

`current_fee(timestamp, plate)` returns what the car would pay if it
left now. Null if the plate is not parked.

`revenue(timestamp, from, to)` returns the sum of fees for every
`leave` whose timestamp is in `[from, to)`.

## Example

```
add_spot(1, "s1", "small") -> true
park(100, "a", "small") -> "s1"
current_fee(100, "a") -> 2
current_fee(3700, "a") -> 2
current_fee(3701, "a") -> 4
leave(7300, "a") -> "s1"
revenue(7302, 0, 7300) -> 0
revenue(7302, 0, 7301) -> 4
```

Zero time still pays one hour. Exactly 3600 is one hour, and 3601 is
two. The leave at 7300 is not inside `[0, 7300)`.

```
add_spot(1, "m1", "medium") -> true
add_spot(1, "l1", "large") -> true
park(10, "a", "small") -> "m1"
park(10, "b", "small") -> "l1"
leave(10810, "a") -> "m1"
leave(10810, "b") -> "l1"
revenue(10820, 0, 10820) -> 24
```

Both stays are 3 hours: 3 * 3 + 3 * 5.
