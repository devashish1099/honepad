# Versioned key-value store level 1

String keys mapped to string values.

- `set(timestamp, key, value)` stores the value. Returns the previous value, or null if the key was missing.
- `get(timestamp, key)` returns the value, or null.
- `delete(timestamp, key)` returns true if the key existed and is now gone, false otherwise.
- `compare_and_set(timestamp, key, expected, value)` stores `value` only if the key exists and its value equals `expected`. Returns whether it stored.

## Example

```
set(1, "a", "1") -> null
set(3, "a", "2") -> "1"
get(4, "a") -> "2"
delete(5, "a") -> true
delete(6, "a") -> false
```

```
compare_and_set(1, "a", "x", "y") -> false
set(2, "a", "x") -> null
compare_and_set(3, "a", "z", "y") -> false
compare_and_set(4, "a", "x", "y") -> true
get(5, "a") -> "y"
```

A missing key never matches, not even the empty string.
