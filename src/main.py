from node import Node
from gui import Gui
import logging

def main():

    logging.basicConfig(level=logging.DEBUG)
    node_p: Node = Node("Morning Routine")
    graphics = Gui(node_p)
    graphics.draw_node(graphics._canvas, node_p, 200, 200)
    graphics.run()

    return

if __name__ == "__main__":
    main()
