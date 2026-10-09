import java.util.List;

public class Simulation {
    public Simulation() {}

    /** Store a value. Returns the previous value, or null. */
    public String set(int timestamp, String key, String value) {
        return null;
    }

    /** The value, or null. */
    public String get(int timestamp, String key) {
        return null;
    }

    /** True if the key existed and is now gone. */
    public boolean delete(int timestamp, String key) {
        return false;
    }

    /** Store value only if the key exists and equals expected. */
    public boolean compareAndSet(int timestamp, String key, String expected, String value) {
        return false;
    }

    /** {@code key=value} for keys with the prefix, sorted by key. */
    public List<String> scanPrefix(int timestamp, String prefix) {
        return null;
    }

    /** Number of keys. */
    public Integer size(int timestamp) {
        return null;
    }

    /**
     * Store a value live in {@code [timestamp, timestamp + ttl)}. Returns the
     * previous live value, or null.
     */
    public String setWithTtl(int timestamp, String key, String value, int ttl) {
        return null;
    }

    /** Time left, -1 for no TTL, or null if missing or expired. */
    public Integer ttlRemaining(int timestamp, String key) {
        return null;
    }

    /** Open a transaction. Returns the new depth. */
    public Integer begin(int timestamp) {
        return null;
    }

    /** Merge the innermost transaction into its parent. */
    public boolean commit(int timestamp) {
        return false;
    }

    /** Discard the innermost transaction. */
    public boolean rollback(int timestamp) {
        return false;
    }

    /** Save live keys with remaining TTL. Count saved, or null in a transaction. */
    public Integer backup(int timestamp) {
        return null;
    }

    /**
     * Replace the store with the latest backup at or before
     * {@code timeToRestore}. TTLs count from {@code timestamp}.
     */
    public boolean restore(int timestamp, int timeToRestore) {
        return false;
    }
}
