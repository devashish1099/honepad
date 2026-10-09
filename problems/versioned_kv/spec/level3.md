# Versioned key-value store level 3

`set_with_ttl(timestamp, key, value, ttl)` stores a value that lives in
`[timestamp, timestamp + ttl)`. It returns the previous live value, or
null.

From now on every method only sees keys that are live at its own
`timestamp`. An expired key acts as if it was never set: `get` is null,
`delete` and `compare_and_set` are false, `scan_prefix` and `size` skip
it, and a `set` over it returns null.

- A plain `set` clears any TTL on the key.
- `compare_and_set` keeps the key's current expiry.

`ttl_remaining(timestamp, key)` returns the time left until expiry, -1
for a live key with no TTL, or null if the key is missing or expired.

## Example

```
set_with_ttl(10, "a", "1", 5) -> null
ttl_remaining(12, "a") -> 3
get(14, "a") -> "1"
get(15, "a") -> null
delete(16, "a") -> false
set(17, "a", "2") -> null
ttl_remaining(18, "a") -> -1
```

At 15 the key has expired.

```
set_with_ttl(20, "c", "x", 10) -> null
compare_and_set(25, "c", "x", "y") -> true
get(29, "c") -> "y"
get(30, "c") -> null
```

The swap kept the old expiry of 30.
