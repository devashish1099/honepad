# Task board level 2

`remove_task(timestamp, task_id)` deletes a task. Returns false if it is
missing. The id can be added again later.

`search(timestamp, prefix, n)` returns at most `n` strings
`taskId(priority)`, for tasks whose id starts with `prefix`. The match
is case-sensitive, and an empty prefix matches every task. Sort by
priority, high to low, then id A to Z.

## Example

```
add_task(1, "bug-1", 5) -> true
add_task(2, "bug-2", 9) -> true
add_task(3, "feat-1", 7) -> true
add_task(4, "bug-10", 5) -> true
search(5, "bug", 10) -> ["bug-2(9)", "bug-1(5)", "bug-10(5)"]
search(6, "bug", 2) -> ["bug-2(9)", "bug-1(5)"]
search(7, "", 2) -> ["bug-2(9)", "feat-1(7)"]
search(8, "doc", 5) -> []
```

bug-1 and bug-10 tie on 5. As strings, `"bug-1"` comes first.
