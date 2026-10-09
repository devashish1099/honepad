# Tiered cache level 4

A second, cold tier keeps evicted entries. Its capacity is 0 to start,
so until it is raised nothing is kept.

- `set_cold_capacity(timestamp, capacity)` sets the cold capacity.
  Returns false if `capacity < 0`. Shrinking drops the cold entries
  whose arrival is oldest until the cold total fits.
- `cold_keys(timestamp)` returns the cold keys, most recent first.
- `stats(timestamp)` returns `"hits=H,cold_hits=C,misses=M"`: how many
  `get` calls found the key in the main tier, in the cold tier, or
  nowhere.

Each evicted entry moves to the cold tier as its most recent entry
(no longer pinned). An entry bigger than the cold capacity is dropped
instead. If the cold total is then too big, the oldest cold entries
are dropped until it fits. Expiry, `delete` and `ttl_left` apply to
both tiers. `keys` and `used_bytes` still cover the main tier only,
and only main-tier keys can be pinned.

`get` on a cold key returns its value and moves it back to the main
tier as the most recently used entry, evicting as usual (those
evictions go to the cold tier). If it cannot fit because of pinned
entries, it stays cold and becomes the most recent cold entry. `put`
on a cold key removes the cold copy.

## Example

```
set_cold_capacity(1, 100) -> true
put(2, "a", "apple", 60) -> []
put(3, "b", "berry", 60) -> ["a"]
cold_keys(4) -> ["a"]
get(5, "a") -> "apple"
keys(5) -> ["a"]
cold_keys(5) -> ["b"]
put(6, "c", "cherry", 100) -> ["a"]
cold_keys(7) -> ["a"]
get(8, "b") -> null
get(9, "a") -> "apple"
keys(9) -> ["a"]
cold_keys(9) -> ["c"]
get(10, "a") -> "apple"
stats(11) -> "hits=1,cold_hits=2,misses=1"
```

Getting `a` from the cold tier brings it back and pushes `b` out to
the cold tier. Putting `c` evicts `a`; the cold tier then holds 120
bytes, so its oldest entry `b` is dropped. The second `get` of `a`
brings it back again and sends `c` to the cold tier.
