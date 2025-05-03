import tkinter as tk
from src.node import Node
from collections import deque
import logging
import math

NODE_RADIUS: int = 30#10
# RADIAL_SPACING: int = 100  # Adjust as needed for spacing between levels
# SPIRAL_FACTOR: float = 0.2  # Adjust to control the spiral effect
WIDTH = 1000
HEIGHT = 1000
BASE_DISTANCE: int = 500  # Base distance from parent to first child
DISTANCE_LEVEL_FACTOR: float = 0.55
ANGLE_INCREMENT: float = 2 * math.pi / 5  # Base angle between siblings (adjust for branching)
SPIRAL_FACTOR: float = 20#0.6  # Controls the spiral effect (angle offset per level)


class Gui:

    def __init__(self, tree: Node):
        self._tree: Node = tree
        self._window: tk.Tk = tk.Tk()
        self._window.title("Task-Grapher")
        self._canvas: tk.Canvas = tk.Canvas(self._window, width=WIDTH, height=HEIGHT, bg="white")
        self._canvas.pack()
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._id_to_node: dict[int, Node] = {}
        
        self._optimal_node_positions: dict[Node, tuple[int, int]] = {} #each tuple consists of (x, y)
        self._node_positions: dict[Node, tuple[int, int, int, int]] = {} #each tuple consists of (x, y, circle_id, text_id)
        self._line_positions: dict[int, tuple[int, int, int, int]] = {} #each tuple consists of (xp, yp, xc, yc)

        self._node_to_child_line_ids: dict[Node, set[int]] = {}
        self._node_to_parent_line_ids: dict[Node, set[int]] = {}

        self._selected_nodes: set[Node] = set()
        self._selected_child_line_ids: set[int] = set()
        self._selected_parent_line_ids: set[int] = set()

        self.add_nodes()

        self._canvas.bind("<Button-1>", self.start_drag)
        self._canvas.bind("<B1-Motion>", self.drag)
        self._canvas.bind("<ButtonRelease-1>", self.stop_drag)

    def add_nodes(self):
        visited: set[Node] = set()
        stack: deque[Node] = deque()
        curr = self._tree
        visited.add(curr)
        stack.append(curr)
        while stack:
            curr = stack.pop()
            _ = self.add_node(curr)
            for child in curr.get_children():
                if child not in visited:
                    visited.add(child)
                    stack.append(child)
        return


    def add_node(self, node: Node) -> Node:
        if node.get_id() in self._id_to_node:
            assert self._id_to_node[node.get_id()] == node, "Attempting to add 2 different nodes with the same ID!"
            return node
        self._id_to_node[node.get_id()] = node
        return node 

    def calculate_node_positions(self):
        """Calculates node positions with a parent-relative spiral effect."""

        def calculate_child_positions(parent_node: Node, parent_x: int, parent_y: int, level: int, visited: set[Node], start_angle_offset: float = 0):
            num_children = len(parent_node.get_children())
            if num_children == 0:
                return

            # Calculate the base angle step for this parent
            angle_step = ANGLE_INCREMENT

            for i, child_node in enumerate(parent_node.get_children()):
                if child_node not in visited:
                    logging.debug("finding location of: %s", child_node.get_value())
                    visited.add(child_node)
                    # Calculate angle relative to the parent
                    angle = i * angle_step + start_angle_offset

                    # Calculate distance from parent (can be constant or vary)
                    distance = BASE_DISTANCE * (DISTANCE_LEVEL_FACTOR**level) # You could make this depend on the level

                    # Convert polar coordinates (relative to parent) to Cartesian coordinates
                    child_x = int(parent_x + distance * math.cos(angle))
                    child_y = int(parent_y + distance * math.sin(angle))

                    _ = self.add_node(child_node)
                    self._optimal_node_positions[child_node] = (child_x, child_y)

                    # Introduce a spiral effect by offsetting the starting angle for the next level
                    next_level_angle_offset = start_angle_offset + level * SPIRAL_FACTOR

                    calculate_child_positions(child_node, child_x, child_y, level + 1, visited, next_level_angle_offset)
            return

        # Position the root node
        root_x = int(WIDTH/2)#200
        root_y = int(HEIGHT/2)#200
        _ = self.add_node(self._tree)
        self._optimal_node_positions[self._tree] = (root_x, root_y)
        visited_nodes: set[Node] = set()
        visited_nodes.add(self._tree)

        # Start the recursive positioning from the root
        calculate_child_positions(self._tree, root_x, root_y, 1, visited_nodes, 0)
        print(self._optimal_node_positions.keys())
        return

    def draw_tree(self, canvas: tk.Canvas) -> None:
        x, y = self._optimal_node_positions[self._tree]
        self.draw_node(canvas, self._tree, x, y)

        parent_queue: deque[Node] = deque()
        nodes_visited: set[Node] = set()
        parent_queue.append(self._tree)
        nodes_visited.add(self._tree)

        parent: Node
        while parent_queue:
            parent = parent_queue.popleft()
            for child in parent.get_children():
                if child not in nodes_visited:
                    nodes_visited.add(child)
                    parent_queue.append(child)
                    dx = self._optimal_node_positions[child][0] - self._optimal_node_positions[parent][0]
                    dy = self._optimal_node_positions[child][1] - self._optimal_node_positions[parent][1]
                    self.draw_branch_and_child(canvas, parent, child, dx, dy)
        return

    def draw_node(self, canvas: tk.Canvas, node: Node, x: int, y: int) -> None:
        x1: int = x - NODE_RADIUS
        y1: int = y - NODE_RADIUS
        x2: int = x + NODE_RADIUS
        y2: int = y + NODE_RADIUS
        circle_id: int = canvas.create_oval(x1, y1, x2, y2, fill="blue", outline="black", tags=(str(node.get_id()), "circle"))
        text_id: int = canvas.create_text(x, y, text=node.get_value(), fill="white", font=("Arial", 6), tags=(str(node.get_id()), "text"))
        self._node_positions[node] = (x, y, circle_id, text_id)

        logging.info("Drawing Node: %d", node.get_id())
        logging.debug("Position: %d,%d, Circle_Id: %d, Text_Id: %d", x, y, circle_id, text_id)

    def draw_branch_and_child(self, canvas: tk.Canvas, parent_node: Node, child_node: Node, dx: int, dy: int) -> None:
        x_p, y_p = self._node_positions[parent_node][:2]
        x_c, y_c = x_p + dx, y_p + dy
        self.draw_node(canvas, child_node, x_c, y_c)
        line_id:int = canvas.create_line(x_p, y_p, x_c, y_c, fill="red", width=1, tags=(str(parent_node.get_id()), "line"))#, dash=(5, 2))

        if parent_node in self._node_to_child_line_ids:
            self._node_to_child_line_ids[parent_node].add(line_id)
        else:
            self._node_to_child_line_ids[parent_node] = {line_id}

        if child_node in self._node_to_parent_line_ids:
            self._node_to_parent_line_ids[child_node].add(line_id)
        else:
            self._node_to_parent_line_ids[child_node] = {line_id}

        self._line_positions[line_id] = (x_p, y_p, x_c, y_c)

        logging.debug("node to child line ids %s", str(self._node_to_child_line_ids))
        logging.debug("node to parent line ids %s", str(self._node_to_parent_line_ids))

        canvas.tag_lower("line", "circle")


    def distance_from_node(self, x: int, y: int, node: Node):
        x_node: int = self._node_positions[node][0]
        y_node: int = self._node_positions[node][1]
        return math.sqrt((x-x_node)**2 + (y-y_node)**2)

    def find_node_at(self, x: int, y: int) -> Node|None:
        """Find the node under the given coordinates."""
        items: tuple[int, ...] = self._canvas.find_closest(x, y)
        if items:
            # The tags of the circle and text are the node object itself
            logging.debug(f"items: {items}")
            for item_id in items:
                tags = self._canvas.gettags(item_id)
                logging.debug(f"tags: {tags}")
                for tag in tags:
                    if tag.isdigit() and int(tag) in self._id_to_node and isinstance(self._id_to_node[int(tag)], Node):
                        node = self._id_to_node[int(tag)]
                        if self.distance_from_node(x, y, node) <= NODE_RADIUS:
                            return node
        return None

    def select_child_line_ids(self) -> None:
        logging.debug("num of selected child line ids: %d", len(self._selected_child_line_ids))
        assert len(self._selected_child_line_ids) == 0, "line ids are still selected!"
        for node in self._selected_nodes:
            if node in self._node_to_child_line_ids:
                for id in self._node_to_child_line_ids[node]:
                    if id not in self._selected_child_line_ids:
                        self._selected_child_line_ids.add(id)
        return 

    def select_parent_line_ids(self, child: Node) -> None:
        logging.debug("num of selected parent line ids: %d", len(self._selected_parent_line_ids))
        assert len(self._selected_parent_line_ids) == 0, "line ids are still selected!"
        if child in self._node_to_parent_line_ids:
            for id in self._node_to_parent_line_ids[child]:
                if id not in self._selected_parent_line_ids:
                    self._selected_parent_line_ids.add(id)
        return 

    def start_drag(self, event: tk.Event) -> None:
        """Start the drag operation."""
        selected_node: Node|None = self.find_node_at(event.x, event.y)
        if selected_node:
            logging.info("Starting drag")
            logging.debug("Selected Node value: %s", selected_node.get_value())
            self._selected_nodes.add(selected_node)
            children_r = selected_node.get_children_r()
            for child in children_r:
                self._selected_nodes.add(child)

            self.select_child_line_ids()
            self.select_parent_line_ids(selected_node)
            logging.debug("selected child line ids: %s", str(self._selected_child_line_ids))
            
            self._drag_start_x = event.x
            self._drag_start_y = event.y
        else:
            logging.info("No Nodes to drag")

    def drag(self, event: tk.Event) -> None:
        """Drag the selected node."""
        if len(self._selected_nodes) > 0:
            logging.info("Dragging")
            logging.debug("%d, %d",self._drag_start_x, self._drag_start_y)
            dx: int = event.x - self._drag_start_x
            dy: int = event.y - self._drag_start_y
            
            for selected_node in self._selected_nodes:
                # Get the stored information for the selected node
                if selected_node in self._node_positions:
                    old_x: int; old_y: int; circle_id: int; text_id: int
                    old_x, old_y, circle_id, text_id = self._node_positions[selected_node]

                    # Calculate new coordinates
                    new_x: int = old_x + dx
                    new_y: int = old_y + dy
                    x1: int = new_x - NODE_RADIUS
                    y1: int = new_y - NODE_RADIUS
                    x2: int = new_x + NODE_RADIUS
                    y2: int = new_y + NODE_RADIUS

                    # Move the circle and the text
                    self._canvas.coords(circle_id, x1, y1, x2, y2)
                    self._canvas.coords(text_id, new_x, new_y)

                    # Update the stored position
                    self._node_positions[selected_node] = (new_x, new_y, circle_id, text_id)

            x_p: int; y_p: int; x_c: int; y_c: int
            # Child Lines
            for line_id in self._selected_child_line_ids:
                if line_id in self._line_positions:
                    x_p, y_p, x_c, y_c = self._line_positions[line_id]
                    x_p += dx
                    y_p += dy
                    x_c += dx
                    y_c += dy
                    self._canvas.coords(line_id, x_p, y_p, x_c, y_c)
                    self._line_positions[line_id] = (x_p, y_p, x_c, y_c)
            # Parent Lines
            for line_id in self._selected_parent_line_ids:
                if line_id in self._line_positions:
                    x_p, y_p, x_c, y_c = self._line_positions[line_id]
                    x_c += dx
                    y_c += dy
                    self._canvas.coords(line_id, x_p, y_p, x_c, y_c)
                    self._line_positions[line_id] = (x_p, y_p, x_c, y_c)

            # Update drag start position for the next drag event
            self._drag_start_x = event.x
            self._drag_start_y = event.y
        else:
            logging.info("No Nodes dragging")

    def stop_drag(self, event: tk.Event) -> None:
        """Stop the drag operation."""
        if len(self._selected_nodes) > 0:
            logging.info("Stopping drag")
            self._selected_nodes.clear()
            self._selected_child_line_ids.clear()
            self._selected_parent_line_ids.clear()
            self._drag_start_x = 0
            self._drag_start_y = 0
        else:
            logging.info("No Nodes dragged")

    def run(self) -> None:
        self._window.mainloop()
