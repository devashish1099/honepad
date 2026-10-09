# Tiered cache level 2

Entries can expire.

- `put_with_ttl(timestamp, key, value, size, ttl)` works like `put`,
  but the entry exists only while the current timestamp is below
  `timestamp + ttl`. `ttl <= 0` returns null. A plain `put` on the key
  later removes the expiry.
- `ttl_left(timestamp, key)` returns how long the key has left
  (expiry minus `timestamp`), -1 if it never expires, or null if it is
  not stored.
- `keys(timestamp)` returns the stored keys, most recently used first.

Every call first removes the entries whose expiry has come, using its
own timestamp. Removing an expired entry is not an eviction: it never
appears in a returned eviction list. `ttl_left` and `keys` are not
uses.

## Example

```
put_with_ttl(1, "a", "apple", 40, 10) -> []
put(2, "b", "berry", 30) -> []
ttl_left(3, "a") -> 8
ttl_left(3, "b") -> -1
keys(4) -> ["b", "a"]
get(5, "a") -> "apple"
keys(5) -> ["a", "b"]
ttl_left(11, "a") -> null
keys(11) -> ["b"]
put_with_ttl(12, "c", "cherry", 10, 0) -> null
```
