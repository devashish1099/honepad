import java.util.ArrayList;
import java.util.HashMap;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

class Message {
    int seq;
    String id;
    String channel;
    String author;
    String text;
    String parent;
    boolean edited;
    boolean deleted;
}

public class Simulation {
    private final Map<String, Map<String, Integer>> channels = new LinkedHashMap<>();
    private final Map<String, Message> messages = new LinkedHashMap<>();
    private int counter = 0;

    public Simulation() {}

    private boolean member(String userId, String channelId) {
        Map<String, Integer> members = channels.get(channelId);
        return members != null && members.containsKey(userId);
    }

    private Message create(String userId, String channelId, String text, String parent) {
        counter += 1;
        Message m = new Message();
        m.seq = counter;
        m.id = "m" + counter;
        m.channel = channelId;
        m.author = userId;
        m.text = text;
        m.parent = parent;
        messages.put(m.id, m);
        return m;
    }

    private String render(Message m) {
        return m.author + ":" + m.text + (m.edited ? " (edited)" : "");
    }

    private int countUnread(String userId, String channelId) {
        int readUpTo = channels.get(channelId).get(userId);
        int count = 0;
        for (Message m : messages.values()) {
            if (m.channel.equals(channelId) && m.parent == null && !m.deleted
                    && m.seq > readUpTo && !m.author.equals(userId)) {
                count += 1;
            }
        }
        return count;
    }

    public boolean createChannel(String channelId) {
        if (channels.containsKey(channelId)) {
            return false;
        }
        channels.put(channelId, new HashMap<>());
        return true;
    }

    public boolean join(String userId, String channelId) {
        if (!channels.containsKey(channelId) || member(userId, channelId)) {
            return false;
        }
        channels.get(channelId).put(userId, counter);
        return true;
    }

    public String post(String userId, String channelId, String text) {
        if (!member(userId, channelId) || text.isEmpty()) {
            return null;
        }
        Message m = create(userId, channelId, text, null);
        channels.get(channelId).put(userId, m.seq);
        return m.id;
    }

    public List<String> history(String channelId, int n) {
        if (!channels.containsKey(channelId)) {
            return null;
        }
        List<String> all = new ArrayList<>();
        for (Message m : messages.values()) {
            if (m.channel.equals(channelId) && m.parent == null && !m.deleted) {
                all.add(render(m));
            }
        }
        if (n <= 0) {
            return new ArrayList<>();
        }
        return new ArrayList<>(all.subList(Math.max(0, all.size() - n), all.size()));
    }

    public Integer unread(String userId, String channelId) {
        if (!member(userId, channelId)) {
            return null;
        }
        return countUnread(userId, channelId);
    }

    public Integer markRead(String userId, String channelId) {
        if (!member(userId, channelId)) {
            return null;
        }
        int before = countUnread(userId, channelId);
        channels.get(channelId).put(userId, counter);
        return before;
    }

    public List<String> mostActive(String channelId, int n) {
        if (!channels.containsKey(channelId)) {
            return null;
        }
        Map<String, Integer> counts = new HashMap<>();
        for (Message m : messages.values()) {
            if (m.channel.equals(channelId) && m.parent == null && !m.deleted) {
                counts.merge(m.author, 1, Integer::sum);
            }
        }
        List<String> users = new ArrayList<>(counts.keySet());
        users.sort((a, b) -> {
            int diff = counts.get(b) - counts.get(a);
            return diff != 0 ? diff : a.compareTo(b);
        });
        List<String> out = new ArrayList<>();
        for (String user : users) {
            if (out.size() >= n) {
                break;
            }
            out.add(user + "(" + counts.get(user) + ")");
        }
        return out;
    }

    public boolean leave(String userId, String channelId) {
        if (!member(userId, channelId)) {
            return false;
        }
        channels.get(channelId).remove(userId);
        return true;
    }

    public boolean edit(String userId, String messageId, String text) {
        Message m = messages.get(messageId);
        if (m == null || m.deleted || !m.author.equals(userId) || text.isEmpty()) {
            return false;
        }
        m.text = text;
        m.edited = true;
        return true;
    }

    public boolean deleteMessage(String userId, String messageId) {
        Message m = messages.get(messageId);
        if (m == null || m.deleted || !m.author.equals(userId)) {
            return false;
        }
        m.deleted = true;
        for (Message r : messages.values()) {
            if (messageId.equals(r.parent)) {
                r.deleted = true;
            }
        }
        return true;
    }

    public List<String> mentions(String userId) {
        List<String> out = new ArrayList<>();
        String tag = "@" + userId;
        for (Message m : messages.values()) {
            if (m.deleted || m.author.equals(userId) || !member(userId, m.channel)) {
                continue;
            }
            for (String token : m.text.split(" ")) {
                if (token.equals(tag)) {
                    out.add(m.id);
                    break;
                }
            }
        }
        return out;
    }

    public String reply(String userId, String parentId, String text) {
        Message parent = messages.get(parentId);
        if (parent == null || parent.deleted || parent.parent != null || text.isEmpty()) {
            return null;
        }
        if (!member(userId, parent.channel)) {
            return null;
        }
        return create(userId, parent.channel, text, parentId).id;
    }

    public List<String> thread(String messageId) {
        Message parent = messages.get(messageId);
        if (parent == null || parent.deleted || parent.parent != null) {
            return null;
        }
        List<String> out = new ArrayList<>();
        for (Message m : messages.values()) {
            if (messageId.equals(m.parent) && !m.deleted) {
                out.add(render(m));
            }
        }
        return out;
    }

    public int unreadTotal(String userId) {
        int total = 0;
        for (String channelId : channels.keySet()) {
            if (member(userId, channelId)) {
                total += countUnread(userId, channelId);
            }
        }
        return total;
    }
}
