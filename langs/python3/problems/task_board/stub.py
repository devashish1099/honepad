class Simulation:
    def __init__(self):
        pass

    def add_task(self, timestamp, task_id, priority):
        """Add a task. Returns false if the id exists."""
        raise NotImplementedError

    def update_task(self, timestamp, task_id, priority):
        """Set a new priority. Returns false if the task is missing."""
        raise NotImplementedError

    def get_task(self, timestamp, task_id):
        """The task's priority, or None if missing."""
        raise NotImplementedError

    def remove_task(self, timestamp, task_id):
        """Delete a task. Returns false if missing."""
        raise NotImplementedError

    def search(self, timestamp, prefix, n):
        """At most n id(priority) for ids starting with prefix, priority high to low, then id. Example: ["bug-2(9)", "bug-1(5)"]."""
        raise NotImplementedError

    def add_user(self, timestamp, user_id, quota):
        """Add a user. False if the id exists or quota is not positive."""
        raise NotImplementedError

    def assign(self, timestamp, task_id, user_id, ttl):
        """Assign for [timestamp, timestamp + ttl). False if missing, ttl not positive, the task is live, or the user is at quota."""
        raise NotImplementedError

    def get_user_tasks(self, timestamp, user_id):
        """The user's live tasks, sorted like search. Null if the user is missing."""
        raise NotImplementedError

    def complete(self, timestamp, task_id, user_id):
        """Finish a task live for this user. The task is removed."""
        raise NotImplementedError

    def overdue(self, timestamp):
        """Ended, not completed assignments as taskId(userId), by end time then id."""
        raise NotImplementedError

    def top_completers(self, timestamp, n):
        """At most n userId(count), count high to low, then id."""
        raise NotImplementedError
