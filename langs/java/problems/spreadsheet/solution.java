import java.util.ArrayDeque;
import java.util.ArrayList;
import java.util.Deque;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Term {
    int sign;
    int kind; // 0 number, 1 cell, 2 range
    int number;
    int col;
    int row;
    int col2;
    int row2;
}

class Cell {
    final Integer value;
    final List<Term> terms;

    Cell(Integer value, List<Term> terms) {
        this.value = value;
        this.terms = terms;
    }
}

public class Simulation {
    private Map<String, Cell> cells = new HashMap<>();
    private final Deque<Map<String, Cell>> undoStack = new ArrayDeque<>();
    private final Deque<Map<String, Cell>> redoStack = new ArrayDeque<>();

    public Simulation() {}

    private static String name(int col, int row) {
        return (char) ('A' + col) + String.valueOf(row);
    }

    private static int[] cellAt(String text) {
        if (text.length() < 2 || text.length() > 3 || text.charAt(0) < 'A' || text.charAt(0) > 'Z') {
            return null;
        }
        String digits = text.substring(1);
        if (!digits.chars().allMatch(Character::isDigit) || digits.charAt(0) == '0') {
            return null;
        }
        return new int[] {text.charAt(0) - 'A', Integer.parseInt(digits)};
    }

    private static List<Term> parse(String formula) {
        if (!formula.startsWith("=")) {
            return null;
        }
        List<Term> terms = new ArrayList<>();
        String s = formula.substring(1);
        int i = 0;
        int sign = 1;
        while (true) {
            int j = i;
            Term t = new Term();
            t.sign = sign;
            if (s.startsWith("SUM(", i)) {
                j = s.indexOf(')', i);
                if (j < 0) {
                    return null;
                }
                String[] parts = s.substring(i + 4, j).split(":", -1);
                int[] a = parts.length == 2 ? cellAt(parts[0]) : null;
                int[] b = parts.length == 2 ? cellAt(parts[1]) : null;
                if (a == null || b == null || a[0] > b[0] || a[1] > b[1]) {
                    return null;
                }
                t.kind = 2;
                t.col = a[0];
                t.row = a[1];
                t.col2 = b[0];
                t.row2 = b[1];
                j += 1;
            } else {
                while (j < s.length() && Character.isLetterOrDigit(s.charAt(j))) {
                    j++;
                }
                String word = s.substring(i, j);
                if (word.isEmpty()) {
                    return null;
                }
                if (word.chars().allMatch(Character::isDigit)) {
                    if (word.length() > 6) {
                        return null;
                    }
                    t.kind = 0;
                    t.number = Integer.parseInt(word);
                } else {
                    int[] c = cellAt(word);
                    if (c == null) {
                        return null;
                    }
                    t.kind = 1;
                    t.col = c[0];
                    t.row = c[1];
                }
            }
            terms.add(t);
            if (j == s.length()) {
                return terms;
            }
            char op = s.charAt(j);
            if (op != '+' && op != '-') {
                return null;
            }
            sign = op == '+' ? 1 : -1;
            i = j + 1;
        }
    }

    private static String render(List<Term> terms) {
        StringBuilder out = new StringBuilder("=");
        for (int k = 0; k < terms.size(); k++) {
            Term t = terms.get(k);
            if (k > 0) {
                out.append(t.sign > 0 ? '+' : '-');
            }
            if (t.kind == 0) {
                out.append(t.number);
            } else if (t.kind == 1) {
                out.append(name(t.col, t.row));
            } else {
                out.append("SUM(").append(name(t.col, t.row)).append(':').append(name(t.col2, t.row2)).append(')');
            }
        }
        return out.toString();
    }

    private static Set<String> refs(List<Term> terms) {
        Set<String> out = new HashSet<>();
        for (Term t : terms) {
            if (t.kind == 1) {
                out.add(name(t.col, t.row));
            } else if (t.kind == 2) {
                for (int c = t.col; c <= t.col2; c++) {
                    for (int r = t.row; r <= t.row2; r++) {
                        out.add(name(c, r));
                    }
                }
            }
        }
        return out;
    }

    private int value(String cell) {
        Cell c = cells.get(cell);
        if (c == null) {
            return 0;
        }
        if (c.terms == null) {
            return c.value;
        }
        int total = 0;
        for (Term t : c.terms) {
            int v;
            if (t.kind == 0) {
                v = t.number;
            } else if (t.kind == 1) {
                v = value(name(t.col, t.row));
            } else {
                v = rangeSum(t.col, t.row, t.col2, t.row2);
            }
            total += t.sign * v;
        }
        return total;
    }

    private int rangeSum(int c1, int r1, int c2, int r2) {
        int total = 0;
        for (int c = c1; c <= c2; c++) {
            for (int r = r1; r <= r2; r++) {
                total += value(name(c, r));
            }
        }
        return total;
    }

    private boolean reaches(String from, String target, Set<String> seen) {
        if (from.equals(target)) {
            return true;
        }
        Cell c = cells.get(from);
        if (c == null || c.terms == null || !seen.add(from)) {
            return false;
        }
        for (String next : refs(c.terms)) {
            if (reaches(next, target, seen)) {
                return true;
            }
        }
        return false;
    }

    private boolean createsCycle(String cell, List<Term> terms) {
        for (String ref : refs(terms)) {
            if (reaches(ref, cell, new HashSet<>())) {
                return true;
            }
        }
        return false;
    }

    private void save() {
        undoStack.push(new HashMap<>(cells));
        redoStack.clear();
    }

    private static List<Term> shifted(List<Term> terms, int dc, int dr) {
        List<Term> out = new ArrayList<>();
        for (Term t : terms) {
            Term n = new Term();
            n.sign = t.sign;
            n.kind = t.kind;
            n.number = t.number;
            n.col = t.col + dc;
            n.row = t.row + dr;
            n.col2 = t.col2 + dc;
            n.row2 = t.row2 + dr;
            if (t.kind != 0 && !inside(n.col, n.row)) {
                return null;
            }
            if (t.kind == 2 && !inside(n.col2, n.row2)) {
                return null;
            }
            out.add(n);
        }
        return out;
    }

    private static boolean inside(int col, int row) {
        return col >= 0 && col < 26 && row >= 1 && row <= 99;
    }

    public Integer setValue(String cell, int value) {
        Integer before = cells.containsKey(cell) ? value(cell) : null;
        save();
        cells.put(cell, new Cell(value, null));
        return before;
    }

    public int getValue(String cell) {
        return value(cell);
    }

    public boolean clear(String cell) {
        if (!cells.containsKey(cell)) {
            return false;
        }
        save();
        cells.remove(cell);
        return true;
    }

    public Integer sumRange(String from, String to) {
        int[] a = cellAt(from);
        int[] b = cellAt(to);
        if (a[0] > b[0] || a[1] > b[1]) {
            return null;
        }
        return rangeSum(a[0], a[1], b[0], b[1]);
    }

    public Integer setFormula(String cell, String formula) {
        List<Term> terms = parse(formula);
        if (terms == null || createsCycle(cell, terms)) {
            return null;
        }
        save();
        cells.put(cell, new Cell(null, terms));
        return value(cell);
    }

    public String getFormula(String cell) {
        Cell c = cells.get(cell);
        return c == null || c.terms == null ? null : render(c.terms);
    }

    public List<String> dependents(String cell) {
        List<int[]> found = new ArrayList<>();
        for (String other : cells.keySet()) {
            Cell c = cells.get(other);
            if (!other.equals(cell) && c.terms != null && reaches(other, cell, new HashSet<>())) {
                found.add(cellAt(other));
            }
        }
        found.sort((x, y) -> x[0] != y[0] ? x[0] - y[0] : x[1] - y[1]);
        List<String> out = new ArrayList<>();
        for (int[] f : found) {
            out.add(name(f[0], f[1]));
        }
        return out;
    }

    public Integer copy(String fromCell, String toCell) {
        Cell src = cells.get(fromCell);
        int[] a = cellAt(fromCell);
        int[] b = cellAt(toCell);
        Cell made = null;
        if (src != null && src.terms != null) {
            List<Term> moved = shifted(src.terms, b[0] - a[0], b[1] - a[1]);
            if (moved == null || createsCycle(toCell, moved)) {
                return null;
            }
            made = new Cell(null, moved);
        } else if (src != null) {
            made = new Cell(src.value, null);
        }
        save();
        if (made == null) {
            cells.remove(toCell);
        } else {
            cells.put(toCell, made);
        }
        return value(toCell);
    }

    public boolean insertRow(int row) {
        if (row < 1 || row > 99) {
            return false;
        }
        Map<String, Cell> next = new HashMap<>();
        for (Map.Entry<String, Cell> e : cells.entrySet()) {
            int[] at = cellAt(e.getKey());
            Cell c = e.getValue();
            if (at[1] >= row && at[1] == 99) {
                return false;
            }
            Cell moved = c;
            if (c.terms != null) {
                List<Term> terms = new ArrayList<>();
                for (Term t : c.terms) {
                    Term n = new Term();
                    n.sign = t.sign;
                    n.kind = t.kind;
                    n.number = t.number;
                    n.col = t.col;
                    n.col2 = t.col2;
                    n.row = t.kind != 0 && t.row >= row ? t.row + 1 : t.row;
                    n.row2 = t.kind == 2 && t.row2 >= row ? t.row2 + 1 : t.row2;
                    if (n.row > 99 || n.row2 > 99) {
                        return false;
                    }
                    terms.add(n);
                }
                moved = new Cell(null, terms);
            }
            next.put(name(at[0], at[1] >= row ? at[1] + 1 : at[1]), moved);
        }
        save();
        cells = next;
        return true;
    }

    public boolean undo() {
        if (undoStack.isEmpty()) {
            return false;
        }
        redoStack.push(cells);
        cells = undoStack.pop();
        return true;
    }

    public boolean redo() {
        if (redoStack.isEmpty()) {
            return false;
        }
        undoStack.push(cells);
        cells = redoStack.pop();
        return true;
    }
}
