import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Put a number in a cell. Returns the cell's previous value, or null
     * if it was empty.
     */
    public Integer setValue(String cell, int value) {
        return null;
    }

    /**
     * A cell's value. Empty cells are 0.
     */
    public int getValue(String cell) {
        return 0;
    }

    /**
     * Empty a cell. Returns true if it had content.
     */
    public boolean clear(String cell) {
        return false;
    }

    /**
     * Sum of the rectangle from one corner to the other, or null.
     */
    public Integer sumRange(String from, String to) {
        return null;
    }

    /**
     * Put a formula in a cell. Returns its value, or null if the formula
     * is invalid or would create a cycle.
     */
    public Integer setFormula(String cell, String formula) {
        return null;
    }

    /**
     * The cell's formula text, or null if it holds none.
     */
    public String getFormula(String cell) {
        return null;
    }

    /**
     * Cells whose value depends on this cell.
     */
    public List<String> dependents(String cell) {
        return null;
    }

    /**
     * Copy a cell, shifting formula references. Returns the new value of
     * the target, or null.
     */
    public Integer copy(String fromCell, String toCell) {
        return null;
    }

    /**
     * Insert an empty row, moving rows down. Returns true if done.
     */
    public boolean insertRow(int row) {
        return false;
    }

    /**
     * Undo the last change. Returns true if there was one.
     */
    public boolean undo() {
        return false;
    }

    /**
     * Redo the last undone change. Returns true if there was one.
     */
    public boolean redo() {
        return false;
    }
}
