import java.util.List;

public class Simulation {
    public Simulation() {}

    /** Add a room. False if the id exists or price is not positive. */
    public boolean addRoom(int timestamp, String roomId, String roomType, int price) {
        return false;
    }

    /**
     * Book nights {@code [checkIn, checkOut)}. Returns {@code "bookingN"}, or
     * null if the room is missing, the range is empty, or it overlaps.
     */
    public String book(int timestamp, String guestId, String roomId, int checkIn, int checkOut) {
        return null;
    }

    /** Cancel an active booking. */
    public boolean cancel(int timestamp, String bookingId) {
        return false;
    }

    /** Free rooms of a type as {@code roomId(price)}, by price then id. */
    public List<String> available(int timestamp, String roomType, int checkIn, int checkOut) {
        return null;
    }

    /** Book the first room {@code available} lists, or null. */
    public String bookAny(int timestamp, String guestId, String roomType, int checkIn, int checkOut) {
        return null;
    }

    /**
     * Join the type's waitlist. Returns the 1-based position, or null if the
     * range is empty or a room is free now.
     */
    public Integer waitlist(int timestamp, String guestId, String roomType, int checkIn, int checkOut) {
        return null;
    }

    /** Active bookings as {@code bookingN(roomId)}, by check-in then number. */
    public List<String> guestBookings(int timestamp, String guestId) {
        return null;
    }

    /** Total nights in active bookings, or null if unknown. */
    public Integer loyalty(int timestamp, String guestId) {
        return null;
    }

    /** Move drop's bookings and waitlist requests to keep. */
    public boolean mergeGuests(int timestamp, String keep, String drop) {
        return false;
    }

    /** Revenue of bookings that existed at {@code timeAt}. */
    public Integer revenueAt(int timestamp, int timeAt) {
        return null;
    }
}
