import tkinter as tk
from tkinter import simpledialog
from src.node import Node
from collections import deque
import logging
import math

NODE_RADIUS: float = 30.0#10
# RADIAL_SPACING: int = 100  # Adjust as needed for spacing between levels
# SPIRAL_FACTOR: float = 0.2  # Adjust to control the spiral effect
WIDTH: int = 1000
HEIGHT: int = 1000
BASE_DISTANCE: float = 500  # Base distance from parent to first child
DISTANCE_LEVEL_FACTOR: float = 0.55
ANGLE_INCREMENT: float = 2 * math.pi / 5  # Base angle between siblings (adjust for branching)
SPIRAL_FACTOR: float = 20#0.6  # Controls the spiral effect (angle offset per level)
ZOOM_FACTOR: float = 1.1


class Gui:

    def __init__(self, tree: Node):
        self._tree: Node = tree
        self._window: tk.Tk = tk.Tk()
        self._window.title("Task-Grapher")

        self._frame: tk.Frame = tk.Frame(self._window)
        self._frame.pack(fill=tk.BOTH, expand=True)

        self._h_scroll: tk.Scrollbar = tk.Scrollbar(self._frame, orient=tk.HORIZONTAL)
        self._h_scroll.pack(side=tk.BOTTOM, fill=tk.X)

        self._v_scroll: tk.Scrollbar = tk.Scrollbar(self._frame, orient=tk.VERTICAL)
        self._v_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        self._canvas = tk.Canvas(
            self._frame,
            width=WIDTH,
            height=HEIGHT,
            bg="white",
            xscrollcommand=self._h_scroll.set,
            yscrollcommand=self._v_scroll.set,
            scrollregion=(0, 0, WIDTH * 2, HEIGHT * 2)
        )
        self._canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.create_context_menu()

        self._h_scroll.config(command=self._canvas.xview)
        self._v_scroll.config(command=self._canvas.yview)

        #self._canvas: tk.Canvas = tk.Canvas(self._window, width=WIDTH, height=HEIGHT, bg="white")
        #self._canvas.pack()

        self._scale_factor: float = 1.0
        self._drag_start_x: float = 0.0
        self._drag_start_y: float = 0.0
        self._pan_start_x: float = 0.0
        self._pan_start_y: float = 0.0
        self._id_to_node: dict[int, Node] = {}
        
        self._optimal_node_positions: dict[Node, tuple[float, float]] = {} #each tuple consists of (x, y)
        self._node_positions: dict[Node, tuple[float, float, int, int]] = {} #each tuple consists of (x, y, circle_id, text_id)
        self._line_positions: dict[int, tuple[float, float, float, float]] = {} #each tuple consists of (xp, yp, xc, yc)

        self._node_to_child_line_ids: dict[Node, set[int]] = {}
        self._node_to_parent_line_ids: dict[Node, set[int]] = {}
        self._line_ids_to_nodes: dict[int, tuple[Node, Node]] = {} #line_id to tuple of (parent_node, child_node)

        self._selected_nodes: set[Node] = set()
        self._selected_child_line_ids: set[int] = set()
        self._selected_parent_line_ids: set[int] = set()
        self._selected_node: Node|None = None

        self.add_nodes()

        self._canvas.bind("<KeyPress-s>", lambda e: self.pan_canvas(0, -50))
        self._canvas.bind("<KeyPress-d>", lambda e: self.pan_canvas(-50, 0))
        self._canvas.bind("<KeyPress-w>", lambda e: self.pan_canvas(0, 50))
        self._canvas.bind("<KeyPress-a>", lambda e: self.pan_canvas(50, 0))
        self._canvas.bind("<Button-2>", self.start_pan)
        self._canvas.bind("<B2-Motion>", self.perform_pan)

        self._canvas.bind("<KeyPress-j>", self.zoom_in)
        self._canvas.bind("<KeyPress-k>", self.zoom_out)
        self._canvas.bind("<Button-1>", self.start_drag)
        self._canvas.bind("<B1-Motion>", self.drag)
        self._canvas.bind("<ButtonRelease-1>", self.stop_drag)

        self._canvas.config(highlightthickness=1)
        self._canvas.focus_set()
    
    def create_context_menu(self):
        self.context_menu: tk.Menu = tk.Menu(self._window, tearoff=0)
        #self.context_menu.add_command(label="Delete Singular Node", command=self.handle_delete_single_node)
        self.context_menu.add_command(label="Add Child", command=self.prompt_add_child)
        self.context_menu.add_command(label="Delete Node and Descendants", command=self.handle_delete_node_and_descendants)
        return

    def show_context_menu(self, event: tk.Event, node: Node):
        self._selected_node = node  # store reference for deletion or other ops
        self.context_menu.tk_popup(event.x_root, event.y_root)
        return

    def prompt_add_child(self):
        if self._selected_node:
            value = simpledialog.askstring("New Task", "Enter name for the new task:")
            if value is not None:
                child = Node(value)
                added = self._selected_node.add_child(child)
                if added:
                    _ = self.add_node(child)
                    self.draw_branch_and_child(self._canvas, self._selected_node, child, 0, 100)
            self._selected_node = None

    def handle_delete_single_node(self):
        if self._selected_node:
            self.delete_node_from_canvas(self._selected_node)
            self._selected_node = None
        return

    def handle_delete_node_and_descendants(self):
        if self._selected_node:
            self.delete_node_and_descendants(self._selected_node)
            self._selected_node = None
        return

    def delete_node_and_descendants(self, n: Node) -> None:
        """Deletes Node and Descendants from Canvas and Tree"""

        def recursive_remove(node: Node) -> None:
            children_lst_copy = node.get_children().copy()
            for child in children_lst_copy:
                recursive_remove(child)
            self.delete_node_from_canvas(node)
            node.remove_from_tree()
            return

        recursive_remove(n)
        return

    def delete_node_from_canvas(self, node: Node) -> None:
        """Deletes Node and Surrounding Lines from Canvas"""

        #remove reference of line from each parent
        if node in self._node_to_parent_line_ids:
            for l_id in self._node_to_parent_line_ids[node]:
                p: Node = self._line_ids_to_nodes[l_id][0]
                #if l_id in self._node_to_child_line_ids[p]:
                self._node_to_child_line_ids[p].remove(l_id) #remove reference of line from parent
                del self._line_ids_to_nodes[l_id] #remove reference of line from map
                del self._line_positions[l_id]
                self._canvas.delete(l_id)
            #self._node_to_parent_line_ids[node].clear() #remove reference of all parent lines from node
            del self._node_to_parent_line_ids[node]
            
        #remove reference of line from each child
        if node in self._node_to_child_line_ids:
            for l_id in self._node_to_child_line_ids[node]:
                c: Node = self._line_ids_to_nodes[l_id][1]
                #if l_id in self._node_to_parent_line_ids[c]:
                self._node_to_parent_line_ids[c].remove(l_id) #remove reference of line from child
                del self._line_ids_to_nodes[l_id] #remove reference of line from map
                del self._line_positions[l_id]
                self._canvas.delete(l_id)
            #self._node_to_child_line_ids[node].clear() #remove reference of all child lines from node
            del self._node_to_child_line_ids[node]

        _, _, c_id, t_id = self._node_positions[node]
        self._canvas.tag_unbind(c_id, "<Button-3>")
        self._canvas.delete(c_id)
        self._canvas.delete(t_id)
        del self._node_positions[node]

        if node in self._optimal_node_positions:
            del self._optimal_node_positions[node]
        
        del self._id_to_node[node.get_id()]

        #node.remove_from_tree()
        #del node
        return

    def event_to_canvas_coords(self, event: tk.Event) -> tuple[float, float]:
        # Use canvas center if we don't have event coordinates
        x: float
        y: float
        if event.x == 0 and event.y == 0:
            x, y = self._canvas.winfo_width() / 2, self._canvas.winfo_height() / 2
        else:
            x, y = float(self._canvas.canvasx(event.x)), float(self._canvas.canvasy(event.y))
        logging.debug(f"Canvas Coords: {x}, {y}")
        return x, y

    def pan_canvas(self, dx: float, dy: float) -> None:
        # Move all canvas elements visually
        self._canvas.move("all", dx, dy)

        # Move node positions
        for node, (x, y, cid, tid) in self._node_positions.items():
            new_x = x + dx
            new_y = y + dy
            self._node_positions[node] = (new_x, new_y, cid, tid)

        # Move line positions
        for line_id, (x_p, y_p, x_c, y_c) in self._line_positions.items():
            new_x_p = x_p + dx
            new_y_p = y_p + dy
            new_x_c = x_c + dx
            new_y_c = y_c + dy
            self._line_positions[line_id] = (new_x_p, new_y_p, new_x_c, new_y_c)

    def start_pan(self, event: tk.Event) -> None:
        self._canvas.focus_set()
        self._pan_start_x = self._canvas.canvasx(event.x)
        self._pan_start_y = self._canvas.canvasy(event.y)
        return

    def perform_pan(self, event: tk.Event) -> None:
        new_x = self._canvas.canvasx(event.x)
        new_y = self._canvas.canvasy(event.y)
        dx = new_x - self._pan_start_x
        dy = new_y - self._pan_start_y
        self._pan_start_x = new_x
        self._pan_start_y = new_y
        self.pan_canvas(dx, dy)
        return

    def zoom_in(self, event: tk.Event):
        x, y = self.event_to_canvas_coords(event)
        factor = ZOOM_FACTOR
        #updating internal tracker of scale factor
        self._scale_factor *= factor
        #scale all objects
        self._canvas.scale("all", x, y, factor, factor)

        # Update node positions
        for node, (nx, ny, cid, tid) in self._node_positions.items():
            dx = nx - x
            dy = ny - y
            new_x = x + dx * factor
            new_y = y + dy * factor
            self._node_positions[node] = (new_x, new_y, cid, tid)

        # Update line positions
        for line_id, (x_p, y_p, x_c, y_c) in self._line_positions.items():
            dx_p = x_p - x
            dy_p = y_p - y
            dx_c = x_c - x
            dy_c = y_c - y
            new_x_p = x + dx_p * factor
            new_y_p = y + dy_p * factor
            new_x_c = x + dx_c * factor
            new_y_c = y + dy_c * factor
            self._line_positions[line_id] = (new_x_p, new_y_p, new_x_c, new_y_c)
        
        return

    def zoom_out(self, event: tk.Event):
        x, y = self.event_to_canvas_coords(event)
        factor = 1 / ZOOM_FACTOR
        #updating internal tracker of scale factor
        self._scale_factor *= factor
        #scale all objects
        self._canvas.scale("all", x, y, factor, factor)

        # Update node positions
        for node, (nx, ny, cid, tid) in self._node_positions.items():
            dx = nx - x
            dy = ny - y
            new_x = x + dx * factor
            new_y = y + dy * factor
            self._node_positions[node] = (new_x, new_y, cid, tid)

        # Update line positions
        for line_id, (x_p, y_p, x_c, y_c) in self._line_positions.items():
            dx_p = x_p - x
            dy_p = y_p - y
            dx_c = x_c - x
            dy_c = y_c - y
            new_x_p = x + dx_p * factor
            new_y_p = y + dy_p * factor
            new_x_c = x + dx_c * factor
            new_y_c = y + dy_c * factor
            self._line_positions[line_id] = (new_x_p, new_y_p, new_x_c, new_y_c)
        
        return

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

        def calculate_child_positions(parent_node: Node, parent_x: float, parent_y: float, level: int, visited: set[Node], start_angle_offset: float = 0):
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
        root_x: float = WIDTH/2#200
        root_y: float = HEIGHT/2#200
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

    def draw_node(self, canvas: tk.Canvas, node: Node, x: float, y: float) -> None:
        x1: float = x - NODE_RADIUS
        y1: float = y - NODE_RADIUS
        x2: float = x + NODE_RADIUS
        y2: float = y + NODE_RADIUS
        circle_id: int = canvas.create_oval(x1, y1, x2, y2, fill="blue", outline="black", tags=(str(node.get_id()), "circle"))
        text_id: int = canvas.create_text(x, y, text=node.get_value(), fill="white", font=("Arial", 6), tags=(str(node.get_id()), "text"))
        self._node_positions[node] = (x, y, circle_id, text_id)
        self._canvas.tag_bind(circle_id, "<Button-3>", lambda event, n=node: self.show_context_menu(event, n))

        logging.info("Drawing Node: %d", node.get_id())
        logging.debug("Position: %d,%d, Circle_Id: %d, Text_Id: %d", x, y, circle_id, text_id)

    def draw_branch_and_child(self, canvas: tk.Canvas, parent_node: Node, child_node: Node, dx: float, dy: float) -> None:
        x_p: float; y_p: float
        x_p, y_p = self._node_positions[parent_node][:2]
        x_c: float; y_c: float
        x_c, y_c = x_p + dx, y_p + dy
        self.draw_node(canvas, child_node, x_c, y_c)
        line_id:int = canvas.create_line(x_p, y_p, x_c, y_c, fill="red", width=1, tags=(str(parent_node.get_id()), "line"))#, dash=(5, 2))
        
        self._line_ids_to_nodes[line_id] = (parent_node, child_node)

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


    def distance_from_node(self, x: float, y: float, node: Node):
        x_node: float = self._node_positions[node][0]
        y_node: float = self._node_positions[node][1]
        return math.sqrt((x-x_node)**2 + (y-y_node)**2)

    def find_node_at(self, x: float, y: float) -> Node|None:
        """Find the node under the given canvas coordinates."""
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
                        if self.distance_from_node(x, y, node) <= NODE_RADIUS * self._scale_factor:
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
        #focus to canvas window for keypresses after mouse click
        self._canvas.focus_set()
        x, y = self.event_to_canvas_coords(event)
        selected_node: Node|None = self.find_node_at(x, y)
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
            
            self._drag_start_x = x
            self._drag_start_y = y
        else:
            logging.info("No Nodes to drag")

    def drag(self, event: tk.Event) -> None:
        """Drag the selected node."""
        if len(self._selected_nodes) > 0:
            logging.info("Dragging")
            logging.debug("%d, %d",self._drag_start_x, self._drag_start_y)
            x, y = self.event_to_canvas_coords(event)
            dx: float = x - self._drag_start_x
            dy: float = y - self._drag_start_y
            
            for selected_node in self._selected_nodes:
                # Get the stored information for the selected node
                if selected_node in self._node_positions:
                    old_x: float; old_y: float; circle_id: int; text_id: int
                    old_x, old_y, circle_id, text_id = self._node_positions[selected_node]

                    # Calculate new coordinates
                    new_x: float = old_x + dx
                    new_y: float = old_y + dy
                    x1: float = new_x - NODE_RADIUS
                    y1: float = new_y - NODE_RADIUS
                    x2: float = new_x + NODE_RADIUS
                    y2: float = new_y + NODE_RADIUS

                    # Move the circle and the text
                    #self._canvas.coords(circle_id, x1, y1, x2, y2)
                    #self._canvas.coords(text_id, new_x, new_y)
                    self._canvas.move(circle_id, dx, dy)
                    self._canvas.move(text_id, dx, dy)
                    #could use self._canvas.move instead

                    # Update the stored position
                    self._node_positions[selected_node] = (new_x, new_y, circle_id, text_id)

            x_p: float; y_p: float; x_c: float; y_c: float 
            # Child Lines
            for line_id in self._selected_child_line_ids:
                if line_id in self._line_positions:
                    x_p, y_p, x_c, y_c = self._line_positions[line_id]
                    x_p += dx
                    y_p += dy
                    x_c += dx
                    y_c += dy
                    #self._canvas.coords(line_id, x_p, y_p, x_c, y_c)
                    self._canvas.move(line_id, dx, dy)
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
            self._drag_start_x = x
            self._drag_start_y = y
        else:
            logging.info("No Nodes dragging")

    def stop_drag(self, event: tk.Event) -> None:
        """Stop the drag operation."""
        if len(self._selected_nodes) > 0:
            logging.info("Stopping drag")
            self._selected_nodes.clear()
            self._selected_child_line_ids.clear()
            self._selected_parent_line_ids.clear()
            self._drag_start_x = 0.0
            self._drag_start_y = 0.0
        else:
            logging.info("No Nodes dragged")

    def run(self) -> None:
        self._window.mainloop()
