# Spreadsheet level 4

- `undo()` takes back the most recent change that has not been undone.
  Returns false if there is none.
- `redo()` re-applies the most recently undone change. Returns false
  if there is none.

A change is any call to `set_value`, `set_formula`, `copy` or
`insert_row` that does not return null or false, and any `clear` that
returns true. Making a new change forgets everything that could be
redone.

## Example

```
set_value("A1", 1) -> null
set_formula("B1", "=A1+1") -> 2
set_formula("B1", "=A1+") -> null
undo() -> true
get_formula("B1") -> null
get_value("B1") -> 0
undo() -> true
get_value("A1") -> 0
undo() -> false
redo() -> true
get_value("A1") -> 1
set_value("A1", 5) -> 1
redo() -> false
undo() -> true
get_value("A1") -> 1
```
