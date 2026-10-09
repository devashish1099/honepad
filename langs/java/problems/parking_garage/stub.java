import java.util.List;

public class Simulation {
    public Simulation() {}

    /**
     * Add a spot of size small, medium, or large. Returns false if the id
     * exists or the size is unknown.
     */
    public boolean addSpot(int timestamp, String spotId, String size) {
        return false;
    }

    /**
     * Park in the smallest free size that fits, lowest id first. Returns the
     * spot id, or null.
     */
    public String park(int timestamp, String plate, String size) {
        return null;
    }

    /** Leave. Returns the freed spot id, or null if not parked. */
    public String leave(int timestamp, String plate) {
        return null;
    }

    /**
     * One {@code size(used/total)} per size that has spots, in size order.
     * Example: {@code ["small(1/2)", "large(1/1)"]}.
     */
    public List<String> occupancy(int timestamp) {
        return null;
    }

    /** The spot the plate is in, or null. */
    public String findCar(int timestamp, String plate) {
        return null;
    }

    /**
     * Fee if the car left now: started hours (min 1) times the spot rate
     * (small 2, medium 3, large 5). Null if not parked.
     */
    public Integer currentFee(int timestamp, String plate) {
        return null;
    }

    /** Sum of fees for leaves with timestamp in {@code [from, to)}. */
    public Integer revenue(int timestamp, int from, int to) {
        return null;
    }

    /**
     * Hold a spot for one plate during {@code [start, end)}. False if the spot
     * is missing, the window is empty, or it overlaps another reservation.
     */
    public boolean reserveSpot(int timestamp, String spotId, String plate, int start, int end) {
        return false;
    }

    /** Remove that plate's reservation starting at {@code start}. */
    public boolean cancelReservation(int timestamp, String spotId, String plate, int start) {
        return false;
    }
}
