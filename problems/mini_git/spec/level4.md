# Mini git level 4

- `merge(name)` brings branch `name` into the current branch. Returns
  null, changing nothing, if the branch is unknown, is the current
  branch, or `diff()` is not empty. Otherwise, with ours = current
  head and theirs = `name`'s head:
  - If theirs has no commit, or is ours or an ancestor of ours (reached
    by following parents), return `"up to date"`.
  - If ours has no commit or is an ancestor of theirs, the current
    branch moves to theirs and the working tree becomes its files.
    Return `"fast-forward"`.
  - Otherwise do a three-way merge. The base is the common ancestor of
    ours and theirs with the highest commit number. For each path in
    any of the three, with B, O, T its content in base, ours and
    theirs (a missing file counts as a value): if O equals T, or T
    equals B, keep O; else if O equals B, take T; else the path
    conflicts. If any path conflicts, return `"conflict:"` followed by
    the conflicting paths sorted and joined by commas, and change
    nothing. If none does, the result becomes the working tree and is
    committed with message `"merge <name>"` and two parents (ours
    first). Return the new commit id.
- `file_history(path)` walks from the head along first parents and
  returns the ids of commits whose content for `path` differs from
  their first parent's (no parent counts as no file), newest first.

`log` follows first parents.

## Example

```
write("a", "1") -> "created"
write("b", "1") -> "created"
commit("base") -> "c1"
branch("dev") -> true
switch_branch("dev") -> true
write("a", "dev") -> "modified"
commit("d1") -> "c2"
switch_branch("main") -> true
merge("dev") -> "fast-forward"
write("b", "main") -> "modified"
commit("m1") -> "c3"
switch_branch("dev") -> true
write("c", "dev") -> "created"
commit("d2") -> "c4"
switch_branch("main") -> true
merge("dev") -> "c5"
log(9) -> ["c5:merge dev", "c3:m1", "c2:d1", "c1:base"]
read("c") -> "dev"
switch_branch("dev") -> true
write("b", "dev") -> "modified"
commit("d3") -> "c6"
switch_branch("main") -> true
merge("dev") -> "conflict:b"
file_history("a") -> ["c2", "c1"]
```
