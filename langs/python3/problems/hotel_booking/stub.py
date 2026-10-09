class Simulation:
    def __init__(self):
        pass

    def add_room(self, timestamp, room_id, room_type, price):
        """Add a room. False if the id exists or price is not positive."""
        raise NotImplementedError

    def book(self, timestamp, guest_id, room_id, check_in, check_out):
        """Book nights [checkIn, checkOut). Returns "bookingN", or None if the room is missing, the range is empty, or it overlaps."""
        raise NotImplementedError

    def cancel(self, timestamp, booking_id):
        """Cancel an active booking."""
        raise NotImplementedError

    def available(self, timestamp, room_type, check_in, check_out):
        """Free rooms of a type as roomId(price), by price then id."""
        raise NotImplementedError

    def book_any(self, timestamp, guest_id, room_type, check_in, check_out):
        """Book the first room available lists, or None."""
        raise NotImplementedError

    def waitlist(self, timestamp, guest_id, room_type, check_in, check_out):
        """Join the type's waitlist. Returns the 1-based position, or None if the range is empty or a room is free now."""
        raise NotImplementedError

    def guest_bookings(self, timestamp, guest_id):
        """Active bookings as bookingN(roomId), by check-in then number."""
        raise NotImplementedError

    def loyalty(self, timestamp, guest_id):
        """Total nights in active bookings, or None if unknown."""
        raise NotImplementedError

    def merge_guests(self, timestamp, keep, drop):
        """Move drop's bookings and waitlist requests to keep."""
        raise NotImplementedError

    def revenue_at(self, timestamp, time_at):
        """Revenue of bookings that existed at timeAt."""
        raise NotImplementedError
