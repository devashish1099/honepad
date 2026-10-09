DAY = 86400
LOAN_DAYS = 14
FINE_PER_DAY = 10


class Simulation:
    def __init__(self):
        self.copies = {}
        self.borrows = {}
        self.loans = {}
        self.history = {}
        self.closed_fines = {}
        self.paid = {}
        self.members = set()
        self.queues = {}

    # level 1

    def add_book(self, timestamp, book_id, copies):
        if book_id in self.copies or copies <= 0:
            return False
        self.copies[book_id] = copies
        self.borrows[book_id] = 0
        self.queues[book_id] = []
        return True

    def _start_loan(self, timestamp, member_id, book_id):
        self.members.add(member_id)
        self.loans[(member_id, book_id)] = timestamp
        self.borrows[book_id] += 1
        self.history.setdefault(member_id, []).append([book_id, timestamp, None])

    def borrow(self, timestamp, member_id, book_id):
        if book_id not in self.copies:
            return None
        if (member_id, book_id) in self.loans:
            return None
        if self.copies[book_id] == 0:
            return None
        if member_id in self.members and self._fine(timestamp, member_id) > 0:
            return None
        self.copies[book_id] -= 1
        self._start_loan(timestamp, member_id, book_id)
        return self.copies[book_id]

    def return_book(self, timestamp, member_id, book_id):
        start = self.loans.pop((member_id, book_id), None)
        if start is None:
            return None
        self.closed_fines[member_id] = self.closed_fines.get(member_id, 0) + _accrued(
            start, timestamp
        )
        for row in self.history[member_id]:
            if row[0] == book_id and row[2] is None:
                row[2] = timestamp
        queue = self.queues[book_id]
        if queue:
            self._start_loan(timestamp, queue.pop(0), book_id)
        else:
            self.copies[book_id] += 1
        return self.copies[book_id]

    # level 2

    def top_books(self, timestamp, n):
        rows = sorted(self.borrows.items(), key=lambda kv: (-kv[1], kv[0]))
        return [f"{book}({count})" for book, count in rows[:n]]

    # level 3

    def _fine(self, timestamp, member_id):
        total = self.closed_fines.get(member_id, 0) - self.paid.get(member_id, 0)
        for (member, _book), start in self.loans.items():
            if member == member_id:
                total += _accrued(start, timestamp)
        return total

    def get_fine(self, timestamp, member_id):
        if member_id not in self.members:
            return None
        return self._fine(timestamp, member_id)

    def pay_fine(self, timestamp, member_id, amount):
        if member_id not in self.members:
            return None
        owed = self._fine(timestamp, member_id)
        if amount <= 0 or amount > owed:
            return None
        self.paid[member_id] = self.paid.get(member_id, 0) + amount
        return owed - amount

    # level 4

    def reserve(self, timestamp, member_id, book_id):
        if book_id not in self.copies:
            return None
        if self.copies[book_id] > 0:
            return None
        if (member_id, book_id) in self.loans:
            return None
        queue = self.queues[book_id]
        if member_id in queue:
            return None
        self.members.add(member_id)
        queue.append(member_id)
        return len(queue)

    def loans_at(self, timestamp, member_id, time_at):
        if member_id not in self.members:
            return None
        held = set()
        for book, start, end in self.history.get(member_id, []):
            if start <= time_at and (end is None or time_at < end):
                held.add(book)
        return sorted(held)


def _accrued(start, now):
    due = start + LOAN_DAYS * DAY
    late = now - due
    if late <= 0:
        return 0
    return -(-late // DAY) * FINE_PER_DAY
