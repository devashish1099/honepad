import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Store a value. Returns the previous value, or null.
     */
    public String set(String key, String value) {
        return null;
    }

    /**
     * The current value, or null.
     */
    public String get(String key) {
        return null;
    }

    /**
     * Remove a key. Returns true if it existed.
     */
    public boolean delete(String key) {
        return false;
    }

    /**
     * How many keys hold exactly this value.
     */
    public int count(String value) {
        return 0;
    }

    /**
     * Start a transaction. Returns the new nesting depth.
     */
    public int begin() {
        return 0;
    }

    /**
     * Keep the innermost transaction's changes. Returns true if there was
     * one.
     */
    public boolean commit() {
        return false;
    }

    /**
     * Discard the innermost transaction's changes. Returns true if there
     * was one.
     */
    public boolean rollback() {
        return false;
    }

    /**
     * Set only if the key currently holds {@code expected}. Returns true
     * if set.
     */
    public boolean compareAndSet(String key, String expected, String newValue) {
        return false;
    }

    /**
     * The number of the latest committed version.
     */
    public int version() {
        return 0;
    }

    /**
     * A key's value in a committed version, or null.
     */
    public String getAt(String key, int version) {
        return null;
    }

    /**
     * Current keys starting with {@code prefix}, sorted, as
     * {@code "key=value"}.
     */
    public List<String> scan(String prefix) {
        return null;
    }

    /**
     * Add {@code delta} to a numeric value. Returns the new value, or
     * null.
     */
    public Integer increment(String key, int delta) {
        return null;
    }

    /**
     * Versions where the key changed, as {@code "version:value"}.
     */
    public List<String> history(String key) {
        return null;
    }

    /**
     * Keys that differ between two versions, or null.
     */
    public List<String> diff(int fromVersion, int toVersion) {
        return null;
    }

    /**
     * Make an old version current again. Returns the new version number,
     * or null.
     */
    public Integer revert(int toVersion) {
        return null;
    }
}
