# Versioned key-value store level 4

Transactions can be nested.

- `begin(timestamp)` opens a transaction and returns the new depth (1 for the outermost).
- `commit(timestamp)` merges the innermost transaction into its parent. If the parent is the store, the changes become permanent.
- `rollback(timestamp)` throws away the innermost transaction.
- Both return false when no transaction is open.

Reads see the innermost view, and that includes deletes. A rollback
restores each key exactly as it was stored, value and expiry. If that
expiry has passed, the key stays expired.

Backups:

- `backup(timestamp)` saves every live key and how much TTL it has left. It returns the number of keys saved, or null if a transaction is open.
- `restore(timestamp, time_to_restore)` replaces the whole store with the latest backup taken at or before `time_to_restore`. Each restored TTL counts from `timestamp`, the restore time. It returns false if a transaction is open or no backup qualifies.

## Example

```
begin(1) -> 1
set(2, "a", "1") -> null
begin(3) -> 2
set(4, "a", "2") -> "1"
get(5, "a") -> "2"
rollback(6) -> true
get(7, "a") -> "1"
commit(8) -> true
get(9, "a") -> "1"
commit(10) -> false
```

```
set_with_ttl(1, "k", "v", 10) -> null
begin(2) -> 1
set(3, "k", "w") -> "v"
get(12, "k") -> "w"
rollback(13) -> true
get(14, "k") -> null
```

Inside the transaction, k had no TTL. The rollback brings back the
stored row, which expired at 11.

```
set(1, "a", "1") -> null
set_with_ttl(10, "b", "2", 20) -> null
set_with_ttl(10, "c", "3", 1) -> null
backup(11) -> 2
set(12, "a", "z") -> "1"
delete(13, "b") -> true
restore(100, 11) -> true
get(101, "a") -> "1"
ttl_remaining(101, "b") -> 18
get(101, "c") -> null
restore(102, 5) -> false
```

c had expired by 11, so it was not saved. b had 19 left at the backup.
After the restore at 100 it expires at 119, so 18 remain at 101.
