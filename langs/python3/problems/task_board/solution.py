class Simulation:
    def __init__(self):
        self.tasks = {}
        self.users = {}
        self.assigned = {}
        self.completed = {}

    # level 1

    def add_task(self, timestamp, task_id, priority):
        if task_id in self.tasks:
            return False
        self.tasks[task_id] = priority
        return True

    def update_task(self, timestamp, task_id, priority):
        if task_id not in self.tasks:
            return False
        self.tasks[task_id] = priority
        return True

    def get_task(self, timestamp, task_id):
        return self.tasks.get(task_id)

    # level 2

    def remove_task(self, timestamp, task_id):
        if task_id not in self.tasks:
            return False
        del self.tasks[task_id]
        self.assigned.pop(task_id, None)
        return True

    def search(self, timestamp, prefix, n):
        rows = [(-p, t) for t, p in self.tasks.items() if t.startswith(prefix)]
        return [f"{t}({-p})" for p, t in sorted(rows)[:n]]

    # level 3

    def add_user(self, timestamp, user_id, quota):
        if user_id in self.users or quota <= 0:
            return False
        self.users[user_id] = quota
        self.completed[user_id] = 0
        return True

    def _live(self, task_id, timestamp):
        row = self.assigned.get(task_id)
        return row is not None and timestamp < row[1]

    def assign(self, timestamp, task_id, user_id, ttl):
        if task_id not in self.tasks or user_id not in self.users or ttl <= 0:
            return False
        if self._live(task_id, timestamp):
            return False
        held = sum(
            1 for t, row in self.assigned.items() if row[0] == user_id and self._live(t, timestamp)
        )
        if held >= self.users[user_id]:
            return False
        self.assigned[task_id] = [user_id, timestamp + ttl]
        return True

    def get_user_tasks(self, timestamp, user_id):
        if user_id not in self.users:
            return None
        rows = [
            (-self.tasks[t], t)
            for t, row in self.assigned.items()
            if row[0] == user_id and self._live(t, timestamp)
        ]
        return [f"{t}({-p})" for p, t in sorted(rows)]

    # level 4

    def complete(self, timestamp, task_id, user_id):
        row = self.assigned.get(task_id)
        if row is None or row[0] != user_id or not self._live(task_id, timestamp):
            return False
        del self.tasks[task_id]
        del self.assigned[task_id]
        self.completed[user_id] += 1
        return True

    def overdue(self, timestamp):
        rows = [
            (row[1], t, row[0])
            for t, row in self.assigned.items()
            if row[1] <= timestamp
        ]
        return [f"{t}({u})" for _exp, t, u in sorted(rows)]

    def top_completers(self, timestamp, n):
        rows = sorted(self.completed.items(), key=lambda kv: (-kv[1], kv[0]))
        return [f"{u}({c})" for u, c in rows[:n]]
