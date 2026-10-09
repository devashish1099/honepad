# Task board level 1

Tasks with an integer priority. The priority can be zero or negative.

- `add_task(timestamp, task_id, priority)` returns true if added, false if the id exists.
- `update_task(timestamp, task_id, priority)` sets a new priority. Returns false if the task is missing.
- `get_task(timestamp, task_id)` returns the priority, or null if the task is missing.

## Example

```
add_task(1, "t1", 5) -> true
add_task(2, "t1", 9) -> false
get_task(3, "t1") -> 5
update_task(4, "t1", 7) -> true
get_task(5, "t1") -> 7
update_task(6, "t2", 1) -> false
get_task(7, "t2") -> null
```

The failed add does not change t1.
