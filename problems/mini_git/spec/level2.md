# Mini git level 2

The head is the most recent commit. Each commit after the first has
the previous head as its parent.

- `log(n)` returns up to `n` commits, starting at the head and
  following parents, as `"commit_id:message"`. `n <= 0` or no commits
  is an empty list.
- `diff()` compares the working tree with the head commit (an empty
  tree before any commit). It returns one entry per changed path,
  sorted by path: `"+path"` added, `"-path"` removed, `"~path"`
  content changed.
- `restore(path)` puts one path back the way the head commit has it:
  its content, or no file if the head has none. Returns true if the
  working tree changed.

## Example

```
write("a", "1") -> "created"
commit("one") -> "c1"
write("b", "1") -> "created"
commit("two") -> "c2"
log(5) -> ["c2:two", "c1:one"]
log(1) -> ["c2:two"]
write("a", "2") -> "modified"
remove("b") -> true
write("c", "1") -> "created"
diff() -> ["~a", "-b", "+c"]
restore("a") -> true
restore("a") -> false
restore("c") -> true
diff() -> ["-b"]
```
