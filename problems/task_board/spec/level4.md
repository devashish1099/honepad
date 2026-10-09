# Task board level 4

`complete(timestamp, task_id, user_id)` finishes a task. It is true only
if the task has a live assignment to that user. A completed task is
removed, as if `remove_task` was called, and the user's completed count
goes up by one.

`overdue(timestamp)` lists assignments that ended without being
completed, as `taskId(userId)`. A task stays on the list until it is
assigned again, completed, or removed. Sort by the end time, earliest
first, then task id A to Z.

`top_completers(timestamp, n)` returns at most `n` strings
`userId(count)`, sorted by count, high to low, then id A to Z. Users with
0 still appear.

## Example

```
assign(10, "c", "u1", 5) -> true
assign(10, "a", "u2", 5) -> true
assign(11, "b", "u1", 3) -> true
overdue(14) -> ["b(u1)"]
overdue(15) -> ["b(u1)", "a(u2)", "c(u1)"]
assign(16, "b", "u2", 10) -> true
overdue(17) -> ["a(u2)", "c(u1)"]
remove_task(18, "a") -> true
overdue(19) -> ["c(u1)"]
overdue(26) -> ["c(u1)", "b(u2)"]
```

b ends at 14. a and c both end at 15, so they are sorted by id. Giving b
to u2 takes it off the list until that assignment ends at 26.

```
assign(10, "b", "u1", 10) -> true
complete(20, "b", "u1") -> false
top_completers(21, 5) -> ["u1(1)", "u2(0)"]
```

At 20 the assignment has ended, so completing is too late. u1's count
of 1 comes from an earlier task.
