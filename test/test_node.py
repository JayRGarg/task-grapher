import unittest
from src.node import Node

class NodeTests(unittest.TestCase):

    def test_init_node(self):
        node_p: Node = Node("Parent Task")
        node_c: Node = Node("Child Task")
        self.assertEqual("Parent Task", node_p.get_value())
        self.assertEqual("Child Task", node_c.get_value())

if __name__ == "__main__":
    _ = unittest.main()
