# Job DAG level 1

A build system runs jobs that depend on each other.

- `add_job(job_id, duration)` adds a pending job that takes `duration`
  time units. Returns true if added. False if the id exists or
  `duration <= 0`.
- `add_dependency(job_id, depends_on)` says `job_id` may only start
  after `depends_on` is done. Returns true if added. Returns false if
  either job is unknown, they are the same job, the dependency already
  exists, `job_id` is not pending, or the new dependency would create a
  cycle (`depends_on` already depends on `job_id`, directly or through
  other jobs).
- `ready_jobs()` lists the pending jobs whose dependencies are all
  done, sorted by id.
- `complete(job_id)` marks a ready job done. Returns true if it was
  ready. A job that is not pending, or still waits on a dependency,
  gives false.

## Example

```
add_job("compile", 3) -> true
add_job("test", 2) -> true
add_job("lint", 1) -> true
add_job("ship", 1) -> true
add_job("lint", 5) -> false
add_dependency("test", "compile") -> true
add_dependency("ship", "test") -> true
add_dependency("ship", "lint") -> true
add_dependency("compile", "ship") -> false
add_dependency("ship", "ship") -> false
ready_jobs() -> ["compile", "lint"]
complete("test") -> false
complete("compile") -> true
ready_jobs() -> ["lint", "test"]
complete("lint") -> true
complete("test") -> true
ready_jobs() -> ["ship"]
add_dependency("test", "lint") -> false
```
