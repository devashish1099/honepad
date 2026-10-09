import java.util.ArrayList;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.TreeMap;
import java.util.TreeSet;

class Commit {
    String id;
    int number;
    String message;
    Map<String, String> files;
    List<String> parents = new ArrayList<>();
}

public class Simulation {
    private final Map<String, Commit> commits = new HashMap<>();
    private final Map<String, String> branches = new HashMap<>();
    private TreeMap<String, String> work = new TreeMap<>();
    private String current = "main";
    private int counter = 0;

    public Simulation() {
        branches.put("main", null);
    }

    private Map<String, String> headFiles() {
        String head = branches.get(current);
        return head == null ? new TreeMap<>() : commits.get(head).files;
    }

    private Commit record(String message, List<String> parents) {
        counter += 1;
        Commit c = new Commit();
        c.id = "c" + counter;
        c.number = counter;
        c.message = message;
        c.files = new TreeMap<>(work);
        c.parents.addAll(parents);
        commits.put(c.id, c);
        branches.put(current, c.id);
        return c;
    }

    private Set<String> ancestors(String id) {
        Set<String> seen = new HashSet<>();
        List<String> stack = new ArrayList<>();
        stack.add(id);
        while (!stack.isEmpty()) {
            String next = stack.remove(stack.size() - 1);
            if (seen.add(next)) {
                stack.addAll(commits.get(next).parents);
            }
        }
        return seen;
    }

    public String write(String path, String content) {
        String old = work.put(path, content);
        if (old == null) {
            return "created";
        }
        return old.equals(content) ? "unchanged" : "modified";
    }

    public String read(String path) {
        return work.get(path);
    }

    public boolean remove(String path) {
        return work.remove(path) != null;
    }

    public String commit(String message) {
        if (message.isEmpty() || work.equals(headFiles())) {
            return null;
        }
        List<String> parents = new ArrayList<>();
        if (branches.get(current) != null) {
            parents.add(branches.get(current));
        }
        return record(message, parents).id;
    }

    public List<String> log(int n) {
        List<String> out = new ArrayList<>();
        String at = branches.get(current);
        while (at != null && out.size() < n) {
            Commit c = commits.get(at);
            out.add(c.id + ":" + c.message);
            at = c.parents.isEmpty() ? null : c.parents.get(0);
        }
        return out;
    }

    public List<String> diff() {
        Map<String, String> head = headFiles();
        Set<String> paths = new TreeSet<>(head.keySet());
        paths.addAll(work.keySet());
        List<String> out = new ArrayList<>();
        for (String path : paths) {
            String before = head.get(path);
            String after = work.get(path);
            if (before == null) {
                out.add("+" + path);
            } else if (after == null) {
                out.add("-" + path);
            } else if (!before.equals(after)) {
                out.add("~" + path);
            }
        }
        return out;
    }

    public boolean restore(String path) {
        String saved = headFiles().get(path);
        if (Objects.equals(saved, work.get(path))) {
            return false;
        }
        if (saved == null) {
            work.remove(path);
        } else {
            work.put(path, saved);
        }
        return true;
    }

    public boolean branch(String name) {
        if (branches.containsKey(name) || branches.get(current) == null) {
            return false;
        }
        branches.put(name, branches.get(current));
        return true;
    }

    public boolean switchBranch(String name) {
        if (!branches.containsKey(name) || name.equals(current) || !diff().isEmpty()) {
            return false;
        }
        current = name;
        work = new TreeMap<>(headFiles());
        return true;
    }

    public String currentBranch() {
        return current;
    }

    public String merge(String name) {
        if (!branches.containsKey(name) || name.equals(current) || !diff().isEmpty()) {
            return null;
        }
        String ours = branches.get(current);
        String theirs = branches.get(name);
        if (theirs == null || (ours != null && ancestors(ours).contains(theirs))) {
            return "up to date";
        }
        if (ours == null || ancestors(theirs).contains(ours)) {
            branches.put(current, theirs);
            work = new TreeMap<>(commits.get(theirs).files);
            return "fast-forward";
        }
        Set<String> common = ancestors(ours);
        common.retainAll(ancestors(theirs));
        Commit base = null;
        for (String id : common) {
            if (base == null || commits.get(id).number > base.number) {
                base = commits.get(id);
            }
        }
        Map<String, String> b = base.files;
        Map<String, String> o = commits.get(ours).files;
        Map<String, String> t = commits.get(theirs).files;
        Set<String> paths = new TreeSet<>(b.keySet());
        paths.addAll(o.keySet());
        paths.addAll(t.keySet());
        TreeMap<String, String> result = new TreeMap<>();
        List<String> conflicts = new ArrayList<>();
        for (String path : paths) {
            String bv = b.get(path);
            String ov = o.get(path);
            String tv = t.get(path);
            String pick;
            if (Objects.equals(ov, tv) || Objects.equals(tv, bv)) {
                pick = ov;
            } else if (Objects.equals(ov, bv)) {
                pick = tv;
            } else {
                conflicts.add(path);
                continue;
            }
            if (pick != null) {
                result.put(path, pick);
            }
        }
        if (!conflicts.isEmpty()) {
            return "conflict:" + String.join(",", conflicts);
        }
        work = result;
        return record("merge " + name, List.of(ours, theirs)).id;
    }

    public List<String> fileHistory(String path) {
        List<String> out = new ArrayList<>();
        String at = branches.get(current);
        while (at != null) {
            Commit c = commits.get(at);
            String parent = c.parents.isEmpty() ? null : c.parents.get(0);
            String before = parent == null ? null : commits.get(parent).files.get(path);
            if (!Objects.equals(before, c.files.get(path))) {
                out.add(c.id);
            }
            at = parent;
        }
        return out;
    }
}
