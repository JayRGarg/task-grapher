import unittest
from datetime import date, time, datetime
from unittest.mock import MagicMock, patch
import tkinter as tk
from collections import deque

# Import the classes to be tested
from src.node import Node
from src.gui import Gui  # Assuming gui.py is in the same directory

class TestGui(unittest.TestCase):
    """
    Test cases for the Gui class.  This is more challenging to test
    because it involves Tkinter, which is GUI-based.  We'll use
    mocking to isolate the GUI logic as much as possible.
    """
    def setUp(self):
        """Set up a Gui instance with a mock Tkinter window and canvas."""
        self.root = MagicMock()  # Create a mock Tk root window
        self.canvas = MagicMock()  # Create a mock Tk canvas
        # Patch the Tkinter.Tk and Tkinter.Canvas constructors.  This replaces
        # the actual Tkinter objects with our mocks.
        with patch("tkinter.Tk", return_value=self.root), \
             patch("tkinter.Canvas", return_value=self.canvas):
            self.node_tree = Node("Root Node")
            self.gui = Gui(self.node_tree) #create a Gui instance with the mock objects
        return


    def test_gui_initialization(self):
        """Test that the Gui is initialized with the correct attributes."""
        # Check that Tk and Canvas were called during initialization
        self.root.title.assert_called_once()
        self.canvas.pack.assert_called_once()
        self.assertEqual(self.gui._tree, self.node_tree)
        self.assertEqual(self.gui._window, self.root)
        self.assertEqual(self.gui._canvas, self.canvas)
        self.assertEqual(self.gui._id_to_node, {self.node_tree.get_id(): self.node_tree}) #added node tree
        self.assertEqual(len(self.gui._id_to_node), 1)
        self.assertEqual(self.gui._node_positions, {})
        self.assertEqual(self.gui._line_positions, {})
        self.assertEqual(self.gui._selected_nodes, set())
        self.assertEqual(self.gui._selected_child_line_ids, set())
        return

    def test_add_node(self):
        """Test that the add_node method adds a node to the _id_to_node dictionary."""
        self.assertEqual(len(self.gui._id_to_node), 1)
        new_node = Node("New Node")
        returned_node = self.gui.add_node(new_node)
        self.assertEqual(self.gui._id_to_node[new_node.get_id()], new_node)
        self.assertEqual(len(self.gui._id_to_node), 2)
        self.assertEqual(returned_node, new_node)
        return

    def test_add_nodes(self):
        """Test that the add_nodes method adds all nodes in the tree."""
        # Create a small tree for testing
        child1 = Node("Child 1")
        child2 = Node("Child 2")
        grandchild1 = Node("Grandchild 1")
        self.node_tree.add_child(child1)
        self.node_tree.add_child(child2)
        child1.add_child(grandchild1)

        # Call add_nodes
        self.gui.add_nodes()

        # Check that all nodes are in _id_to_node
        self.assertIn(self.node_tree.get_id(), self.gui._id_to_node)
        self.assertIn(child1.get_id(), self.gui._id_to_node)
        self.assertIn(child2.get_id(), self.gui._id_to_node)
        self.assertIn(grandchild1.get_id(), self.gui._id_to_node)
        self.assertEqual(len(self.gui._id_to_node), 4)
        return

    def test_draw_node(self):
        """Test that the draw_node method creates the correct canvas items and updates _node_positions."""
        node = Node("Draw Node")
        x, y = 100, 150
        self.gui.draw_node(self.canvas, node, x, y)

        # Assert that create_oval and create_text were called with the correct arguments
        self.canvas.create_oval.assert_called_once()
        self.canvas.create_text.assert_called_once()

        #Check the tags.
        oval_args = self.canvas.create_oval.call_args_list[0][1]
        text_args = self.canvas.create_text.call_args_list[0][1]
        self.assertIn(str(node.get_id()), oval_args['tags'])
        self.assertIn(str(node.get_id()), text_args['tags'])

        # Assert that the node's position and IDs are stored correctly
        self.assertIn(node, self.gui._node_positions)
        stored_x, stored_y, circle_id, text_id = self.gui._node_positions[node]
        self.assertEqual(stored_x, x)
        self.assertEqual(stored_y, y)
        self.assertEqual(circle_id, self.canvas.create_oval.return_value)
        self.assertEqual(text_id, self.canvas.create_text.return_value)
        return

    def test_draw_branch_and_child(self):
        """Test that draw_branch_and_child draws a line and a child node."""
        parent_node = Node("Parent")
        child_node = Node("Child")
        self.gui.add_node(parent_node) # Manually add nodes.
        self.gui.add_node(child_node)
        x_p, y_p = 50, 50
        dx, dy = 20, 30

        # Mock the return values of create_oval and create_text, so that draw_node works.
        self.canvas.create_oval.return_value = 100  # Mock circle_id
        self.canvas.create_text.return_value = 200  # Mock text_id
        self.gui._node_positions[parent_node] = (x_p, y_p, 1, 2)  # Add parent to positions
        
        self.assertEqual(len(self.gui._line_positions), 0)
        self.gui.draw_branch_and_child(self.canvas, parent_node, child_node, dx, dy)
        self.assertEqual(len(self.gui._line_positions), 1)

        # Assert that draw_node was called for the child
        self.canvas.create_oval.assert_called()
        self.canvas.create_text.assert_called()

        # Assert that create_line was called with the correct coordinates
        self.canvas.create_line.assert_called_once_with(x_p, y_p, x_p + dx, y_p + dy, fill="red", width=1, tags=(str(parent_node.get_id()), "line"))

        # Assert that the line positions are stored correctly
        line_id = self.canvas.create_line.return_value
        self.assertIn(line_id, self.gui._line_positions)
        self.assertEqual(self.gui._line_positions[line_id], (x_p, y_p, x_p + dx, y_p + dy))

        # Assert that the node-to-line dictionaries are updated
        self.assertIn(parent_node, self.gui._node_to_child_line_ids)
        self.assertIn(line_id, self.gui._node_to_child_line_ids[parent_node])
        self.assertIn(child_node, self.gui._node_to_parent_line_ids)
        self.assertIn(line_id, self.gui._node_to_parent_line_ids[child_node])
        return

    def test_distance_from_node(self):
        """Test that distance_from_node calculates the correct distance."""
        node = Node("Distance Test")
        x_node, y_node = 100, 150
        self.gui._node_positions[node] = (x_node, y_node, 1, 2)  # Add node to positions
        x, y = 120, 180
        expected_distance = ((x - x_node) ** 2 + (y - y_node) ** 2) ** 0.5
        self.assertAlmostEqual(self.gui.distance_from_node(x, y, node), expected_distance)
        return

    def test_find_node_at(self):
        """Test that find_node_at returns the correct node or None."""
        node1 = Node("Node 1")
        node2 = Node("Node 2")
        x1, y1 = 100, 150
        x2, y2 = 200, 250
        self.gui._node_positions[node1] = (x1, y1, 1, 2)
        self.gui._node_positions[node2] = (x2, y2, 3, 4)
        self.gui._id_to_node[node1.get_id()] = node1 # add to id_to_node
        self.gui._id_to_node[node2.get_id()] = node2

        # Mock the return value of find_closest
        self.canvas.find_closest.side_effect = [(1,), (3,)] # Return item IDs

        # Mock the return value of the tags.
        self.canvas.gettags.side_effect = [('1', str(node1.get_id()), 'circle'), ('3', str(node2.get_id()), 'circle')]

        # Test finding node1
        found_node1 = self.gui.find_node_at(x1, y1)
        self.assertEqual(found_node1, node1)

        # Test finding node2
        found_node2 = self.gui.find_node_at(x2, y2)
        self.assertEqual(found_node2, node2)

        #resetting side effects
        self.canvas.find_closest.side_effect = None
        self.canvas.gettags.side_effect = None
        # Test when no node is found (outside the radius)
        self.canvas.find_closest.return_value = (1,)
        self.canvas.gettags.return_value = ('1', str(node1.get_id()), 'circle')
        not_found_node = self.gui.find_node_at(x1 - 50, y1 - 50)  # Outside radius
        self.assertIsNone(not_found_node)

        # Test when find_closest returns an empty tuple
        self.canvas.find_closest.return_value = ()
        none_node = self.gui.find_node_at(x1,y1)
        self.assertIsNone(none_node)
        return

    def test_select_child_line_ids(self):
        """Test that select_child_line_ids selects the correct line IDs."""
        parent_node = Node("Parent")
        child1 = Node("Child 1")
        child2 = Node("Child 2")
        self.gui.add_node(parent_node)
        self.gui.add_node(child1)
        self.gui.add_node(child2)

        line_id1 = 10
        line_id2 = 20
        self.gui._node_to_child_line_ids[parent_node] = {line_id1, line_id2}

        # Select the parent node
        self.gui._selected_nodes = {parent_node}
        self.gui._selected_child_line_ids = set()
        self.gui.select_child_line_ids()

        # Assert that the line IDs are added to _selected_child_line_ids
        self.assertEqual(self.gui._selected_child_line_ids, {line_id1, line_id2})
        return

    def test_select_parent_line_ids(self):
        """Test that select_child_line_ids selects the correct line IDs."""
        parent_node = Node("Parent")
        child1 = Node("Child 1")
        child2 = Node("Child 2")
        self.gui.add_node(parent_node)
        self.gui.add_node(child1)
        self.gui.add_node(child2)

        line_id1 = 10
        line_id2 = 20
        self.gui._node_to_child_line_ids[parent_node] = {line_id1, line_id2}
        self.gui._node_to_parent_line_ids[child1] = {line_id1}
        self.gui._node_to_parent_line_ids[child2] = {line_id2}

        # Select the parent node
        self.gui._selected_parent_line_ids = set()
        self.gui.select_parent_line_ids(child1)

        # Assert that the line IDs are added to _selected_child_line_ids
        self.assertEqual(self.gui._selected_parent_line_ids, {line_id1})
        return

    def test_start_drag(self):
        """Test that start_drag starts the drag operation correctly."""
        node1 = Node("Node 1")
        node2 = Node("Node 2")
        self.gui.add_node(node1)
        self.gui.add_node(node2)
        self.gui.find_node_at = MagicMock(return_value=node1)  # Mock find_node_at
        self.gui.select_child_line_ids = MagicMock()
        self.gui.select_parent_line_ids = MagicMock()

        event = MagicMock(x=100, y=150)

        def coord_effect(event):
            return event.x, event.y
        self.gui.event_to_canvas_coords = MagicMock()
        self.gui.event_to_canvas_coords.side_effect = coord_effect

        self.gui.start_drag(event)

        # Assert that find_node_at was called
        self.gui.find_node_at.assert_called_once_with(100, 150)
        # Assert the selected node
        self.assertEqual(self.gui._selected_nodes, {node1})
        self.assertEqual(self.gui._drag_start_x, 100)
        self.assertEqual(self.gui._drag_start_y, 150)
        self.gui.select_child_line_ids.assert_called_once()
        self.gui.select_parent_line_ids.assert_called_once()

        # Test when no node is found
        self.gui.find_node_at.return_value = None
        self.gui._selected_nodes = set()  # Clear selected nodes
        self.gui.start_drag(event)
        self.assertEqual(self.gui._selected_nodes, set())  # No node should be selected
        return

    def test_drag(self):
        """Test that the drag method moves the selected node and connected lines."""
        node0 = Node("Node 0")
        node1 = Node("Node 1")
        node2 = Node("Node 2")
        self.gui.add_node(node0)
        self.gui.add_node(node1)
        self.gui.add_node(node2)

        x0, y0 = 0, 50
        x1, y1 = 100, 150
        x2, y2 = 200, 250

        circle_id0, text_id0 = -1, 0
        circle_id1, text_id1 = 1, 2
        circle_id2, text_id2 = 3, 4
        self.gui._node_positions[node0] = (x0, y0, circle_id0, text_id0)
        self.gui._node_positions[node1] = (x1, y1, circle_id1, text_id1)
        self.gui._node_positions[node2] = (x2, y2, circle_id2, text_id2)
        line_id0 = -10
        line_id1 = 10
        self.gui._line_positions[line_id0] = (x0, y0, x1, y1)
        self.gui._line_positions[line_id1] = (x1, y1, x2, y2)
        self.gui._node_to_child_line_ids[node1] = {line_id1}
        self.gui._node_to_parent_line_ids[node1] = {line_id0}
        self.gui._selected_nodes = {node1, node2}
        self.gui._selected_child_line_ids = {line_id1}#realistically wouldn't be adding line_id2, it's a random line
        self.gui._selected_parent_line_ids = {line_id0}#realistically wouldn't be adding line_id2, it's a random line

        event = MagicMock(x=110, y=160)  # Move by 10 in x and y
        def coord_effect(event):
            return event.x, event.y
        self.gui.event_to_canvas_coords = MagicMock()
        self.gui.event_to_canvas_coords.side_effect = coord_effect
        self.gui._drag_start_x = 100
        self.gui._drag_start_y = 150
        self.gui.drag(event)

        # Assert that the node positions are updated correctly
        self.assertEqual(self.gui._node_positions[node0][:2], (x0, y0))
        self.assertEqual(self.gui._node_positions[node1][:2], (x1 + 10, y1 + 10))
        self.assertEqual(self.gui._node_positions[node2][:2], (x2 + 10, y2 + 10))

        # Assert that the canvas.coords method was called to move the node elements
        self.canvas.coords.assert_called()

        # Assert that the line positions are updated correctly
        self.assertEqual(self.gui._line_positions[line_id0], (x0, y0, x1 + 10, y1 + 10))
        self.assertEqual(self.gui._line_positions[line_id1], (x1 + 10, y1 + 10, x2 + 10, y2 + 10))

        # Check the updated drag start
        self.assertEqual(self.gui._drag_start_x, 110)
        self.assertEqual(self.gui._drag_start_y, 160)

        # Test when no nodes are selected
        self.gui._selected_nodes = set()
        self.gui.drag(event)  # Should not raise an error
        return

    def test_stop_drag(self):
        """Test that stop_drag resets the drag state correctly."""
        node0 = Node("Node 0")
        node1 = Node("Node 1")
        node2 = Node("Node 2")
        self.gui._selected_nodes = {node1, node2}
        self.gui._selected_child_line_ids = {10}
        self.gui._selected_parent_line_ids = {0}
        self.gui._drag_start_x = 100
        self.gui._drag_start_y = 150

        self.gui.stop_drag(MagicMock())

        self.assertEqual(self.gui._selected_nodes, set())
        self.assertEqual(self.gui._selected_child_line_ids, set())
        self.assertEqual(self.gui._selected_parent_line_ids, set())
        self.assertEqual(self.gui._drag_start_x, 0)
        self.assertEqual(self.gui._drag_start_y, 0)

        # Test when no nodes are selected
        self.gui.stop_drag(MagicMock()) # Should not raise errors
        return

    def test_run(self):
        """Test that run calls the mainloop method of the Tkinter window."""
        self.gui._window.mainloop = MagicMock()  # Mock mainloop
        self.gui.run()
        self.gui._window.mainloop.assert_called_once()
        return

if __name__ == '__main__':
    unittest.main()
