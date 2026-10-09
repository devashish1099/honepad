# Mini git level 3

Branches are names that point at commits. The branch `"main"` exists
from the start. The current branch starts as `"main"`. `commit` moves
the current branch to the new commit, and "head" now means the commit
the current branch points at (`log`, `diff`, `restore` use it).

- `branch(name)` creates a branch pointing at the head. Returns false
  if the name exists or there is no commit yet. It does not switch.
- `switch_branch(name)` makes `name` the current branch and replaces
  the working tree with that branch's head. Returns false, changing
  nothing, if the branch is unknown, it is already current, or `diff()`
  is not empty.
- `current_branch()` returns the current branch's name.

## Example

```
write("a", "1") -> "created"
branch("dev") -> false
commit("base") -> "c1"
branch("dev") -> true
branch("dev") -> false
switch_branch("dev") -> true
current_branch() -> "dev"
write("a", "2") -> "modified"
switch_branch("main") -> false
commit("dev work") -> "c2"
switch_branch("main") -> true
read("a") -> "1"
log(5) -> ["c1:base"]
switch_branch("dev") -> true
log(5) -> ["c2:dev work", "c1:base"]
```
