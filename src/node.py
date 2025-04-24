from datetime import datetime, date, time

class Node:

    def __init__(self, value: str, due_date: date|None=None, due_time: time|None=None) -> None:
        self._value: str = value
        self._created: datetime = datetime.now()
        self._due_date: date|None = due_date
        self._due_time: time|None = due_time
        self._completed: bool = False

        self._children: list[Node] = []
        self._siblings: list[Node] = []
        self._parents: list[Node] = []
        self._max_children: int = 4
        self._max_parents: int = 4
        #self._time

    def get_value(self) -> str:
        return self._value

    def set_value(self, new_value: str) -> str:
        self._value = new_value
        return self._value

    def get_due_date(self) -> date|None:
        return self._due_date

    def set_due_date(self, new_date: date) -> date|None:
        self._due_date = new_date
        return self._due_date

    def get_due_time(self) -> time|None:
        return self._due_time

    def set_due_time(self, new_time: time) -> time|None:
        self._due_time = new_time
        return self._due_time

    #def add_child(self, child: Node) -> 
