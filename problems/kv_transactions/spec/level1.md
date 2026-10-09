# KV transactions level 1

A key-value store of strings. Empty strings are valid keys and values.

- `set(key, value)` stores the value. Returns the previous value, or
  null if the key was absent.
- `get(key)` returns the value, or null.
- `delete(key)` removes the key. Returns true if it was there.
- `count(value)` returns how many keys hold exactly `value`.

## Example

```
set("a", "red") -> null
set("b", "red") -> null
set("a", "blue") -> "red"
get("a") -> "blue"
get("c") -> null
count("red") -> 1
count("blue") -> 1
delete("b") -> true
delete("b") -> false
count("red") -> 0
```
