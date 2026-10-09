# KV transactions level 2

Changes can be grouped in transactions, which nest.

- `begin()` starts a transaction inside the current one (or at the top
  level) and returns the new nesting depth (1 for the outermost).
- `commit()` ends the innermost transaction and keeps its changes: they
  become part of the enclosing transaction, or of the store itself if
  it was the outermost one. Returns false if no transaction is open.
- `rollback()` ends the innermost transaction and throws its changes
  away. Returns false if no transaction is open.
- `compare_and_set(key, expected, new_value)` sets the key to
  `new_value` only if it currently holds exactly `expected` (an absent
  key never matches). Returns true if it set it.

While transactions are open, `set`, `delete` and `compare_and_set`
change only the innermost one, and `get`, `count` and every other read
see the store with all open transactions applied in order.

## Example

```
set("a", "1") -> null
begin() -> 1
set("a", "2") -> "1"
begin() -> 2
delete("a") -> true
get("a") -> null
rollback() -> true
get("a") -> "2"
compare_and_set("a", "1", "3") -> false
compare_and_set("a", "2", "3") -> true
commit() -> true
get("a") -> "3"
commit() -> false
rollback() -> false
```
