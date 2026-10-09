import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.TreeMap;
import java.util.TreeSet;

public class Simulation {
    private static final String GONE = "\u0000deleted";
    private final List<Map<String, String>> versions = new ArrayList<>();
    private final List<Map<String, String>> layers = new ArrayList<>();

    public Simulation() {
        versions.add(new HashMap<>());
    }

    private Map<String, String> base() {
        return versions.get(versions.size() - 1);
    }

    private String visible(String key) {
        for (int i = layers.size() - 1; i >= 0; i--) {
            String v = layers.get(i).get(key);
            if (v != null) {
                return GONE.equals(v) ? null : v;
            }
        }
        return base().get(key);
    }

    private Map<String, String> view() {
        Map<String, String> out = new TreeMap<>(base());
        for (Map<String, String> layer : layers) {
            for (Map.Entry<String, String> e : layer.entrySet()) {
                if (GONE.equals(e.getValue())) {
                    out.remove(e.getKey());
                } else {
                    out.put(e.getKey(), e.getValue());
                }
            }
        }
        return out;
    }

    private void write(String key, String value) {
        if (!layers.isEmpty()) {
            layers.get(layers.size() - 1).put(key, value == null ? GONE : value);
            return;
        }
        Map<String, String> next = new HashMap<>(base());
        if (value == null) {
            next.remove(key);
        } else {
            next.put(key, value);
        }
        if (!next.equals(base())) {
            versions.add(next);
        }
    }

    public String set(String key, String value) {
        String before = visible(key);
        write(key, value);
        return before;
    }

    public String get(String key) {
        return visible(key);
    }

    public boolean delete(String key) {
        if (visible(key) == null) {
            return false;
        }
        write(key, null);
        return true;
    }

    public int count(String value) {
        int n = 0;
        for (String v : view().values()) {
            if (v.equals(value)) {
                n += 1;
            }
        }
        return n;
    }

    public int begin() {
        layers.add(new HashMap<>());
        return layers.size();
    }

    public boolean commit() {
        if (layers.isEmpty()) {
            return false;
        }
        Map<String, String> top = layers.remove(layers.size() - 1);
        if (!layers.isEmpty()) {
            layers.get(layers.size() - 1).putAll(top);
            return true;
        }
        Map<String, String> next = new HashMap<>(base());
        for (Map.Entry<String, String> e : top.entrySet()) {
            if (GONE.equals(e.getValue())) {
                next.remove(e.getKey());
            } else {
                next.put(e.getKey(), e.getValue());
            }
        }
        if (!next.equals(base())) {
            versions.add(next);
        }
        return true;
    }

    public boolean rollback() {
        if (layers.isEmpty()) {
            return false;
        }
        layers.remove(layers.size() - 1);
        return true;
    }

    public boolean compareAndSet(String key, String expected, String newValue) {
        String current = visible(key);
        if (current == null || !current.equals(expected)) {
            return false;
        }
        write(key, newValue);
        return true;
    }

    public Integer increment(String key, int delta) {
        String current = visible(key);
        int number = 0;
        if (current != null) {
            if (!current.matches("-?[0-9]{1,9}")) {
                return null;
            }
            number = Integer.parseInt(current);
        }
        long result = (long) number + delta;
        if (result > 999999999L || result < -999999999L) {
            return null;
        }
        write(key, String.valueOf(result));
        return (int) result;
    }

    public Integer revert(int toVersion) {
        if (!layers.isEmpty() || toVersion < 0 || toVersion >= versions.size()) {
            return null;
        }
        Map<String, String> target = versions.get(toVersion);
        if (target.equals(base())) {
            return null;
        }
        versions.add(new HashMap<>(target));
        return versions.size() - 1;
    }

    public int version() {
        return versions.size() - 1;
    }

    public String getAt(String key, int version) {
        if (version < 0 || version >= versions.size()) {
            return null;
        }
        return versions.get(version).get(key);
    }

    public List<String> scan(String prefix) {
        List<String> out = new ArrayList<>();
        for (Map.Entry<String, String> e : view().entrySet()) {
            if (e.getKey().startsWith(prefix)) {
                out.add(e.getKey() + "=" + e.getValue());
            }
        }
        return out;
    }

    public List<String> history(String key) {
        List<String> out = new ArrayList<>();
        for (int v = 1; v < versions.size(); v++) {
            String before = versions.get(v - 1).get(key);
            String after = versions.get(v).get(key);
            if (!Objects.equals(before, after)) {
                out.add(v + ":" + (after == null ? "(none)" : after));
            }
        }
        return out;
    }

    public List<String> diff(int fromVersion, int toVersion) {
        if (fromVersion < 0 || toVersion < 0 || fromVersion >= versions.size() || toVersion >= versions.size()) {
            return null;
        }
        Map<String, String> a = versions.get(fromVersion);
        Map<String, String> b = versions.get(toVersion);
        TreeSet<String> keys = new TreeSet<>(a.keySet());
        keys.addAll(b.keySet());
        List<String> out = new ArrayList<>();
        for (String key : keys) {
            String x = a.get(key);
            String y = b.get(key);
            if (!Objects.equals(x, y)) {
                out.add(key + ":" + (x == null ? "(none)" : x) + "->" + (y == null ? "(none)" : y));
            }
        }
        return out;
    }
}
