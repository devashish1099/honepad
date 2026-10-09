# Job DAG level 2

Workers now run jobs on a clock that starts at time 0. There is 1
worker to start.

- `set_workers(count)` sets how many jobs may run at once. Returns
  false if `count < 1`. Jobs already running keep running.
- `run_until(timestamp)` advances the clock to `timestamp` and returns
  the jobs that finished on the way, in finish order (same time: by
  id). Returns null, doing nothing, if `timestamp` is before the
  current time.
- `status(job_id)` returns `"pending"`, `"running"` or `"done"` (later
  levels add more). Unknown is null.

At each moment the clock passes through, starting with the current
time itself and including `timestamp`:

1. Every running job that started at time `s` with duration `d` and
   has `s + d` equal to this moment becomes done.
2. Then, while fewer jobs run than there are workers, the first ready
   job (by id) starts running.

A running job is not ready. `complete` still works on a ready job and
counts as done at the current time; free workers pick up new work the
next time `run_until` is called.

## Example

```
add_job("a", 2) -> true
add_job("b", 3) -> true
add_job("c", 1) -> true
add_job("d", 2) -> true
add_dependency("b", "a") -> true
add_dependency("c", "a") -> true
add_dependency("d", "b") -> true
add_dependency("d", "c") -> true
run_until(0) -> []
status("a") -> "running"
run_until(2) -> ["a"]
status("b") -> "running"
set_workers(2) -> true
run_until(3) -> ["c"]
status("c") -> "done"
run_until(4) -> []
run_until(7) -> ["b", "d"]
run_until(6) -> null
```
