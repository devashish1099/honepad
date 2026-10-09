class Simulation:
    def __init__(self):
        pass

    def set(self, timestamp, key, value):
        """Store a value. Returns the previous value, or None."""
        raise NotImplementedError

    def get(self, timestamp, key):
        """The value, or None."""
        raise NotImplementedError

    def delete(self, timestamp, key):
        """True if the key existed and is now gone."""
        raise NotImplementedError

    def compare_and_set(self, timestamp, key, expected, value):
        """Store value only if the key exists and equals expected."""
        raise NotImplementedError

    def scan_prefix(self, timestamp, prefix):
        """key=value for keys with the prefix, sorted by key."""
        raise NotImplementedError

    def size(self, timestamp):
        """Number of keys."""
        raise NotImplementedError

    def set_with_ttl(self, timestamp, key, value, ttl):
        """Store a value live in [timestamp, timestamp + ttl). Returns the previous live value, or None."""
        raise NotImplementedError

    def ttl_remaining(self, timestamp, key):
        """Time left, -1 for no TTL, or None if missing or expired."""
        raise NotImplementedError

    def begin(self, timestamp):
        """Open a transaction. Returns the new depth."""
        raise NotImplementedError

    def commit(self, timestamp):
        """Merge the innermost transaction into its parent."""
        raise NotImplementedError

    def rollback(self, timestamp):
        """Discard the innermost transaction."""
        raise NotImplementedError

    def backup(self, timestamp):
        """Save live keys with remaining TTL. Count saved, or None in a transaction."""
        raise NotImplementedError

    def restore(self, timestamp, time_to_restore):
        """Replace the store with the latest backup at or before timeToRestore. TTLs count from timestamp."""
        raise NotImplementedError
