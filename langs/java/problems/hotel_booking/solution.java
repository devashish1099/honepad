import java.util.ArrayList;
import java.util.Comparator;
import java.util.HashMap;
import java.util.HashSet;
import java.util.Iterator;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Set;

class Room {
    final String id;
    final String type;
    final int price;

    Room(String id, String type, int price) {
        this.id = id;
        this.type = type;
        this.price = price;
    }
}

class Booking {
    final int number;
    String guest;
    final String roomId;
    final int checkIn;
    final int checkOut;
    final int createdAt;
    Integer cancelledAt;

    Booking(int number, String guest, String roomId, int checkIn, int checkOut, int createdAt) {
        this.number = number;
        this.guest = guest;
        this.roomId = roomId;
        this.checkIn = checkIn;
        this.checkOut = checkOut;
        this.createdAt = createdAt;
    }

    boolean active() {
        return cancelledAt == null;
    }
}

class Request {
    String guest;
    final int checkIn;
    final int checkOut;

    Request(String guest, int checkIn, int checkOut) {
        this.guest = guest;
        this.checkIn = checkIn;
        this.checkOut = checkOut;
    }
}

public class Simulation {
    private final Map<String, Room> rooms = new HashMap<>();
    private final Map<String, Booking> bookings = new LinkedHashMap<>();
    private final Map<String, List<Request>> waitlists = new HashMap<>();
    private final Set<String> guests = new HashSet<>();
    private int counter = 0;

    public Simulation() {}

    public boolean addRoom(int timestamp, String roomId, String roomType, int price) {
        if (rooms.containsKey(roomId) || price <= 0) {
            return false;
        }
        rooms.put(roomId, new Room(roomId, roomType, price));
        drain(timestamp, roomType);
        return true;
    }

    public String book(int timestamp, String guestId, String roomId, int checkIn, int checkOut) {
        if (!rooms.containsKey(roomId) || checkOut <= checkIn || !free(roomId, checkIn, checkOut)) {
            return null;
        }
        return create(timestamp, guestId, roomId, checkIn, checkOut);
    }

    public boolean cancel(int timestamp, String bookingId) {
        Booking b = bookings.get(bookingId);
        if (b == null || !b.active()) {
            return false;
        }
        b.cancelledAt = timestamp;
        drain(timestamp, rooms.get(b.roomId).type);
        return true;
    }

    public List<String> available(int timestamp, String roomType, int checkIn, int checkOut) {
        List<String> out = new ArrayList<>();
        if (checkOut <= checkIn) {
            return out;
        }
        for (Room r : freeRooms(roomType, checkIn, checkOut)) {
            out.add(r.id + "(" + r.price + ")");
        }
        return out;
    }

    public String bookAny(int timestamp, String guestId, String roomType, int checkIn, int checkOut) {
        if (checkOut <= checkIn) {
            return null;
        }
        List<Room> free = freeRooms(roomType, checkIn, checkOut);
        if (free.isEmpty()) {
            return null;
        }
        return create(timestamp, guestId, free.get(0).id, checkIn, checkOut);
    }

    public Integer waitlist(int timestamp, String guestId, String roomType, int checkIn, int checkOut) {
        if (checkOut <= checkIn || !freeRooms(roomType, checkIn, checkOut).isEmpty()) {
            return null;
        }
        List<Request> queue = waitlists.computeIfAbsent(roomType, k -> new ArrayList<>());
        queue.add(new Request(guestId, checkIn, checkOut));
        guests.add(guestId);
        return queue.size();
    }

    public List<String> guestBookings(int timestamp, String guestId) {
        if (!guests.contains(guestId)) {
            return null;
        }
        List<Booking> mine = new ArrayList<>();
        for (Booking b : bookings.values()) {
            if (b.guest.equals(guestId) && b.active()) {
                mine.add(b);
            }
        }
        mine.sort(Comparator.comparingInt((Booking b) -> b.checkIn).thenComparingInt(b -> b.number));
        List<String> out = new ArrayList<>();
        for (Booking b : mine) {
            out.add("booking" + b.number + "(" + b.roomId + ")");
        }
        return out;
    }

    public Integer loyalty(int timestamp, String guestId) {
        if (!guests.contains(guestId)) {
            return null;
        }
        int nights = 0;
        for (Booking b : bookings.values()) {
            if (b.guest.equals(guestId) && b.active()) {
                nights += b.checkOut - b.checkIn;
            }
        }
        return nights;
    }

    public boolean mergeGuests(int timestamp, String keep, String drop) {
        if (keep.equals(drop) || !guests.contains(keep) || !guests.contains(drop)) {
            return false;
        }
        for (Booking b : bookings.values()) {
            if (b.guest.equals(drop)) {
                b.guest = keep;
            }
        }
        for (List<Request> queue : waitlists.values()) {
            for (Request r : queue) {
                if (r.guest.equals(drop)) {
                    r.guest = keep;
                }
            }
        }
        guests.remove(drop);
        return true;
    }

    public Integer revenueAt(int timestamp, int timeAt) {
        int total = 0;
        for (Booking b : bookings.values()) {
            boolean existed =
                    b.createdAt <= timeAt && (b.cancelledAt == null || timeAt < b.cancelledAt);
            if (existed) {
                total += (b.checkOut - b.checkIn) * rooms.get(b.roomId).price;
            }
        }
        return total;
    }

    private String create(int timestamp, String guestId, String roomId, int checkIn, int checkOut) {
        counter++;
        String id = "booking" + counter;
        bookings.put(id, new Booking(counter, guestId, roomId, checkIn, checkOut, timestamp));
        guests.add(guestId);
        return id;
    }

    private boolean free(String roomId, int checkIn, int checkOut) {
        for (Booking b : bookings.values()) {
            if (b.active() && b.roomId.equals(roomId) && b.checkIn < checkOut && checkIn < b.checkOut) {
                return false;
            }
        }
        return true;
    }

    private List<Room> freeRooms(String roomType, int checkIn, int checkOut) {
        List<Room> out = new ArrayList<>();
        for (Room r : rooms.values()) {
            if (r.type.equals(roomType) && free(r.id, checkIn, checkOut)) {
                out.add(r);
            }
        }
        out.sort(Comparator.comparingInt((Room r) -> r.price).thenComparing(r -> r.id));
        return out;
    }

    private void drain(int timestamp, String roomType) {
        List<Request> queue = waitlists.get(roomType);
        if (queue == null) {
            return;
        }
        Iterator<Request> it = queue.iterator();
        while (it.hasNext()) {
            Request r = it.next();
            List<Room> free = freeRooms(roomType, r.checkIn, r.checkOut);
            if (!free.isEmpty()) {
                create(timestamp, r.guest, free.get(0).id, r.checkIn, r.checkOut);
                it.remove();
            }
        }
    }
}
