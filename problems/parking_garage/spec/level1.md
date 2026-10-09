# Parking garage level 1

Spots come in three sizes, smallest first: `small`, `medium`, `large`.
A car fits any spot of its size or bigger.

- `add_spot(timestamp, spot_id, size)` returns true if added. False if the id exists or the size is not one of the three.
- `park(timestamp, plate, size)` returns the spot id the car took. Null if the plate is already parked, the size is unknown, or nothing fits.
- `leave(timestamp, plate)` returns the spot id it freed, or null if the plate is not parked.

`park` picks the smallest free size that fits. Among spots of that
size it picks the lowest id, comparing ids as strings.

## Example

```
add_spot(1, "s1", "small") -> true
add_spot(2, "m1", "medium") -> true
add_spot(3, "l1", "large") -> true
park(6, "car1", "small") -> "s1"
park(7, "car2", "small") -> "m1"
park(8, "car3", "medium") -> "l1"
park(9, "car4", "small") -> null
leave(11, "car2") -> "m1"
park(14, "car5", "medium") -> "m1"
```

When s1 is taken, the next small car goes up to medium.

```
add_spot(1, "s2", "small") -> true
add_spot(2, "s10", "small") -> true
add_spot(3, "s1", "small") -> true
park(4, "a", "small") -> "s1"
park(5, "b", "small") -> "s10"
park(6, "c", "small") -> "s2"
```

As strings, `"s10"` comes before `"s2"`.
