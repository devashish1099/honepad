# Task board level 3

Users take on tasks, up to a quota of live tasks each.

- `add_user(timestamp, user_id, quota)` returns true if added. False if the id exists or `quota` is not positive.
- `assign(timestamp, task_id, user_id, ttl)` gives the task to the user for `[timestamp, timestamp + ttl)`. Returns false if the task or user is missing, `ttl` is not positive, the task already has a live assignment (to anyone), or the user already holds `quota` live tasks.
- `get_user_tasks(timestamp, user_id)` returns the user's live tasks as `taskId(priority)`, sorted like `search`. Null if the user is missing.

An assignment stops being live at `timestamp + ttl`. Removing a task
also ends its assignment.

## Example

```
add_task(1, "t1", 5) -> true
add_task(2, "t2", 3) -> true
add_task(3, "t3", 9) -> true
add_user(4, "u1", 2) -> true
assign(10, "t1", "u1", 100) -> true
assign(11, "t2", "u1", 50) -> true
assign(12, "t3", "u1", 100) -> false
get_user_tasks(13, "u1") -> ["t1(5)", "t2(3)"]
assign(61, "t3", "u1", 100) -> true
get_user_tasks(61, "u1") -> ["t3(9)", "t1(5)"]
```

u1 is full until t2 ends at 61. At 61, t2 is no longer live.

```
add_user(63, "u2", 1) -> true
assign(64, "t1", "u2", 10) -> false
assign(110, "t1", "u2", 10) -> true
```

t1 is live for u1 until 110, so u2 must wait.
