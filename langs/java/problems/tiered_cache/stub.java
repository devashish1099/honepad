import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Store a value of {@code size} bytes. Returns the keys evicted to
     * make room, oldest use first, or null if it cannot be stored.
     */
    public List<String> put(int timestamp, String key, String value, int size) {
        return null;
    }

    /**
     * The stored value, or null. Counts as a use.
     */
    public String get(int timestamp, String key) {
        return null;
    }

    /**
     * Remove a key. Returns true if it was there.
     */
    public boolean delete(int timestamp, String key) {
        return false;
    }

    /**
     * Total size of the stored entries.
     */
    public int usedBytes(int timestamp) {
        return 0;
    }

    /**
     * Like put, but the entry disappears at {@code timestamp + ttl}.
     */
    public List<String> putWithTtl(int timestamp, String key, String value, int size, int ttl) {
        return null;
    }

    /**
     * Time until the key expires, -1 if it never does, null if absent.
     */
    public Integer ttlLeft(int timestamp, String key) {
        return null;
    }

    /**
     * Stored keys, most recently used first.
     */
    public List<String> keys(int timestamp) {
        return null;
    }

    /**
     * Protect a key from eviction. Returns true if it changed.
     */
    public boolean pin(int timestamp, String key) {
        return false;
    }

    /**
     * Remove protection. Returns true if it changed.
     */
    public boolean unpin(int timestamp, String key) {
        return false;
    }

    /**
     * Change the capacity. Returns the evicted keys, or null if invalid.
     */
    public List<String> setCapacity(int timestamp, int newCapacity) {
        return null;
    }

    /**
     * Change the cold tier's capacity. Returns true if valid.
     */
    public boolean setColdCapacity(int timestamp, int newCapacity) {
        return false;
    }

    /**
     * Keys in the cold tier, most recent first.
     */
    public List<String> coldKeys(int timestamp) {
        return null;
    }

    /**
     * {@code "hits=H,cold_hits=C,misses=M"} over all get calls.
     */
    public String stats(int timestamp) {
        return null;
    }
}
