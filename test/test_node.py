import unittest
from datetime import date, time, datetime, timedelta

# Import the classes to be tested
from src.node import Node

class Test_Node(unittest.TestCase):
    """
    Test cases for the Node class.
    """
    def setUp(self):
        """Set up a Node instance for each test."""
        self.node = Node("Test Node")
        return

    def test_node_creation(self):
        """Test that a node is created with the correct initial values."""
        self.assertEqual(self.node.get_value(), "Test Node")
        self.assertIsInstance(self.node.get_id(), int)
        self.assertIsInstance(self.node._created, datetime)
        self.assertIsNone(self.node.get_due_date())
        self.assertIsNone(self.node.get_due_time())
        self.assertFalse(self.node._completed)
        self.assertEqual(self.node.get_children(), [])
        self.assertEqual(self.node.get_parents(), [])
        return

    def test_node_creation_with_due_date_and_time(self):
        """Test node creation with due date and time."""
        due_date = date(2024, 12, 25)
        due_time = time(17, 30)
        node = Node("Test Node", due_date=due_date, due_time=due_time)
        self.assertEqual(node.get_due_date(), due_date)
        self.assertEqual(node.get_due_time(), due_time)
        return

    def test_node_creation_invalid_value_type(self):
        """Test that a TypeError is raised when the node value is not a string."""
        with self.assertRaises(TypeError):
            Node(123)  # Pass an integer instead of a string
        return

    def test_node_creation_invalid_date_type(self):
        """Test that a TypeError is raised when the due date is not a date."""
        with self.assertRaises(TypeError):
            Node("Test Node", due_date="2023-10-27")
        return

    def test_node_creation_invalid_time_type(self):
        """Test that a TypeError is raised when the due time is not a time."""
        with self.assertRaises(TypeError):
            Node("Test Node", due_time="12:00:00")
        return

    def test_get_value(self):
        """Test that the get_value method returns the correct value."""
        self.assertEqual(self.node.get_value(), "Test Node")
        return

    def test_set_value(self):
        """Test that the set_value method updates the value correctly."""
        new_value = self.node.set_value("New Value")
        self.assertEqual(self.node.get_value(), "New Value")
        self.assertEqual(new_value, "New Value")
        return

    def test_set_value_invalid_type(self):
        """Test that set_value raises TypeError if the new value is not a string."""
        with self.assertRaises(TypeError):
            self.node.set_value(123)
        return

    def test_get_due_date(self):
        """Test that get_due_date returns the correct due date."""
        due_date = date(2023, 11, 15)
        self.node.set_due_date(due_date)
        self.assertEqual(self.node.get_due_date(), due_date)
        return

    def test_set_due_date(self):
        """Test that set_due_date updates the due date correctly."""
        new_date = date(2024, 1, 1)
        returned_date = self.node.set_due_date(new_date)
        self.assertEqual(self.node.get_due_date(), new_date)
        self.assertEqual(returned_date, new_date)
        return

    def test_change_due_date(self):
        tmr: date = date.today() + timedelta(days=1)
        node_p: Node = Node("Parent Task", due_date=tmr)
        self.assertEqual(tmr, node_p.get_due_date())

        day_after: date = tmr + timedelta(days=1)
        _ = node_p.set_due_date(day_after)
        self.assertEqual(day_after, node_p.get_due_date())
        return

    def test_set_due_date_invalid_type(self):
        """Test that set_due_date raises TypeError if the new date is not a date."""
        with self.assertRaises(TypeError):
            self.node.set_due_date("2024-01-01")
        return

    def test_get_due_time(self):
        """Test that get_due_time returns the correct due time."""
        due_time = time(10, 30)
        self.node.set_due_time(due_time)
        self.assertEqual(self.node.get_due_time(), due_time)
        return

    def test_set_due_time(self):
        """Test that set_due_time updates the due time correctly."""
        new_time = time(14, 45)
        returned_time = self.node.set_due_time(new_time)
        self.assertEqual(self.node.get_due_time(), new_time)
        self.assertEqual(returned_time, new_time)
        return

    def test_change_due_time(self):
        tmr: date = date.today() + timedelta(days=1)
        afternoon: time = time(hour=14, minute=30)
        node_p: Node = Node("Parent Task", due_date=tmr, due_time=afternoon)
        self.assertEqual(afternoon, node_p.get_due_time())

        evening: time = time(hour=19, minute=30)
        _ = node_p.set_due_time(evening)
        self.assertEqual(evening, node_p.get_due_time())
        return

    def test_set_due_time_invalid_type(self):
        """Test that set_due_time raises TypeError if the new time is not a time."""
        with self.assertRaises(TypeError):
            self.node.set_due_time("14:45:00")
        return

    def test_get_children(self):
        """Test that get_children returns an empty list initially."""
        self.assertEqual(self.node.get_children(), [])
        return

    def test_get_parents(self):
        """Test that get_parents returns an empty list initially."""
        self.assertEqual(self.node.get_parents(), [])
        return

    def test_add_child(self):
        """Test that add_child adds a child node correctly."""
        child_node = Node("Child Node")
        self.assertTrue(self.node.add_child(child_node))
        self.assertIn(child_node, self.node.get_children())
        self.assertIn(self.node, child_node.get_parents())
        return

    def test_add_child_existing_child(self):
        """Test that add_child does not add a child node if it already exists."""
        child_node = Node("Child Node")
        self.assertTrue(self.node.add_child(child_node))
        self.assertEqual(len(self.node.get_children()), 1) # Ensure only one child
        self.assertTrue(self.node.add_child(child_node))  # Try to add the same child again, should still be true
        self.assertEqual(len(self.node.get_children()), 1) # Ensure length is still 1
        return

    def test_add_child_max_children(self):
        """Test that add_child does not add more than max_children children."""
        self.node._max_children = 2  # Set a maximum of 2 children for this test
        child1 = Node("Child 1")
        child2 = Node("Child 2")
        child3 = Node("Child 3")
        self.assertTrue(self.node.add_child(child1))
        self.assertTrue(self.node.add_child(child2))
        self.assertFalse(self.node.add_child(child3))  # Should not be able to add a third child
        self.assertEqual(len(self.node.get_children()), 2)
        return

    def test_add_child_max_parents(self):
        """Test that add_child does not add a child if it has max parents."""
        parent1 = Node("Parent 1")
        parent2 = Node("Parent 2")
        parent3 = Node("Parent 3")
        parent4 = Node("Parent 4")
        child_node = Node("Child")
        child_node._max_parents = 2
        parent1.add_child(child_node)
        parent2.add_child(child_node)
        self.assertFalse(parent3.add_child(child_node))
        self.assertFalse(parent4.add_child(child_node))
        self.assertEqual(len(child_node.get_parents()), 2)
        return

    def test_get_children_r(self):
        """Test that get_children_r returns all recursive children."""
        child1 = Node("Child 1")
        child2 = Node("Child 2")
        grandchild1 = Node("Grandchild 1")
        grandchild2 = Node("Grandchild 2")

        self.node.add_child(child1)
        self.node.add_child(child2)
        child1.add_child(grandchild1)
        child2.add_child(grandchild2)

        recursive_children = self.node.get_children_r()
        self.assertIn(child1, recursive_children)
        self.assertIn(child2, recursive_children)
        self.assertIn(grandchild1, recursive_children)
        self.assertIn(grandchild2, recursive_children)
        self.assertEqual(len(recursive_children), 4)
        return

    def test_get_children_r_no_children(self):
        """Test that get_children_r returns an empty list when there are no children."""
        self.assertEqual(self.node.get_children_r(), [])
        return

    def test_get_children_r_complex_graph(self):
        """Test get_children_r with a more complex graph structure."""
        # Create a small graph:
        # A -> B, C
        # B -> D
        # C -> D, E
        # D -> F
        node_a = Node("A")
        node_b = Node("B")
        node_c = Node("C")
        node_d = Node("D")
        node_e = Node("E")
        node_f = Node("F")

        node_a.add_child(node_b)
        node_a.add_child(node_c)
        node_b.add_child(node_d)
        node_c.add_child(node_d)
        node_c.add_child(node_e)
        node_d.add_child(node_f)

        # Check the results from node A
        children_of_a = node_a.get_children_r()
        self.assertIn(node_b, children_of_a)
        self.assertIn(node_c, children_of_a)
        self.assertIn(node_d, children_of_a)
        self.assertIn(node_e, children_of_a)
        self.assertIn(node_f, children_of_a)
        self.assertEqual(len(children_of_a), 5)

        # Check results from node B (should be D, F)
        children_of_b = node_b.get_children_r()
        self.assertIn(node_d, children_of_b)
        self.assertIn(node_f, children_of_b)
        self.assertEqual(len(children_of_b), 2)

        # Check results from node D (should be F)
        children_of_d = node_d.get_children_r()
        self.assertIn(node_f, children_of_d)
        self.assertEqual(len(children_of_d), 1)

        # Check results from node F (should be empty)
        children_of_f = node_f.get_children_r()
        self.assertEqual(len(children_of_f), 0)
        return
        
        
if __name__ == "__main__":
    _ = unittest.main()
