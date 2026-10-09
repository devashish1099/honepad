# Job DAG level 3

- `set_priority(job_id, priority)` sets a pending job's priority
  (default 0). Returns false if the job is unknown or not pending.
  Workers now start the ready job with the highest priority first,
  then the lowest id. `ready_jobs` stays sorted by id.
- `fail(job_id)` reports that a running job failed. Its worker is free
  at once. If the job has now failed fewer than 3 times it goes back
  to pending and the call returns `"retry"`. On the third failure it
  becomes `"failed"`, the call returns `"failed"`, and every pending
  job that depends on it, directly or through other jobs, becomes
  `"blocked"`. Not running returns null.
- `critical_path()` returns the largest total duration along any chain
  of dependencies, counting every job whatever its status. No jobs is
  0.

`add_dependency` also returns false if `depends_on` is failed or
blocked. Blocked and failed jobs never run.

## Example

```
add_job("a", 2) -> true
add_job("b", 1) -> true
add_job("c", 1) -> true
add_dependency("c", "a") -> true
set_priority("b", 5) -> true
run_until(0) -> []
status("b") -> "running"
run_until(1) -> ["b"]
fail("a") -> "retry"
run_until(1) -> []
fail("a") -> "retry"
run_until(1) -> []
fail("a") -> "failed"
status("c") -> "blocked"
critical_path() -> 3
add_dependency("c", "b") -> false
```
