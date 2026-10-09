import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Create a channel. Returns true if created.
     */
    public boolean createChannel(String channelId) {
        return false;
    }

    /**
     * Join a channel. Returns true if the user joined.
     */
    public boolean join(String userId, String channelId) {
        return false;
    }

    /**
     * Post a message. Returns its id ({@code "m1"}, {@code "m2"}, ...) or
     * null.
     */
    public String post(String userId, String channelId, String text) {
        return null;
    }

    /**
     * The last {@code n} messages of a channel, oldest first, each as
     * {@code "user:text"}. Null for an unknown channel.
     */
    public List<String> history(String channelId, int n) {
        return null;
    }

    /**
     * How many messages the user has not read in the channel, or null.
     */
    public Integer unread(String userId, String channelId) {
        return null;
    }

    /**
     * Mark the channel read. Returns how many were unread, or null.
     */
    public Integer markRead(String userId, String channelId) {
        return null;
    }

    /**
     * Top {@code n} posters of a channel as {@code "user(count)"}, or null.
     */
    public List<String> mostActive(String channelId, int n) {
        return null;
    }

    /**
     * Leave a channel. Returns true if the user was a member.
     */
    public boolean leave(String userId, String channelId) {
        return false;
    }

    /**
     * Change the text of your own message. Returns true if changed.
     */
    public boolean edit(String userId, String messageId, String text) {
        return false;
    }

    /**
     * Delete your own message. Returns true if deleted.
     */
    public boolean deleteMessage(String userId, String messageId) {
        return false;
    }

    /**
     * Ids of messages that mention {@code "@userId"}, oldest first.
     */
    public List<String> mentions(String userId) {
        return null;
    }

    /**
     * Reply in a message's thread. Returns the reply's id, or null.
     */
    public String reply(String userId, String parentId, String text) {
        return null;
    }

    /**
     * Replies to a message, oldest first, or null.
     */
    public List<String> thread(String messageId) {
        return null;
    }

    /**
     * Unread messages across all of the user's channels.
     */
    public int unreadTotal(String userId) {
        return 0;
    }
}
