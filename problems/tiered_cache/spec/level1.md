# Tiered cache level 1

A cache stores string values under keys. Each entry has a `size` in
bytes. The cache holds at most `capacity` bytes, 100 to start.

- `put(timestamp, key, value, size)` stores the value, replacing any
  value already under `key`. Returns the list of keys evicted to make
  room (see below), which is often empty. Returns null, and changes
  nothing, if `size <= 0` or `size` is larger than the capacity.
- `get(timestamp, key)` returns the value, or null if the key is not
  stored.
- `delete(timestamp, key)` removes the key. Returns true if it was
  stored.
- `used_bytes(timestamp)` returns the total size of all stored entries.

Every `put` and every successful `get` uses its key. When a `put`
leaves the total above the capacity, the cache evicts the entry whose
last use is oldest, again and again, until the total fits. The key
just put is never evicted. The returned list is in eviction order.

Call timestamps never decrease.

## Example

```
put(1, "a", "apple", 40) -> []
put(2, "b", "berry", 30) -> []
put(3, "c", "cherry", 20) -> []
get(4, "a") -> "apple"
get(4, "z") -> null
put(5, "d", "date", 30) -> ["b"]
get(6, "b") -> null
used_bytes(6) -> 90
put(7, "a", "avocado", 101) -> null
delete(8, "c") -> true
delete(8, "c") -> false
used_bytes(9) -> 70
```

The `put` of `d` needs 30 bytes. `b` was used least recently, so it
goes first; that frees enough room.
