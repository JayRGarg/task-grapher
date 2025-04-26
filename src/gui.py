import tkinter as tk
from node import Node
from collections import deque

NODE_RADIUS: int = 30

class Gui:

    def __init__(self, tree: Node):
        self._tree: Node = tree
        self._window: tk.Tk = tk.Tk()
        self._window.title("Task-Grapher")
        self._canvas: tk.Canvas = tk.Canvas(self._window, width=400, height=400, bg="white")
        self._canvas.pack()
        self._drag_start_x: int = 0
        self._drag_start_y: int = 0
        self._id_to_node: dict[str, Node] = {}
        self._node_positions: dict[Node, tuple[int, int, int, int]] = {}
        self._selected_node: Node|None = None

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
        self._id_to_node[node.get_id()] = node
        return node 

    def draw_node(self, canvas: tk.Canvas, node: Node, x: int, y: int):
        x1: int = x - NODE_RADIUS
        y1: int = y - NODE_RADIUS
        x2: int = x + NODE_RADIUS
        y2: int = y + NODE_RADIUS
        circle_id: int = canvas.create_oval(x1, y1, x2, y2, fill="blue", outline="black", tags=node.get_id())
        text_id: int = canvas.create_text(x, y, text=node.get_value(), fill="white", font=("Arial", 6), tags=node.get_id())
        self._node_positions[node] = (x, y, circle_id, text_id)

    def find_node_at(self, x: int, y: int) -> Node|None:
        """Find the node under the given coordinates."""
        items: tuple[int, ...] = self._canvas.find_closest(x, y)
        if items:
            # The tags of the circle and text are the node object itself
            for item_id in items:
                tags = self._canvas.gettags(item_id)
                print(tags)
                for tag in tags:
                    if isinstance(self._id_to_node[tag], Node):
                        return self._id_to_node[tag]
        return None

    def start_drag(self, event: tk.Event) -> None:
        """Start the drag operation."""
        print("starting drag")
        self._selected_node = self.find_node_at(event.x, event.y)
        if self._selected_node:
            print(self._selected_node.get_value())
            self._drag_start_x = event.x
            self._drag_start_y = event.y

    def drag(self, event: tk.Event) -> None:
        """Drag the selected node."""
        print("dragging")
        if self._selected_node:
            dx: int = event.x - self._drag_start_x
            dy: int = event.y - self._drag_start_y

            # Get the stored information for the selected node
            if self._selected_node in self._node_positions:
                old_x: int; old_y: int; circle_id: int; text_id: int
                old_x, old_y, circle_id, text_id = self._node_positions[self._selected_node]

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
                self._node_positions[self._selected_node] = (new_x, new_y, circle_id, text_id)

                # Update drag start position for the next drag event
                self._drag_start_x = event.x
                self._drag_start_y = event.y

    def stop_drag(self, event: tk.Event) -> None:
        """Stop the drag operation."""
        print("stopping drag")
        self._selected_node = None
        self._drag_start_x = 0
        self._drag_start_y = 0

    def run(self) -> None:
        self._window.mainloop()
