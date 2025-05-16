# Task-Grapher

Task-Grapher is a Python-based application that provides a graphical user interface for visualizing and managing hierarchical tasks. It allows users to create, organize, and manipulate tasks in a tree-like structure, making it easier to plan and track complex projects or workflows.

## Features

* **Task Visualization:** Displays tasks as nodes in a graph, clearly showing parent-child relationships.
* **Interactive GUI:** Uses Tkinter for a user-friendly interface with features like:
    * Node creation, deletion, and editing.
    * Drag-and-drop functionality for repositioning tasks.
    * Zoom and pan capabilities for navigating large task graphs.
    * Saving and loading task trees to/from files.
* **Tree Management:** Provides core functionalities to:
    * Add child tasks to existing tasks.
    * Delete tasks and their subtasks.
    * Maintain the hierarchical structure of tasks.

## Files

The project consists of the following main files:

* `main.py`:  The entry point of the application. It initializes the task tree and GUI, and sets up the main event loop.
* `gui.py`:  Implements the graphical user interface using Tkinter. It handles user interactions, displays the task graph, and provides functionalities for manipulating tasks.
* `node.py`: Defines the `Node` class, which represents a task in the task graph.  Each node can have a value/description, due date/time, and parent-child relationships with other nodes.

## Dependencies

* Python 3.x
* Tkinter (usually included with Python)

## How to Run

1.  Make sure you have Python 3.x installed.
2.  Save the files (`main.py`, `gui.py`, `node.py`) in the same directory.
3.  Run `main.py` from the command line:  `python main.py`

## Usage

* **Creating Tasks:** Right-click on a task node and select "Add Child" to create a subtask.  You'll be prompted to enter the task's name.
* **Deleting Tasks:** Right-click on a task node and select "Delete Node and Descendants" to delete the task and all its subtasks.
* **Moving Tasks:** Click and drag a task node to reposition it within the graph.
* **Saving/Loading:** Right-click on the canvas background to access the "Save Tree" and "Load Tree" options for persisting your task trees.
* **Zooming/Panning:** Use the 'j' and 'k' keys to zoom in and out, and the 'w', 'a', 's', 'd' keys or the middle mouse button to pan the view.

## Notes

* The application uses a spiral layout algorithm to automatically arrange task nodes in the graph.
* Logging is included for debugging purposes.
* The project is designed to be extensible, allowing for future enhancements such as task prioritization, dependencies, and more advanced visualization options.
