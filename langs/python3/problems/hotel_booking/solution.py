class Simulation:
    def __init__(self):
        self.rooms = {}
        # booking_id -> [guest, room_id, check_in, check_out, created_at, cancelled_at]
        self.bookings = {}
        self.counter = 0
        self.waitlists = {}
        self.guests = set()

    # helpers

    def _free(self, room_id, check_in, check_out):
        for row in self.bookings.values():
            if row[1] == room_id and row[5] is None and row[2] < check_out and check_in < row[3]:
                return False
        return True

    def _cheapest(self, room_type, check_in, check_out):
        rows = sorted(
            (price, room_id)
            for room_id, (kind, price) in self.rooms.items()
            if kind == room_type and self._free(room_id, check_in, check_out)
        )
        return rows[0][1] if rows else None

    def _create(self, timestamp, guest_id, room_id, check_in, check_out):
        self.counter += 1
        booking_id = f"booking{self.counter}"
        self.bookings[booking_id] = [guest_id, room_id, check_in, check_out, timestamp, None]
        self.guests.add(guest_id)
        return booking_id

    def _drain(self, timestamp, room_type):
        queue = self.waitlists.get(room_type, [])
        kept = []
        for guest_id, check_in, check_out in queue:
            room_id = self._cheapest(room_type, check_in, check_out)
            if room_id is None:
                kept.append((guest_id, check_in, check_out))
            else:
                self._create(timestamp, guest_id, room_id, check_in, check_out)
        self.waitlists[room_type] = kept

    # level 1

    def add_room(self, timestamp, room_id, room_type, price):
        if room_id in self.rooms or price <= 0:
            return False
        self.rooms[room_id] = (room_type, price)
        self._drain(timestamp, room_type)
        return True

    def book(self, timestamp, guest_id, room_id, check_in, check_out):
        if room_id not in self.rooms or check_out <= check_in:
            return None
        if not self._free(room_id, check_in, check_out):
            return None
        return self._create(timestamp, guest_id, room_id, check_in, check_out)

    def cancel(self, timestamp, booking_id):
        row = self.bookings.get(booking_id)
        if row is None or row[5] is not None:
            return False
        row[5] = timestamp
        self._drain(timestamp, self.rooms[row[1]][0])
        return True

    # level 2

    def available(self, timestamp, room_type, check_in, check_out):
        if check_out <= check_in:
            return []
        rows = sorted(
            (price, room_id)
            for room_id, (kind, price) in self.rooms.items()
            if kind == room_type and self._free(room_id, check_in, check_out)
        )
        return [f"{room_id}({price})" for price, room_id in rows]

    def book_any(self, timestamp, guest_id, room_type, check_in, check_out):
        if check_out <= check_in:
            return None
        room_id = self._cheapest(room_type, check_in, check_out)
        if room_id is None:
            return None
        return self._create(timestamp, guest_id, room_id, check_in, check_out)

    # level 3

    def waitlist(self, timestamp, guest_id, room_type, check_in, check_out):
        if check_out <= check_in:
            return None
        if self._cheapest(room_type, check_in, check_out) is not None:
            return None
        queue = self.waitlists.setdefault(room_type, [])
        queue.append((guest_id, check_in, check_out))
        self.guests.add(guest_id)
        return len(queue)

    def guest_bookings(self, timestamp, guest_id):
        if guest_id not in self.guests:
            return None
        rows = sorted(
            (row[2], int(bid.removeprefix("booking")), bid, row[1])
            for bid, row in self.bookings.items()
            if row[0] == guest_id and row[5] is None
        )
        return [f"{bid}({room_id})" for _in, _n, bid, room_id in rows]

    def loyalty(self, timestamp, guest_id):
        if guest_id not in self.guests:
            return None
        return sum(
            row[3] - row[2]
            for row in self.bookings.values()
            if row[0] == guest_id and row[5] is None
        )

    # level 4

    def merge_guests(self, timestamp, keep, drop):
        if keep == drop or keep not in self.guests or drop not in self.guests:
            return False
        for row in self.bookings.values():
            if row[0] == drop:
                row[0] = keep
        for room_type, queue in self.waitlists.items():
            self.waitlists[room_type] = [
                (keep if g == drop else g, a, b) for g, a, b in queue
            ]
        self.guests.discard(drop)
        return True

    def revenue_at(self, timestamp, time_at):
        total = 0
        for _guest, room_id, check_in, check_out, created, cancelled in self.bookings.values():
            if created <= time_at and (cancelled is None or time_at < cancelled):
                total += (check_out - check_in) * self.rooms[room_id][1]
        return total
