# Spreadsheet level 1

A sheet has columns `A` to `Z` and rows 1 to 99. A cell is named by its
column letter and row number, like `"B7"` or `"Z99"`. Every cell name
in the calls is valid. A cell is empty or holds an integer.

- `set_value(cell, value)` puts an integer in the cell. Returns the
  cell's previous value, or null if it was empty.
- `get_value(cell)` returns the cell's value. Empty is 0.
- `clear(cell)` empties the cell. Returns true if it held something.
- `sum_range(from, to)` returns the sum of every cell in the rectangle
  with `from` as its top-left and `to` as its bottom-right corner.
  Returns null if `from`'s column is after `to`'s, or `from`'s row is
  below `to`'s.

## Example

```
get_value("A1") -> 0
set_value("A1", 4) -> null
set_value("A1", 5) -> 4
set_value("B2", 10) -> null
set_value("A10", 1) -> null
sum_range("A1", "B2") -> 15
sum_range("A1", "A10") -> 6
sum_range("B2", "A1") -> null
clear("A1") -> true
clear("A1") -> false
get_value("A1") -> 0
```
