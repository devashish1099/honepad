# Job DAG level 4

- `abort(job_id)` stops a pending or running job; it becomes
  `"aborted"` and its worker, if any, is free. Every pending job that
  depends on it, directly or through other jobs, becomes `"blocked"`.
  Returns the newly blocked ids sorted. Returns null if the job is
  unknown or not pending or running.
- `finished_at(job_id)` returns the time a done job finished. A job
  marked done by `complete` finished at the current clock time.
  Unknown or not done is null.

`add_dependency` also returns false if `depends_on` is aborted.

## Example

```
add_job("a", 4) -> true
add_job("b", 1) -> true
add_job("c", 1) -> true
add_dependency("c", "a") -> true
add_job("d", 2) -> true
add_dependency("d", "c") -> true
set_workers(2) -> true
run_until(1) -> ["b"]
finished_at("b") -> 1
abort("a") -> ["c", "d"]
status("d") -> "blocked"
abort("a") -> null
run_until(2) -> []
complete("c") -> false
add_job("e", 1) -> true
complete("e") -> true
finished_at("e") -> 2
```
