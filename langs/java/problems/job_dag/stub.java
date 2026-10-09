import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Add a job that takes {@code duration} time units. Returns true if
     * added.
     */
    public boolean addJob(String jobId, int duration) {
        return false;
    }

    /**
     * {@code jobId} may only start after {@code dependsOn} is done.
     * Returns true if the dependency was added.
     */
    public boolean addDependency(String jobId, String dependsOn) {
        return false;
    }

    /**
     * Mark a ready job done. Returns true if it was ready.
     */
    public boolean complete(String jobId) {
        return false;
    }

    /**
     * Jobs that could start now, sorted by id.
     */
    public List<String> readyJobs() {
        return null;
    }

    /**
     * Set how many jobs can run at once. Returns true if valid.
     */
    public boolean setWorkers(int count) {
        return false;
    }

    /**
     * Run the schedule up to {@code timestamp}. Returns the jobs that
     * finished, in finish order, or null if time would go back.
     */
    public List<String> runUntil(int timestamp) {
        return null;
    }

    /**
     * pending, running, done, failed, blocked, aborted, or null.
     */
    public String status(String jobId) {
        return null;
    }

    /**
     * Set a pending job's priority. Returns true if set.
     */
    public boolean setPriority(String jobId, int priority) {
        return false;
    }

    /**
     * Report a running job's failure. {@code "retry"}, {@code "failed"},
     * or null if it was not running.
     */
    public String fail(String jobId) {
        return null;
    }

    /**
     * Longest total duration along any chain of dependencies.
     */
    public int criticalPath() {
        return 0;
    }

    /**
     * Stop a pending or running job. Returns the jobs newly blocked, or
     * null if it could not be aborted.
     */
    public List<String> abort(String jobId) {
        return null;
    }

    /**
     * When a done job finished, or null.
     */
    public Integer finishedAt(String jobId) {
        return null;
    }
}
