import java.util.List;

public class Simulation {
    public Simulation() {}

    /** Add a task. Returns false if the id exists. */
    public boolean addTask(int timestamp, String taskId, int priority) {
        return false;
    }

    /** Set a new priority. Returns false if the task is missing. */
    public boolean updateTask(int timestamp, String taskId, int priority) {
        return false;
    }

    /** The task's priority, or null if missing. */
    public Integer getTask(int timestamp, String taskId) {
        return null;
    }

    /** Delete a task. Returns false if missing. */
    public boolean removeTask(int timestamp, String taskId) {
        return false;
    }

    /**
     * At most n {@code id(priority)} for ids starting with prefix, priority
     * high to low, then id. Example: {@code ["bug-2(9)", "bug-1(5)"]}.
     */
    public List<String> search(int timestamp, String prefix, int n) {
        return null;
    }

    /** Add a user. False if the id exists or quota is not positive. */
    public boolean addUser(int timestamp, String userId, int quota) {
        return false;
    }

    /**
     * Assign for {@code [timestamp, timestamp + ttl)}. False if missing, ttl
     * not positive, the task is live, or the user is at quota.
     */
    public boolean assign(int timestamp, String taskId, String userId, int ttl) {
        return false;
    }

    /** The user's live tasks, sorted like search. Null if the user is missing. */
    public List<String> getUserTasks(int timestamp, String userId) {
        return null;
    }

    /** Finish a task live for this user. The task is removed. */
    public boolean complete(int timestamp, String taskId, String userId) {
        return false;
    }

    /**
     * Ended, not completed assignments as {@code taskId(userId)}, by end time
     * then id.
     */
    public List<String> overdue(int timestamp) {
        return null;
    }

    /** At most n {@code userId(count)}, count high to low, then id. */
    public List<String> topCompleters(int timestamp, int n) {
        return null;
    }
}
