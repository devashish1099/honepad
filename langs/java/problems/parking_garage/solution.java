import java.util.ArrayList;
import java.util.HashMap;
import java.util.Iterator;
import java.util.List;
import java.util.Map;
import java.util.TreeMap;

class Reservation {
    final String plate;
    final int start;
    final int end;

    Reservation(String plate, int start, int end) {
        this.plate = plate;
        this.start = start;
        this.end = end;
    }

    boolean activeAt(int t) {
        return start <= t && t < end;
    }
}

class Spot {
    final int size;
    String occupant;
    final List<Reservation> reservations = new ArrayList<>();

    Spot(int size) {
        this.size = size;
    }
}

class Stay {
    final String spotId;
    final int start;
    final boolean reserved;

    Stay(String spotId, int start, boolean reserved) {
        this.spotId = spotId;
        this.start = start;
        this.reserved = reserved;
    }
}

public class Simulation {
    static final int HOUR = 3600;
    static final String[] SIZES = {"small", "medium", "large"};
    static final int[] RATES = {2, 3, 5};

    private final TreeMap<String, Spot> spots = new TreeMap<>();
    private final Map<String, Stay> parked = new HashMap<>();
    private final List<int[]> leaves = new ArrayList<>();

    public Simulation() {}

    public boolean addSpot(int timestamp, String spotId, String size) {
        int rank = sizeRank(size);
        if (spots.containsKey(spotId) || rank < 0) {
            return false;
        }
        spots.put(spotId, new Spot(rank));
        return true;
    }

    public String park(int timestamp, String plate, String size) {
        int need = sizeRank(size);
        if (parked.containsKey(plate) || need < 0) {
            return null;
        }
        for (Map.Entry<String, Spot> e : spots.entrySet()) {
            Spot spot = e.getValue();
            if (spot.occupant != null) {
                continue;
            }
            for (Reservation r : spot.reservations) {
                if (r.plate.equals(plate) && r.activeAt(timestamp)) {
                    return occupy(timestamp, plate, e.getKey(), true);
                }
            }
        }
        String best = null;
        int bestSize = Integer.MAX_VALUE;
        for (Map.Entry<String, Spot> e : spots.entrySet()) {
            Spot spot = e.getValue();
            if (spot.occupant != null || spot.size < need || spot.size >= bestSize) {
                continue;
            }
            if (blockedFor(spot, plate, timestamp)) {
                continue;
            }
            best = e.getKey();
            bestSize = spot.size;
        }
        return best == null ? null : occupy(timestamp, plate, best, false);
    }

    public String leave(int timestamp, String plate) {
        Stay stay = parked.remove(plate);
        if (stay == null) {
            return null;
        }
        spots.get(stay.spotId).occupant = null;
        leaves.add(new int[] {timestamp, fee(stay, timestamp)});
        return stay.spotId;
    }

    public List<String> occupancy(int timestamp) {
        int[] used = new int[SIZES.length];
        int[] total = new int[SIZES.length];
        for (Spot spot : spots.values()) {
            total[spot.size]++;
            if (spot.occupant != null) {
                used[spot.size]++;
            }
        }
        List<String> out = new ArrayList<>();
        for (int i = 0; i < SIZES.length; i++) {
            if (total[i] > 0) {
                out.add(SIZES[i] + "(" + used[i] + "/" + total[i] + ")");
            }
        }
        return out;
    }

    public String findCar(int timestamp, String plate) {
        Stay stay = parked.get(plate);
        return stay == null ? null : stay.spotId;
    }

    public Integer currentFee(int timestamp, String plate) {
        Stay stay = parked.get(plate);
        return stay == null ? null : fee(stay, timestamp);
    }

    public Integer revenue(int timestamp, int from, int to) {
        int sum = 0;
        for (int[] row : leaves) {
            if (from <= row[0] && row[0] < to) {
                sum += row[1];
            }
        }
        return sum;
    }

    public boolean reserveSpot(int timestamp, String spotId, String plate, int start, int end) {
        Spot spot = spots.get(spotId);
        if (spot == null || end <= start) {
            return false;
        }
        for (Reservation r : spot.reservations) {
            if (r.start < end && start < r.end) {
                return false;
            }
        }
        spot.reservations.add(new Reservation(plate, start, end));
        return true;
    }

    public boolean cancelReservation(int timestamp, String spotId, String plate, int start) {
        Spot spot = spots.get(spotId);
        if (spot == null) {
            return false;
        }
        Iterator<Reservation> it = spot.reservations.iterator();
        while (it.hasNext()) {
            Reservation r = it.next();
            if (r.plate.equals(plate) && r.start == start) {
                it.remove();
                return true;
            }
        }
        return false;
    }

    private String occupy(int timestamp, String plate, String spotId, boolean reserved) {
        spots.get(spotId).occupant = plate;
        parked.put(plate, new Stay(spotId, timestamp, reserved));
        return spotId;
    }

    private static boolean blockedFor(Spot spot, String plate, int timestamp) {
        for (Reservation r : spot.reservations) {
            if (!r.plate.equals(plate) && r.activeAt(timestamp)) {
                return true;
            }
        }
        return false;
    }

    private int fee(Stay stay, int now) {
        int elapsed = now - stay.start;
        int hours = Math.max(1, (elapsed + HOUR - 1) / HOUR);
        int full = hours * RATES[spots.get(stay.spotId).size];
        return stay.reserved ? full / 2 : full;
    }

    private static int sizeRank(String size) {
        for (int i = 0; i < SIZES.length; i++) {
            if (SIZES[i].equals(size)) {
                return i;
            }
        }
        return -1;
    }
}
