import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.TreeMap;

class Job {
    String id;
    int duration;
    int priority = 0;
    int attempts = 0;
    String state = "pending";
    int endsAt;
    Integer finishedAt = null;
    Set<String> deps = new LinkedHashSet<>();
}

public class Simulation {
    private final Map<String, Job> jobs = new TreeMap<>();
    private int workers = 1;
    private int now = 0;

    public Simulation() {}

    private boolean isReady(Job job) {
        if (!"pending".equals(job.state)) {
            return false;
        }
        for (String dep : job.deps) {
            if (!"done".equals(jobs.get(dep).state)) {
                return false;
            }
        }
        return true;
    }

    private boolean reaches(String from, String target) {
        if (from.equals(target)) {
            return true;
        }
        for (String dep : jobs.get(from).deps) {
            if (reaches(dep, target)) {
                return true;
            }
        }
        return false;
    }

    private int running() {
        int count = 0;
        for (Job job : jobs.values()) {
            if ("running".equals(job.state)) {
                count += 1;
            }
        }
        return count;
    }

    private void step(int t, List<String> finished) {
        for (Job job : jobs.values()) {
            if ("running".equals(job.state) && job.endsAt == t) {
                job.state = "done";
                job.finishedAt = t;
                finished.add(job.id);
            }
        }
        List<Job> ready = new ArrayList<>();
        for (Job job : jobs.values()) {
            if (isReady(job)) {
                ready.add(job);
            }
        }
        ready.sort((a, b) -> a.priority != b.priority ? b.priority - a.priority : a.id.compareTo(b.id));
        int idle = workers - running();
        for (int i = 0; i < ready.size() && i < idle; i++) {
            ready.get(i).state = "running";
            ready.get(i).endsAt = t + ready.get(i).duration;
        }
    }

    private List<String> blockDependents(String root) {
        List<String> blocked = new ArrayList<>();
        boolean changed = true;
        Set<String> dead = new LinkedHashSet<>();
        dead.add(root);
        while (changed) {
            changed = false;
            for (Job job : jobs.values()) {
                if (!"pending".equals(job.state)) {
                    continue;
                }
                for (String dep : job.deps) {
                    if (dead.contains(dep)) {
                        job.state = "blocked";
                        dead.add(job.id);
                        blocked.add(job.id);
                        changed = true;
                        break;
                    }
                }
            }
        }
        blocked.sort(null);
        return blocked;
    }

    public boolean addJob(String jobId, int duration) {
        if (jobs.containsKey(jobId) || duration <= 0) {
            return false;
        }
        Job job = new Job();
        job.id = jobId;
        job.duration = duration;
        jobs.put(jobId, job);
        return true;
    }

    public boolean addDependency(String jobId, String dependsOn) {
        Job job = jobs.get(jobId);
        Job dep = jobs.get(dependsOn);
        if (job == null || dep == null || !"pending".equals(job.state) || job.deps.contains(dependsOn)) {
            return false;
        }
        String s = dep.state;
        if ("failed".equals(s) || "aborted".equals(s) || "blocked".equals(s) || reaches(dependsOn, jobId)) {
            return false;
        }
        job.deps.add(dependsOn);
        return true;
    }

    public boolean complete(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null || !isReady(job)) {
            return false;
        }
        job.state = "done";
        job.finishedAt = now;
        return true;
    }

    public List<String> readyJobs() {
        List<String> out = new ArrayList<>();
        for (Job job : jobs.values()) {
            if (isReady(job)) {
                out.add(job.id);
            }
        }
        return out;
    }

    public boolean setWorkers(int count) {
        if (count < 1) {
            return false;
        }
        workers = count;
        return true;
    }

    public List<String> runUntil(int timestamp) {
        if (timestamp < now) {
            return null;
        }
        List<String> finished = new ArrayList<>();
        step(now, finished);
        while (true) {
            Integer next = null;
            for (Job job : jobs.values()) {
                if ("running".equals(job.state) && (next == null || job.endsAt < next)) {
                    next = job.endsAt;
                }
            }
            if (next == null || next > timestamp) {
                break;
            }
            now = next;
            step(now, finished);
        }
        now = timestamp;
        return finished;
    }

    public String status(String jobId) {
        Job job = jobs.get(jobId);
        return job == null ? null : job.state;
    }

    public boolean setPriority(String jobId, int priority) {
        Job job = jobs.get(jobId);
        if (job == null || !"pending".equals(job.state)) {
            return false;
        }
        job.priority = priority;
        return true;
    }

    public String fail(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null || !"running".equals(job.state)) {
            return null;
        }
        job.attempts += 1;
        if (job.attempts >= 3) {
            job.state = "failed";
            blockDependents(jobId);
            return "failed";
        }
        job.state = "pending";
        return "retry";
    }

    public int criticalPath() {
        Map<String, Integer> memo = new HashMap<>();
        int best = 0;
        for (String id : jobs.keySet()) {
            best = Math.max(best, longest(id, memo));
        }
        return best;
    }

    private int longest(String id, Map<String, Integer> memo) {
        Integer known = memo.get(id);
        if (known != null) {
            return known;
        }
        int deepest = 0;
        for (String dep : jobs.get(id).deps) {
            deepest = Math.max(deepest, longest(dep, memo));
        }
        int value = deepest + jobs.get(id).duration;
        memo.put(id, value);
        return value;
    }

    public List<String> abort(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null || !("pending".equals(job.state) || "running".equals(job.state))) {
            return null;
        }
        job.state = "aborted";
        return blockDependents(jobId);
    }

    public Integer finishedAt(String jobId) {
        Job job = jobs.get(jobId);
        if (job == null || !"done".equals(job.state)) {
            return null;
        }
        return job.finishedAt;
    }
}
