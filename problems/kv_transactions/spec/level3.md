# KV transactions level 3

The store keeps versions. Version 0 is the empty store. Each time the
store itself changes, a new version is recorded with the next number:
after a `set` or `delete` outside any transaction, or after the
outermost `commit`. If the store ends up exactly as it was (for
example setting a key to the value it already has, or committing a
transaction that changed nothing in the end), no version is recorded.
Changes inside open transactions are not versions.

- `version()` returns the latest version number.
- `get_at(key, version)` returns the key's value in that version, or
  null if absent or the version does not exist.
- `scan(prefix)` returns the keys currently visible that start with
  `prefix`, sorted, as `"key=value"`.
- `increment(key, delta)` treats the value as an integer and adds
  `delta`. An absent key counts as 0. Returns the new value, stored as
  a string, like `set` would. Returns null, changing nothing, if the
  value is not an integer (an optional `-` and 1 to 9 digits, nothing
  else) or the result would be outside -999999999 to 999999999.

## Example

```
version() -> 0
set("a", "1") -> null
set("a", "1") -> "1"
version() -> 1
begin() -> 1
set("b", "2") -> null
set("c", "3") -> null
version() -> 1
commit() -> true
version() -> 2
get_at("b", 1) -> null
get_at("b", 2) -> "2"
scan("") -> ["a=1", "b=2", "c=3"]
increment("n", 5) -> 5
increment("n", -8) -> -3
set("s", "007") -> null
increment("s", 1) -> 8
set("t", "x") -> null
increment("t", 1) -> null
```
