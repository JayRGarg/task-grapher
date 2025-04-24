import unittest
from src.node import Node
from datetime import datetime, timedelta, date, time

class NodeTests(unittest.TestCase):

    def test_init_node(self):
        node_p: Node = Node("Parent Task")
        node_c: Node = Node("Child Task")
        self.assertEqual("Parent Task", node_p.get_value())
        self.assertEqual("Child Task", node_c.get_value())
        return

    def test_node_due_date(self):
        tmr: date = date.today() + timedelta(days=1)
        node_p: Node = Node("Parent Task", due_date=tmr)
        self.assertEqual(tmr, node_p.get_due_date())

        day_after: date = tmr + timedelta(days=1)
        _ = node_p.set_due_date(day_after)
        self.assertEqual(day_after, node_p.get_due_date())
        return

    def test_node_due_time(self):
        tmr: date = date.today() + timedelta(days=1)
        afternoon: time = time(hour=14, minute=30)
        node_p: Node = Node("Parent Task", due_date=tmr, due_time=afternoon)
        self.assertEqual(afternoon, node_p.get_due_time())

        evening: time = time(hour=19, minute=30)
        _ = node_p.set_due_time(evening)
        self.assertEqual(evening, node_p.get_due_time())
        return
        
        
if __name__ == "__main__":
    _ = unittest.main()
