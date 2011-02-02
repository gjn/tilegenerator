import unittest

from tileforge.utils.list import TodoList

class TestTodoList(unittest.TestCase):
    def setUp(self):
        self.dummy = [1, 2, 19, "foo", 42, "bar"]

    def test_init(self):
        # empty list
        todo = TodoList()
        assert todo.success_count == 0
        assert todo.failure_count == 0
        assert len([item for item in todo]) == 0
        
        todo = TodoList(self.dummy)
        assert len([item for item in todo]) == len(self.dummy)
        
    def test_empty_after_read(self):
        todo = TodoList(self.dummy)
        # get all items
        [_ for _ in todo]
        assert len([item for item in todo]) == 0

    def test_task_done_success(self):
        todo = TodoList(self.dummy)
        for item in todo:
            todo.task_done(item, errors=None)
        assert todo.success_count == len(self.dummy)
        
    def test_task_done_failure(self):
        todo = TodoList(self.dummy)
        for item in todo:
            todo.task_done(item, errors="oups")
        assert todo.failure_count == len(self.dummy)

    def test_task_done_mixed(self):
        items = [True, False, True, True, False]
        todo = TodoList(items)
        for item in todo:
            todo.task_done(item, errors=item)
        
        assert todo.success_count == len([item for item in items if not item])
        assert todo.failure_count == len([item for item in items if item])

    def test_in_progress(self):
        todo = TodoList(self.dummy)
        items = [item for item in todo]
        assert todo.success_count == 0
        assert todo.failure_count == 0
        
        assert len(todo.in_progress) == len(self.dummy)
        for item in items:
            todo.task_done(item)
            assert len(todo.in_progress) + todo.success_count == len(self.dummy)
