import threading
from collections import deque

class TodoList(object):
    def __init__(self, initial=[]):
        self.mutex = threading.Lock()
        self.todo = iter(initial)

        self.in_progress = deque()
        self.success = 0
        self.failure = deque()

    def __iter__(self):
        return self

    def next(self):
        self.mutex.acquire()
        try: 
            item = self.todo.next()
            self.in_progress.append(item)
        finally:
            self.mutex.release()
        return item

    def task_done(self, item, errors=False):
        self.mutex.acquire()
        try: 
            self.in_progress.remove(item)
            if not errors:
                self.success += 1
            else:
                self.failure.append({'item': item, 'errors': errors})
        finally:
            self.mutex.release()

    @property
    def success_count(self):
        return self.success

    @property
    def failure_count(self):
        return len(self.failure)
