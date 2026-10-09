# Versioned key-value store level 2

`scan_prefix(timestamp, prefix)` returns `key=value` for every key that
starts with `prefix`, sorted by key as strings. An empty prefix matches
every key.

`size(timestamp)` returns the number of keys.

## Example

```
set(1, "user:2", "bo") -> null
set(2, "user:10", "amy") -> null
set(3, "item:1", "pen") -> null
scan_prefix(4, "user:") -> ["user:10=amy", "user:2=bo"]
scan_prefix(5, "") -> ["item:1=pen", "user:10=amy", "user:2=bo"]
size(7) -> 3
```

`"user:10"` sorts before `"user:2"`. An empty value is still a key:
`set(3, "k", "")` then `scan_prefix(5, "k")` is `["k="]`.
