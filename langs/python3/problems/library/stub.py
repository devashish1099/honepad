class Simulation:
    def __init__(self):
        pass

    def add_book(self, timestamp, book_id, copies):
        """Add a book with copies copies. Returns false if the id exists or copies is not positive."""
        raise NotImplementedError

    def borrow(self, timestamp, member_id, book_id):
        """Borrow one copy. Returns copies left, or None if the book is missing, none is free, or the member already holds it."""
        raise NotImplementedError

    def return_book(self, timestamp, member_id, book_id):
        """Return a held copy. Returns free copies after the return, or None if the member does not hold the book."""
        raise NotImplementedError

    def top_books(self, timestamp, n):
        """Top books as id(count) by total loans, then id. Example: ["b2(2)", "b1(1)", "b3(0)"]."""
        raise NotImplementedError

    def get_fine(self, timestamp, member_id):
        """Frozen plus open-loan fines minus payments. 10 per started late day, due 1209600 after the loan starts. Null if the member is unknown."""
        raise NotImplementedError

    def pay_fine(self, timestamp, member_id, amount):
        """Pay toward the fine. Returns what is still owed, or None if unknown, not positive, or more than is owed."""
        raise NotImplementedError

    def reserve(self, timestamp, member_id, book_id):
        """Join the hold queue. Returns the 1-based position, or None if the book is missing, a copy is free, the member holds it, or is already queued."""
        raise NotImplementedError

    def loans_at(self, timestamp, member_id, time_at):
        """Book ids held at timeAt, sorted. A loan covers [start, return). Null if the member is unknown."""
        raise NotImplementedError
