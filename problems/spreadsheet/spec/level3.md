# Spreadsheet level 3

- `copy(from_cell, to_cell)` copies a cell's content to another cell.
  A plain value is copied as is. A copied formula has every cell name
  in it moved by the same columns and rows as the copy (copying `C1`
  to `D3` moves `A1` to `B3`). Copying an empty cell empties the
  target. Returns the target's new value. Returns null, changing
  nothing, if a moved name would leave the sheet or the target's value
  would depend on itself.
- `insert_row(row)` inserts an empty row: every cell at `row` or below
  moves down one row, and every cell name in every formula that points
  at `row` or below is increased by one (each corner of a `SUM` moves
  on its own). Returns false, changing nothing, if `row` is not between
  1 and 99, or if a cell with content or a formula reference would be
  pushed past row 99.

Formula text after a move is written back in the same format, with the
new names.

## Example

```
set_value("A1", 1) -> null
set_value("B1", 10) -> null
set_formula("C1", "=A1+B1") -> 11
copy("C1", "D3") -> 0
get_formula("D3") -> "=B3+C3"
copy("C1", "C2") -> 0
get_formula("C2") -> "=A2+B2"
copy("C1", "B5") -> null
copy("A1", "A9") -> 1
set_formula("E1", "=SUM(A1:A9)") -> 2
insert_row(2) -> true
get_formula("E1") -> "=SUM(A1:A10)"
get_formula("D4") -> "=B4+C4"
get_value("E1") -> 2
set_value("A99", 7) -> null
insert_row(50) -> false
```
