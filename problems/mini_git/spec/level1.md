# Mini git level 1

A tiny version control system. The working tree maps file paths to
string contents. A commit saves a copy of the whole working tree.

- `write(path, content)` sets a file in the working tree. Returns
  `"created"` if the path was not there, `"modified"` if its content
  changed, or `"unchanged"`. Empty content is allowed.
- `read(path)` returns the working-tree content, or null.
- `remove(path)` deletes a file from the working tree. Returns true if
  it was there.
- `commit(message)` saves the working tree and returns the new commit
  id: `"c1"`, `"c2"`, ... counting every commit ever made. Returns
  null, saving nothing, if `message` is empty or the working tree is
  exactly the same as the last commit (or, before any commit, is
  empty).

## Example

```
write("readme", "hi") -> "created"
write("readme", "hi") -> "unchanged"
write("readme", "hello") -> "modified"
read("readme") -> "hello"
commit("") -> null
commit("first") -> "c1"
commit("again") -> null
write("notes", "") -> "created"
commit("notes") -> "c2"
remove("notes") -> true
remove("notes") -> false
read("notes") -> null
commit("drop notes") -> "c3"
```
