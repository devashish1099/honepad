# Tiered cache level 3

- `pin(timestamp, key)` protects a stored key from eviction. Returns
  true if the key was stored and not pinned. `unpin(timestamp, key)`
  removes the protection; true if the key was stored and pinned.
  Pinned entries can still expire, be deleted and be replaced (a
  replaced entry stays pinned). Pinning is not a use.
- Eviction skips pinned entries. `put` now returns null, changing
  nothing, if `size` plus the sizes of the other pinned entries is
  larger than the capacity.
- `set_capacity(timestamp, capacity)` changes the capacity and evicts
  as `put` does until the total fits or only pinned entries are left.
  Returns the evicted keys. `capacity <= 0` returns null.

Pinned entries may leave the total above the capacity after
`set_capacity`. Nothing is evicted until the next call that evicts.

## Example

```
put(1, "a", "apple", 50) -> []
put(2, "b", "berry", 30) -> []
pin(3, "a") -> true
pin(3, "a") -> false
put(4, "c", "cherry", 40) -> ["b"]
put(5, "d", "date", 60) -> null
set_capacity(6, 40) -> ["c"]
keys(6) -> ["a"]
used_bytes(6) -> 50
unpin(7, "a") -> true
put(8, "e", "elder", 10) -> ["a"]
```
