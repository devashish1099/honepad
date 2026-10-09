import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Write a file in the working tree. {@code "created"},
     * {@code "modified"} or {@code "unchanged"}.
     */
    public String write(String path, String content) {
        return null;
    }

    /**
     * A file's content in the working tree, or null.
     */
    public String read(String path) {
        return null;
    }

    /**
     * Remove a file from the working tree. Returns true if it existed.
     */
    public boolean remove(String path) {
        return false;
    }

    /**
     * Save the working tree. Returns the commit id, or null if nothing
     * changed or the message is empty.
     */
    public String commit(String message) {
        return null;
    }

    /**
     * The last {@code n} commits from the head, newest first, as
     * {@code "id:message"}.
     */
    public List<String> log(int n) {
        return null;
    }

    /**
     * Changes since the head commit: {@code "+path"}, {@code "-path"},
     * {@code "~path"}, sorted by path.
     */
    public List<String> diff() {
        return null;
    }

    /**
     * Put one file back to its committed state. Returns true if it
     * changed.
     */
    public boolean restore(String path) {
        return false;
    }

    /**
     * Create a branch at the head commit. Returns true if created.
     */
    public boolean branch(String name) {
        return false;
    }

    /**
     * Switch to another branch. Returns true if switched.
     */
    public boolean switchBranch(String name) {
        return false;
    }

    /**
     * The current branch's name.
     */
    public String currentBranch() {
        return null;
    }

    /**
     * Merge a branch into the current one.
     */
    public String merge(String name) {
        return null;
    }

    /**
     * Commits that changed {@code path}, newest first.
     */
    public List<String> fileHistory(String path) {
        return null;
    }
}
