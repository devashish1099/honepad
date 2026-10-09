class Simulation:
    def __init__(self):
        pass

    def add_spot(self, timestamp, spot_id, size):
        """Add a spot of size small, medium, or large. Returns false if the id exists or the size is unknown."""
        raise NotImplementedError

    def park(self, timestamp, plate, size):
        """Park in the smallest free size that fits, lowest id first. Returns the spot id, or None."""
        raise NotImplementedError

    def leave(self, timestamp, plate):
        """Leave. Returns the freed spot id, or None if not parked."""
        raise NotImplementedError

    def occupancy(self, timestamp):
        """One size(used/total) per size that has spots, in size order. Example: ["small(1/2)", "large(1/1)"]."""
        raise NotImplementedError

    def find_car(self, timestamp, plate):
        """The spot the plate is in, or None."""
        raise NotImplementedError

    def current_fee(self, timestamp, plate):
        """Fee if the car left now: started hours (min 1) times the spot rate (small 2, medium 3, large 5). Null if not parked."""
        raise NotImplementedError

    def revenue(self, timestamp, start, end):
        """Sum of fees for leaves with timestamp in [from, to)."""
        raise NotImplementedError

    def reserve_spot(self, timestamp, spot_id, plate, start, end):
        """Hold a spot for one plate during [start, end). False if the spot is missing, the window is empty, or it overlaps another reservation."""
        raise NotImplementedError

    def cancel_reservation(self, timestamp, spot_id, plate, start):
        """Remove that plate's reservation starting at start."""
        raise NotImplementedError
