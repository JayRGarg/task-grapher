from datetime import datetime, date, time
from typing import Self, Iterator
import itertools
from collections import deque
import logging

class Node:

    id_iter: Iterator[int] = itertools.count()

    def __init__(self, value: str, due_date: date|None=None, due_time: time|None=None) -> None:
        if not isinstance(value, str):
            raise TypeError(f"Node value must be a string, not a {type(value)}.")
        if not isinstance(due_date, (date, type(None))):
            raise TypeError(f"Node date must be a date or None, not a {type(due_date)}.")
        if not isinstance(due_time, (time, type(None))):
            raise TypeError(f"Node time must be a time or None, not a {type(due_time)}.")

        self._id: int = next(Node.id_iter)
        self._value: str = value
        self._created: datetime = datetime.now()
        self._due_date: date|None = due_date
        self._due_time: time|None = due_time
        self._completed: bool = False

        self._children: list[Self] = []
        #self._siblings: list[Self] = []
        self._parents: list[Self] = []
        self._max_children: int = 4
        self._max_parents: int = 4
        #self._time

    def get_id(self) -> int:
        return self._id

    def get_value(self) -> str:
        return self._value

    def set_value(self, new_value: str) -> str:
        if not isinstance(new_value, str):
            raise TypeError(f"Node value must be a string, not a {type(new_value)}.")
        self._value = new_value
        return self._value

    def get_due_date(self) -> date|None:
        return self._due_date

    def set_due_date(self, new_date: date) -> date|None:
        if not isinstance(new_date, date):
            raise TypeError(f"Node date must be a date, not a {type(new_date)}.")
        self._due_date = new_date
        return self._due_date

    def get_due_time(self) -> time|None:
        return self._due_time

    def set_due_time(self, new_time: time) -> time|None:
        if not isinstance(new_time, time):
            raise TypeError(f"Node time must be a time, not a {type(new_time)}.")
        self._due_time = new_time
        return self._due_time

    def get_children(self) -> list[Self]:
        logging.debug(print([c._value for c in self._children]))
        return self._children

    def get_parents(self) -> list[Self]:
        return self._parents

    def add_child(self, child: Self) -> bool:
        if not (child in self._children) \
                and len(self._children) < self._max_children \
                and len(child._parents) < child._max_parents:
            self._children.append(child)
            child._parents.append(self)
        if child in self._children:
            assert (self in child._parents), "Parent missing in Child's Parent List?"
        return (child in self._children) and (self in child._parents)

    def get_children_r(self) -> list[Self]:
        visited: set[Self] = set()
        stack: deque[Self] = deque()
        for child in self.get_children():
            visited.add(child)
            stack.append(child)

        while stack:
            curr: Self = stack.pop()
            for child in curr.get_children():
                if child is not self and child not in visited:
                    visited.add(child)
                    stack.append(child)

        return list(visited)

    def remove_from_tree(self) -> None:
        """
        Removes this node from its parents' children lists and clears references
        to and from its children.
        """
        # 1. Remove from parents
        for parent in list(self._parents):
            if self in parent._children:
                parent._children.remove(self)
        self._parents = []

        # 2. Clear references to children and remove parent reference from children
        for child in list(self._children):  # Iterate over a copy
            if self in child._parents:
                child._parents.remove(self)
        self._children = []
        return

