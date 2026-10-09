# Spreadsheet level 2

Cells can hold formulas. A formula is `=` followed by terms joined by
`+` or `-`, with no spaces. A term is one of:

- a number: 1 to 6 digits (`7`, `0`, `120`);
- a cell name: one capital letter and a row from 1 to 99 with no
  leading zero (`A1`, `C42`);
- `SUM(X:Y)` with two cell names, where `X` is not after `Y` in column
  or row; it adds up that rectangle.

A formula's value is computed from the current values of the cells it
names, every time it is read. Empty cells count as 0.

- `set_formula(cell, formula)` puts a formula in the cell and returns
  its value. Returns null, changing nothing, if the text is not a valid
  formula, or if the cell's value would depend on itself (directly, or
  through other formulas, including through a `SUM`).
- `get_formula(cell)` returns the cell's formula text, or null if the
  cell is empty or holds a plain value.
- `dependents(cell)` returns the cells whose value depends on `cell`,
  directly or through other formulas. Sort by column, then by row
  number (so `B9` comes before `B10`).

`set_value` replaces a formula. Its return value is the cell's value
before the change, which for a formula is the computed value.

## Example

```
set_value("A1", 2) -> null
set_value("A2", 3) -> null
set_formula("A3", "=A1+A2") -> 5
set_formula("B1", "=SUM(A1:A3)-1") -> 9
set_value("A1", 10) -> 2
get_value("A3") -> 13
get_value("B1") -> 25
get_formula("B1") -> "=SUM(A1:A3)-1"
set_formula("A1", "=B1") -> null
set_formula("C1", "=A1*2") -> null
set_formula("C1", "=A01") -> null
dependents("A1") -> ["A3", "B1"]
dependents("A3") -> ["B1"]
set_value("A3", 0) -> 13
get_formula("A3") -> null
get_value("B1") -> 12
```
