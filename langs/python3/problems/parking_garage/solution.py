HOUR = 3600
SIZES = ["small", "medium", "large"]
RATES = {"small": 2, "medium": 3, "large": 5}


class Simulation:
    def __init__(self):
        self.spots = {}
        self.occupant = {}
        self.parked = {}
        self.leaves = []
        self.reservations = {}

    # level 1

    def add_spot(self, timestamp, spot_id, size):
        if spot_id in self.spots or size not in SIZES:
            return False
        self.spots[spot_id] = size
        self.occupant[spot_id] = None
        self.reservations[spot_id] = []
        return True

    def _blocked(self, spot_id, plate, timestamp):
        for owner, start, end in self.reservations[spot_id]:
            if owner != plate and start <= timestamp < end:
                return True
        return False

    def _own_reservation(self, spot_id, plate, timestamp):
        for owner, start, end in self.reservations[spot_id]:
            if owner == plate and start <= timestamp < end:
                return True
        return False

    def park(self, timestamp, plate, size):
        if plate in self.parked or size not in SIZES:
            return None
        for spot_id in sorted(self.spots):
            if self.occupant[spot_id] is None and self._own_reservation(
                spot_id, plate, timestamp
            ):
                return self._occupy(timestamp, plate, spot_id, True)
        need = SIZES.index(size)
        candidates = [
            (SIZES.index(self.spots[s]), s)
            for s in self.spots
            if self.occupant[s] is None
            and SIZES.index(self.spots[s]) >= need
            and not self._blocked(s, plate, timestamp)
        ]
        if not candidates:
            return None
        _rank, spot_id = min(candidates)
        return self._occupy(timestamp, plate, spot_id, False)

    def _occupy(self, timestamp, plate, spot_id, reserved):
        self.occupant[spot_id] = plate
        self.parked[plate] = (spot_id, timestamp, reserved)
        return spot_id

    def leave(self, timestamp, plate):
        row = self.parked.pop(plate, None)
        if row is None:
            return None
        spot_id = row[0]
        self.occupant[spot_id] = None
        self.leaves.append((timestamp, self._fee(row, timestamp)))
        return spot_id

    # level 2

    def occupancy(self, timestamp):
        out = []
        for size in SIZES:
            ids = [s for s, z in self.spots.items() if z == size]
            if not ids:
                continue
            used = sum(1 for s in ids if self.occupant[s] is not None)
            out.append(f"{size}({used}/{len(ids)})")
        return out

    def find_car(self, timestamp, plate):
        row = self.parked.get(plate)
        return None if row is None else row[0]

    # level 3

    def _fee(self, row, timestamp):
        spot_id, start, reserved = row
        hours = max(1, -(-(timestamp - start) // HOUR))
        fee = hours * RATES[self.spots[spot_id]]
        return fee // 2 if reserved else fee

    def current_fee(self, timestamp, plate):
        row = self.parked.get(plate)
        if row is None:
            return None
        return self._fee(row, timestamp)

    def revenue(self, timestamp, start, end):
        return sum(fee for when, fee in self.leaves if start <= when < end)

    # level 4

    def reserve_spot(self, timestamp, spot_id, plate, start, end):
        if spot_id not in self.spots or end <= start:
            return False
        for _owner, s, e in self.reservations[spot_id]:
            if s < end and start < e:
                return False
        self.reservations[spot_id].append((plate, start, end))
        return True

    def cancel_reservation(self, timestamp, spot_id, plate, start):
        if spot_id not in self.spots:
            return False
        rows = self.reservations[spot_id]
        for i, (owner, s, _e) in enumerate(rows):
            if owner == plate and s == start:
                rows.pop(i)
                return True
        return False
