_DELETED = object()


class Simulation:
    def __init__(self):
        self.layers = [{}]
        self.backups = []

    # storage helpers: a row is (value, expiry) with expiry None for no TTL

    def _row(self, key, timestamp):
        for layer in reversed(self.layers):
            if key in layer:
                row = layer[key]
                if row is _DELETED:
                    return None
                if row[1] is not None and timestamp >= row[1]:
                    return None
                return row
        return None

    def _write(self, key, row):
        if len(self.layers) == 1 and row is _DELETED:
            self.layers[0].pop(key, None)
        else:
            self.layers[-1][key] = row

    def _live_items(self, timestamp):
        merged = {}
        for layer in self.layers:
            merged.update(layer)
        out = {}
        for key, row in merged.items():
            if row is _DELETED:
                continue
            if row[1] is not None and timestamp >= row[1]:
                continue
            out[key] = row
        return out

    # level 1

    def set(self, timestamp, key, value):
        old = self._row(key, timestamp)
        self._write(key, (value, None))
        return None if old is None else old[0]

    def get(self, timestamp, key):
        row = self._row(key, timestamp)
        return None if row is None else row[0]

    def delete(self, timestamp, key):
        if self._row(key, timestamp) is None:
            return False
        self._write(key, _DELETED)
        return True

    def compare_and_set(self, timestamp, key, expected, value):
        row = self._row(key, timestamp)
        if row is None or row[0] != expected:
            return False
        self._write(key, (value, row[1]))
        return True

    # level 2

    def scan_prefix(self, timestamp, prefix):
        items = self._live_items(timestamp)
        return [f"{k}={items[k][0]}" for k in sorted(items) if k.startswith(prefix)]

    def size(self, timestamp):
        return len(self._live_items(timestamp))

    # level 3

    def set_with_ttl(self, timestamp, key, value, ttl):
        old = self._row(key, timestamp)
        self._write(key, (value, timestamp + ttl))
        return None if old is None else old[0]

    def ttl_remaining(self, timestamp, key):
        row = self._row(key, timestamp)
        if row is None:
            return None
        if row[1] is None:
            return -1
        return row[1] - timestamp

    # level 4

    def begin(self, timestamp):
        self.layers.append({})
        return len(self.layers) - 1

    def commit(self, timestamp):
        if len(self.layers) == 1:
            return False
        top = self.layers.pop()
        for key, row in top.items():
            self._write(key, row)
        return True

    def rollback(self, timestamp):
        if len(self.layers) == 1:
            return False
        self.layers.pop()
        return True

    def backup(self, timestamp):
        if len(self.layers) > 1:
            return None
        items = self._live_items(timestamp)
        snapshot = {
            k: (v, None if exp is None else exp - timestamp) for k, (v, exp) in items.items()
        }
        self.backups.append((timestamp, snapshot))
        return len(snapshot)

    def restore(self, timestamp, time_to_restore):
        if len(self.layers) > 1:
            return False
        chosen = None
        for when, snapshot in self.backups:
            if when <= time_to_restore:
                chosen = snapshot
        if chosen is None:
            return False
        self.layers = [
            {k: (v, None if left is None else timestamp + left) for k, (v, left) in chosen.items()}
        ]
        return True
