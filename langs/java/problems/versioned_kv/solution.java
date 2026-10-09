import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

/** One stored value. A null value marks a delete inside a transaction. */
class Entry {
    final String value;
    final Integer expiresAt;

    Entry(String value, Integer expiresAt) {
        this.value = value;
        this.expiresAt = expiresAt;
    }

    boolean isTombstone() {
        return value == null;
    }

    boolean liveAt(int t) {
        return !isTombstone() && (expiresAt == null || t < expiresAt);
    }
}

class Backup {
    final int takenAt;
    /** key -> {value, remaining ttl or null}. */
    final Map<String, Object[]> rows;

    Backup(int takenAt, Map<String, Object[]> rows) {
        this.takenAt = takenAt;
        this.rows = rows;
    }
}

public class Simulation {
    private static final Entry TOMBSTONE = new Entry(null, null);

    private final List<Map<String, Entry>> layers = new ArrayList<>();
    private final List<Backup> backups = new ArrayList<>();

    public Simulation() {
        layers.add(new HashMap<>());
    }

    public String set(int timestamp, String key, String value) {
        return put(timestamp, key, new Entry(value, null));
    }

    public String get(int timestamp, String key) {
        Entry e = live(key, timestamp);
        return e == null ? null : e.value;
    }

    public boolean delete(int timestamp, String key) {
        if (live(key, timestamp) == null) {
            return false;
        }
        write(key, TOMBSTONE);
        return true;
    }

    public boolean compareAndSet(int timestamp, String key, String expected, String value) {
        Entry e = live(key, timestamp);
        if (e == null || !e.value.equals(expected)) {
            return false;
        }
        write(key, new Entry(value, e.expiresAt));
        return true;
    }

    public List<String> scanPrefix(int timestamp, String prefix) {
        List<String> out = new ArrayList<>();
        for (Map.Entry<String, Entry> e : view(timestamp).entrySet()) {
            if (e.getKey().startsWith(prefix)) {
                out.add(e.getKey() + "=" + e.getValue().value);
            }
        }
        return out;
    }

    public Integer size(int timestamp) {
        return view(timestamp).size();
    }

    public String setWithTtl(int timestamp, String key, String value, int ttl) {
        return put(timestamp, key, new Entry(value, timestamp + ttl));
    }

    public Integer ttlRemaining(int timestamp, String key) {
        Entry e = live(key, timestamp);
        if (e == null) {
            return null;
        }
        return e.expiresAt == null ? -1 : e.expiresAt - timestamp;
    }

    public Integer begin(int timestamp) {
        layers.add(new HashMap<>());
        return layers.size() - 1;
    }

    public boolean commit(int timestamp) {
        if (layers.size() == 1) {
            return false;
        }
        Map<String, Entry> top = layers.remove(layers.size() - 1);
        for (Map.Entry<String, Entry> e : top.entrySet()) {
            write(e.getKey(), e.getValue());
        }
        return true;
    }

    public boolean rollback(int timestamp) {
        if (layers.size() == 1) {
            return false;
        }
        layers.remove(layers.size() - 1);
        return true;
    }

    public Integer backup(int timestamp) {
        if (layers.size() > 1) {
            return null;
        }
        Map<String, Object[]> rows = new HashMap<>();
        for (Map.Entry<String, Entry> e : view(timestamp).entrySet()) {
            Integer exp = e.getValue().expiresAt;
            rows.put(
                    e.getKey(),
                    new Object[] {e.getValue().value, exp == null ? null : exp - timestamp});
        }
        backups.add(new Backup(timestamp, rows));
        return rows.size();
    }

    public boolean restore(int timestamp, int timeToRestore) {
        if (layers.size() > 1) {
            return false;
        }
        Backup chosen = null;
        for (Backup b : backups) {
            if (b.takenAt <= timeToRestore) {
                chosen = b;
            }
        }
        if (chosen == null) {
            return false;
        }
        Map<String, Entry> base = new HashMap<>();
        for (Map.Entry<String, Object[]> e : chosen.rows.entrySet()) {
            Integer left = (Integer) e.getValue()[1];
            base.put(
                    e.getKey(),
                    new Entry((String) e.getValue()[0], left == null ? null : timestamp + left));
        }
        layers.clear();
        layers.add(base);
        return true;
    }

    private String put(int timestamp, String key, Entry entry) {
        Entry old = live(key, timestamp);
        write(key, entry);
        return old == null ? null : old.value;
    }

    /** The innermost stored entry for key, if it is live at t. */
    private Entry live(String key, int t) {
        for (int i = layers.size() - 1; i >= 0; i--) {
            Entry e = layers.get(i).get(key);
            if (e != null) {
                return e.liveAt(t) ? e : null;
            }
        }
        return null;
    }

    private void write(String key, Entry entry) {
        Map<String, Entry> top = layers.get(layers.size() - 1);
        if (entry.isTombstone() && layers.size() == 1) {
            top.remove(key);
        } else {
            top.put(key, entry);
        }
    }

    private TreeMap<String, Entry> view(int t) {
        Map<String, Entry> merged = new HashMap<>();
        for (Map<String, Entry> layer : layers) {
            merged.putAll(layer);
        }
        TreeMap<String, Entry> out = new TreeMap<>();
        for (Map.Entry<String, Entry> e : merged.entrySet()) {
            if (e.getValue().liveAt(t)) {
                out.put(e.getKey(), e.getValue());
            }
        }
        return out;
    }
}
