import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

class Entry {
    String key;
    String value;
    int size;
    Integer expiresAt;
    boolean pinned;
    int lastUse;
}

public class Simulation {
    private final Map<String, Entry> hot = new HashMap<>();
    private final Map<String, Entry> cold = new HashMap<>();
    private int capacity = 100;
    private int coldCapacity = 0;
    private int clock = 0;
    private int hits = 0;
    private int coldHits = 0;
    private int misses = 0;

    public Simulation() {}

    private void expire(int timestamp) {
        for (Map<String, Entry> tier : List.of(hot, cold)) {
            tier.values().removeIf(e -> e.expiresAt != null && timestamp >= e.expiresAt);
        }
    }

    private int used(Map<String, Entry> tier) {
        int total = 0;
        for (Entry e : tier.values()) {
            total += e.size;
        }
        return total;
    }

    private int pinnedExcept(String key) {
        int total = 0;
        for (Entry e : hot.values()) {
            if (e.pinned && !e.key.equals(key)) {
                total += e.size;
            }
        }
        return total;
    }

    private Entry oldest(Map<String, Entry> tier, String skip, boolean skipPinned) {
        Entry best = null;
        for (Entry e : tier.values()) {
            if (e.key.equals(skip) || (skipPinned && e.pinned)) {
                continue;
            }
            if (best == null || e.lastUse < best.lastUse) {
                best = e;
            }
        }
        return best;
    }

    private void toCold(Entry e) {
        if (e.size > coldCapacity) {
            return;
        }
        e.pinned = false;
        clock += 1;
        e.lastUse = clock;
        cold.put(e.key, e);
        while (used(cold) > coldCapacity) {
            cold.remove(oldest(cold, e.key, false).key);
        }
    }

    private List<String> evictHot(String keep) {
        List<String> evicted = new ArrayList<>();
        while (used(hot) > capacity) {
            Entry victim = oldest(hot, keep, true);
            if (victim == null) {
                break;
            }
            hot.remove(victim.key);
            evicted.add(victim.key);
            toCold(victim);
        }
        return evicted;
    }

    private List<String> byRecency(Map<String, Entry> tier) {
        List<Entry> all = new ArrayList<>(tier.values());
        all.sort((a, b) -> Integer.compare(b.lastUse, a.lastUse));
        List<String> out = new ArrayList<>();
        for (Entry e : all) {
            out.add(e.key);
        }
        return out;
    }

    private List<String> store(int timestamp, String key, String value, int size, Integer expiresAt) {
        expire(timestamp);
        if (size <= 0 || size + pinnedExcept(key) > capacity) {
            return null;
        }
        Entry e = hot.get(key);
        if (e == null) {
            e = new Entry();
            e.key = key;
        }
        cold.remove(key);
        e.value = value;
        e.size = size;
        e.expiresAt = expiresAt;
        clock += 1;
        e.lastUse = clock;
        hot.put(key, e);
        return evictHot(key);
    }

    public List<String> put(int timestamp, String key, String value, int size) {
        return store(timestamp, key, value, size, null);
    }

    public String get(int timestamp, String key) {
        expire(timestamp);
        Entry e = hot.get(key);
        if (e != null) {
            hits += 1;
            clock += 1;
            e.lastUse = clock;
            return e.value;
        }
        e = cold.get(key);
        if (e == null) {
            misses += 1;
            return null;
        }
        coldHits += 1;
        clock += 1;
        e.lastUse = clock;
        if (e.size + pinnedExcept(key) <= capacity) {
            cold.remove(key);
            hot.put(key, e);
            evictHot(key);
        }
        return e.value;
    }

    public boolean delete(int timestamp, String key) {
        expire(timestamp);
        return hot.remove(key) != null || cold.remove(key) != null;
    }

    public int usedBytes(int timestamp) {
        expire(timestamp);
        return used(hot);
    }

    public List<String> putWithTtl(int timestamp, String key, String value, int size, int ttl) {
        if (ttl <= 0) {
            return null;
        }
        return store(timestamp, key, value, size, timestamp + ttl);
    }

    public Integer ttlLeft(int timestamp, String key) {
        expire(timestamp);
        Entry e = hot.containsKey(key) ? hot.get(key) : cold.get(key);
        if (e == null) {
            return null;
        }
        return e.expiresAt == null ? -1 : e.expiresAt - timestamp;
    }

    public List<String> keys(int timestamp) {
        expire(timestamp);
        return byRecency(hot);
    }

    public boolean pin(int timestamp, String key) {
        expire(timestamp);
        Entry e = hot.get(key);
        if (e == null || e.pinned) {
            return false;
        }
        e.pinned = true;
        return true;
    }

    public boolean unpin(int timestamp, String key) {
        expire(timestamp);
        Entry e = hot.get(key);
        if (e == null || !e.pinned) {
            return false;
        }
        e.pinned = false;
        return true;
    }

    public List<String> setCapacity(int timestamp, int newCapacity) {
        expire(timestamp);
        if (newCapacity <= 0) {
            return null;
        }
        capacity = newCapacity;
        return evictHot(null);
    }

    public boolean setColdCapacity(int timestamp, int newCapacity) {
        expire(timestamp);
        if (newCapacity < 0) {
            return false;
        }
        coldCapacity = newCapacity;
        while (used(cold) > coldCapacity) {
            cold.remove(oldest(cold, null, false).key);
        }
        return true;
    }

    public List<String> coldKeys(int timestamp) {
        expire(timestamp);
        return byRecency(cold);
    }

    public String stats(int timestamp) {
        expire(timestamp);
        return "hits=" + hits + ",cold_hits=" + coldHits + ",misses=" + misses;
    }
}
