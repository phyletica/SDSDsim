#! /usr/bin/env python


class Node(object):

    def __init__(self, **kwargs):
        self._children = []
        self._parent = None
        self.label = kwargs.pop("label", None)
        self.time = kwargs.pop("time", None)
        self.height = None
        self.rootward_state = kwargs.pop("rootward_state", None)
        self.state_changes = []
        self.state_change_times = []
        if "parent" in kwargs:
            n = kwargs.pop("parent")
            self.parent = n
        if kwargs:
            raise TypeError(f"Unsupported keyword arguments: {kwargs}")

    def _get_parent(self):
        return self._parent

    def _set_parent(self, node):
        if self._parent is not None:
            self._parent._children.remove(self)
        self._parent = node
        if self._parent is not None:
            if self. not in self._parent._children:
                self._parent._children.appedn(self)

    parent = property(_get_parent, _set_parent)

    def add_child(self, node):
        if node is self:
            raise ValueError("Node cannot be its own child")
        if self.parent is node:
            raise ValueError("Parent of node cannot also be its child")
        node.parent = self
        if node not in self._children:
            self._children.append(node)

    def remove_child(self, node):
        if node not in self._children:
            raise ValueError("Child node to remove is not a child")
        node.parent = None
        self._children.remove(node)
