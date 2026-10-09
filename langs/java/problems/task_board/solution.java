import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class Assignment {
    final String userId;
    final int expiresAt;

    Assignment(String userId, int expiresAt) {
        this.userId = userId;
        this.expiresAt = expiresAt;
    }

    boolean liveAt(int t) {
        return t < expiresAt;
    }
}

public class Simulation {
    private final Map<String, Integer> tasks = new HashMap<>();
    private final Map<String, Integer> quotas = new HashMap<>();
    private final Map<String, Integer> completed = new TreeMap<>();
    private final Map<String, Assignment> assigned = new HashMap<>();

    public Simulation() {}

    public boolean addTask(int timestamp, String taskId, int priority) {
        if (tasks.containsKey(taskId)) {
            return false;
        }
        tasks.put(taskId, priority);
        return true;
    }

    public boolean updateTask(int timestamp, String taskId, int priority) {
        if (!tasks.containsKey(taskId)) {
            return false;
        }
        tasks.put(taskId, priority);
        return true;
    }

    public Integer getTask(int timestamp, String taskId) {
        return tasks.get(taskId);
    }

    public boolean removeTask(int timestamp, String taskId) {
        if (tasks.remove(taskId) == null) {
            return false;
        }
        assigned.remove(taskId);
        return true;
    }

    public List<String> search(int timestamp, String prefix, int n) {
        List<String> ids = new ArrayList<>();
        for (String id : tasks.keySet()) {
            if (id.startsWith(prefix)) {
                ids.add(id);
            }
        }
        return format(ids, n);
    }

    public boolean addUser(int timestamp, String userId, int quota) {
        if (quotas.containsKey(userId) || quota <= 0) {
            return false;
        }
        quotas.put(userId, quota);
        completed.put(userId, 0);
        return true;
    }

    public boolean assign(int timestamp, String taskId, String userId, int ttl) {
        if (!tasks.containsKey(taskId) || !quotas.containsKey(userId) || ttl <= 0) {
            return false;
        }
        Assignment current = assigned.get(taskId);
        if (current != null && current.liveAt(timestamp)) {
            return false;
        }
        if (liveTasks(userId, timestamp).size() >= quotas.get(userId)) {
            return false;
        }
        assigned.put(taskId, new Assignment(userId, timestamp + ttl));
        return true;
    }

    public List<String> getUserTasks(int timestamp, String userId) {
        if (!quotas.containsKey(userId)) {
            return null;
        }
        return format(liveTasks(userId, timestamp), Integer.MAX_VALUE);
    }

    public boolean complete(int timestamp, String taskId, String userId) {
        Assignment a = assigned.get(taskId);
        if (a == null || !a.userId.equals(userId) || !a.liveAt(timestamp)) {
            return false;
        }
        tasks.remove(taskId);
        assigned.remove(taskId);
        completed.merge(userId, 1, Integer::sum);
        return true;
    }

    public List<String> overdue(int timestamp) {
        List<String> ids = new ArrayList<>();
        for (Map.Entry<String, Assignment> e : assigned.entrySet()) {
            if (!e.getValue().liveAt(timestamp)) {
                ids.add(e.getKey());
            }
        }
        ids.sort(
                Comparator.<String>comparingInt(id -> assigned.get(id).expiresAt)
                        .thenComparing(Comparator.naturalOrder()));
        List<String> out = new ArrayList<>();
        for (String id : ids) {
            out.add(id + "(" + assigned.get(id).userId + ")");
        }
        return out;
    }

    public List<String> topCompleters(int timestamp, int n) {
        List<String> users = new ArrayList<>(completed.keySet());
        users.sort(
                Comparator.<String>comparingInt(u -> -completed.get(u))
                        .thenComparing(Comparator.naturalOrder()));
        List<String> out = new ArrayList<>();
        for (String u : users.subList(0, Math.min(n, users.size()))) {
            out.add(u + "(" + completed.get(u) + ")");
        }
        return out;
    }

    private List<String> liveTasks(String userId, int timestamp) {
        List<String> ids = new ArrayList<>();
        for (Map.Entry<String, Assignment> e : assigned.entrySet()) {
            Assignment a = e.getValue();
            if (a.userId.equals(userId) && a.liveAt(timestamp)) {
                ids.add(e.getKey());
            }
        }
        return ids;
    }

    private List<String> format(List<String> ids, int n) {
        ids.sort(
                Comparator.<String>comparingInt(id -> -tasks.get(id))
                        .thenComparing(Comparator.naturalOrder()));
        List<String> out = new ArrayList<>();
        for (String id : ids.subList(0, Math.min(n, ids.size()))) {
            out.add(id + "(" + tasks.get(id) + ")");
        }
        return out;
    }
}
