from src.node import Node
from src.gui import Gui
import logging

def main():

    logging.basicConfig(level=logging.DEBUG)
    node_p: Node = Node("Morning Routine")
    node_c: Node = Node("Brush My Teeth")
    _ = node_p.add_child(node_c)
    graphics = Gui(node_p)
    graphics.draw_node(graphics._canvas, node_p, 200, 200)
    graphics.draw_branch_and_child(graphics._canvas, node_p, node_c, 50, 50)
    graphics.run()

    return

if __name__ == "__main__":
    main()
