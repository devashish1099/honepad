# Parking garage level 2

`occupancy(timestamp)` returns one string per size that has at least
one spot, in size order: `size(used/total)`.

`find_car(timestamp, plate)` returns the spot id the plate is parked
in, or null.

## Example

```
occupancy(1) -> []
add_spot(2, "l1", "large") -> true
add_spot(3, "s1", "small") -> true
add_spot(4, "s2", "small") -> true
occupancy(5) -> ["small(0/2)", "large(0/1)"]
park(6, "a", "small") -> "s1"
park(7, "b", "medium") -> "l1"
occupancy(8) -> ["small(1/2)", "large(1/1)"]
find_car(8, "b") -> "l1"
```

There are no medium spots, so medium is left out.
