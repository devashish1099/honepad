# KV transactions level 4

- `history(key)` returns, oldest first, each version in which the
  key's value differs from the version before, as `"version:value"`,
  with `(none)` as the value when the key was removed.
- `diff(from_version, to_version)` returns the keys whose values
  differ between the two versions, sorted, as `"key:old->new"` with
  `(none)` for an absent key. Returns null if either version does not
  exist.
- `revert(version)` records a new version identical to an older one
  and returns the new version number. Returns null if a transaction is
  open, the version does not exist, or it is identical to the latest
  version.

## Example

```
set("a", "1") -> null
set("b", "1") -> null
set("a", "2") -> "1"
delete("b") -> true
history("a") -> ["1:1", "3:2"]
history("b") -> ["2:1", "4:(none)"]
diff(1, 4) -> ["a:1->2"]
diff(4, 9) -> null
revert(2) -> 5
get("b") -> "1"
history("b") -> ["2:1", "4:(none)", "5:1"]
revert(5) -> null
begin() -> 1
revert(0) -> null
```
