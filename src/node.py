class Node:

    def __init__(self, value: str) -> None:
        self._value: str = value
        self._children: list[Node] = []
        self._siblings: list[Node] = []
        self._parents: list[Node] = []

    def get_value(self) -> str:
        return self._value

    def set_value(self, new_value: str) -> str:
        self._value = new_value
        return self._value

    #def add_child(self, v)
