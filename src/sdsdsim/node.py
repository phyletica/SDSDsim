#! /usr/bin/env python

from io import StringIO
import copy

class Node(object):

    def __init__(self, **kwargs):
        self._children = []
        self._parent = None
        self.label = kwargs.pop("label", None)
        self.time = kwargs.pop("time", None)
        self._seed_time = None
        self.rootward_state = kwargs.pop("rootward_state", None)
        self.state_changes = []
        self.state_change_times = []
        self.is_extinct = False
        self.is_burst_node = False
        if kwargs:
            raise TypeError(f"Unsupported keyword arguments: {kwargs}")

    def _get_parent(self):
        return self._parent

    def _set_parent(self, node):
        if self._parent is not None:
            self._parent._children.remove(self)
        self._parent = node
        if self._parent is not None:
            if self not in self._parent._children:
                self._parent._children.append(self)

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
        node._parent = None
        self._children.remove(node)

    def _get_leafward_state(self):
        if not self.state_changes:
            if self.rootward_state is None:
                raise Exception("Node has no state")
            return self.rootward_state
        else:
            return self.state_changes[-1][-1]

    leafward_state = property(_get_leafward_state)

    def transition_state(self, new_state, time):
        transition = (self.leafward_state, new_state)
        self.state_changes.append(transition)
        self.state_change_times.append(time)

    def _get_leafward_state_history(self):
        if self.rootward_state is None:
            raise Exception("Node has no character-state history")
        if len(self.state_changes) == 0:
            return ((self.rootward_state, self.branch_length),)
        history = []
        current_time = None
        if self.is_root:
            current_time = self.seed_time
        else:
            current_time = self.parent.time
        for i, (current_state, next_state) in enumerate(self.state_changes):
            duration = self.state_change_times[i] - current_time
            history.append((current_state, duration))
            current_time = self.state_change_times[i]
        assert next_state == self.leafward_state
        duration = self.time - current_time
        history.append((next_state, duration))
        return tuple(history)

    leafward_state_history = property(_get_leafward_state_history)

    @staticmethod
    def as_simmap_string(node, include_label = True):
        s = StringIO()
        if (node.label is not None) and include_label:
            s.write(f"{node.label}")
        s.write(":{")
        s.write(
            ":".join(f"{k},{d}" for k, d in node.leafward_state_history)
        )
        s.write("}")
        return s.getvalue()

    @staticmethod
    def as_length_string(node, include_label = True):
        if (node.label is not None) and include_label:
            return f"{node.label}:{node.branch_length}"
        return f":{node.branch_length}"

    def _get_children(self):
        return self._children

    children = property(_get_children)

    def _get_is_root(self):
        return self._parent is None

    is_root = property(_get_is_root)

    def _get_is_leaf(self):
        return len(self._children) == 0

    is_leaf = property(_get_is_leaf)

    def _get_seed_time(self):
        return self._seed_time

    def _get_n_leaves(self):
        n = 0
        for l in self.leaf_iter():
            n += 1
        return n

    number_of_leaves = property(_get_n_leaves)

    def _get_n_extant_leaves(self):
        n = 0
        for l in self.leaf_iter():
            if not l.is_extinct:
                n += 1
        return n

    number_of_extant_leaves = property(_get_n_extant_leaves)

    def _get_n_extinct_leaves(self):
        n = 0
        for l in self.leaf_iter():
            if l.is_extinct:
                n += 1
        return n

    number_of_extinct_leaves = property(_get_n_extinct_leaves)

    def _set_seed_time(self, time):
        if not self.is_root:
            raise Exception("seed time should only be set for a root node")
        self._seed_time = time

    seed_time = property(_get_seed_time, _set_seed_time)

    def _get_branch_length(self):
        if self._parent is None:
            if self.seed_time is None:
                return 0.0
            return self.time - self.seed_time
        if (self.time is not None) and (self.parent.time is not None):
            return self.time - self.parent.time
        raise Exception("node or parent lacking info to calc branch length")

    branch_length = property(_get_branch_length)

    def _get_root(self):
        if self.is_root:
            return self
        for node in self.ancestor_iter():
            pass
        assert node.is_root
        return node

    root = property(_get_root)

    def _get_max_time(self):
        r = self.root
        return max(leaf.time for leaf in r.leaf_iter())

    max_time = property(_get_max_time)

    def _get_height(self):
        return self.max_time - self.time

    height = property(_get_height)

    def is_ancestor(self, node):
        if self.is_root:
            return False
        for n in self.ancestor_iter():
            if n is node:
                return True
        return False

    def _get_tree_length(self):
        l = 0.0
        for node in self:
            if node is self:
                continue
            l += node.branch_length
        return l

    tree_length = property(_get_tree_length)

    def __iter__(self):
        return self.leafward_iter()

    def leafward_iter(self):
        """
        Pre-order traversal over descending nodes.

        Visits nodes leafward (each parent is visited before its children)

        Modified from Node.preorder_iter from Dendropy:
        https://github.com/jeetsukumaran/DendroPy/blob/cc82ab774ed83831b5c5125278d88c3c614c2d8a/src/dendropy/datamodel/treemodel/_node.py#L103
        """
        stack = [self]
        while stack:
            node = stack.pop()
            yield node
            stack.extend(reversed(node.children))

    def internal_leafward_iter(self):
        """
        Pre-order traversal over descending internal nodes (leaves are skipped).

        Visits nodes leafward (each parent is visited before its children)
        """
        for n in self.leafward_iter():
            if n.is_leaf:
                continue
            yield n

    def rootward_iter(self):
        """
        Post-order traversal over descending nodes.

        Visits nodes rootward (each parent is visited after its children)

        Modified from Node.postorder_iter from Dendropy:
        https://github.com/jeetsukumaran/DendroPy/blob/cc82ab774ed83831b5c5125278d88c3c614c2d8a/src/dendropy/datamodel/treemodel/_node.py#L171
        """
        stack = [(self, False)]
        while stack:
            node, state = stack.pop()
            if state:
                yield node
            else:
                stack.append((node, True))
                stack.extend([(n, False) for n in reversed(node.children)])

    def internal_rootward_iter(self):
        """
        Post-order traversal over descending internal nodes (leaves are skipped).

        Visits nodes rootward (each parent is visited after its children)
        """
        for n in self.rootward_iter():
            if n.is_leaf:
                continue
            yield n

    def leaf_iter(self):
        """
        Iterate over all leaves that descend from this node.
        """
        for n in self.rootward_iter():
            if not n.is_leaf:
                continue
            yield n

    def ancestor_iter(self):
        node = self
        while node is not None:
            node = node._parent
            if node is not None:
                yield node

    def _write_newick(self, out, include_root_annotations, branch_annot_func):
        if self.is_root and include_root_annotations:
            out.write("(")
        if self.is_leaf:
            out.write(f"{branch_annot_func(self, include_label = True)}")
        else:
            out.write("(");
            for i, child in enumerate(self._children):
                if i > 0:
                    out.write(",")
                child._write_newick(
                    out = out,
                    include_root_annotations = include_root_annotations,
                    branch_annot_func = branch_annot_func,
                )
            if self.is_root and (not include_root_annotations):
                out.write(f")");
            else:
                out.write(f"){branch_annot_func(self, include_label = False)}");
            if self.is_root and include_root_annotations:
                out.write(f")");

    def write_newick_simmap(self, out, include_root_annotations = True):
        self._write_newick(
            out = out,
            include_root_annotations = include_root_annotations,
            branch_annot_func = Node.as_simmap_string,
        )

    def write_newick_simple(self, out, include_root_annotations = True):
        self._write_newick(
            out = out,
            include_root_annotations = include_root_annotations,
            branch_annot_func = Node.as_length_string,
        )

    def write_newick(self, out, include_root_annotations = True):
        self.write_newick_simmap(out, include_root_annotations)

    def _as_newick_string(self, include_root_annotations, branch_annot_func):
        out = StringIO()
        self._write_newick(
            out = out,
            include_root_annotations = include_root_annotations,
            branch_annot_func = branch_annot_func,
        )
        out.write(";")
        return out.getvalue()

    def as_newick_simmap_string(self, include_root_annotations = True):
        return self._as_newick_string(
            include_root_annotations = include_root_annotations,
            branch_annot_func = Node.as_simmap_string,
        )

    def as_newick_simple_string(self, include_root_annotations = True):
        return self._as_newick_string(
            include_root_annotations = include_root_annotations,
            branch_annot_func = Node.as_length_string,
        )

    def as_newick_string(self, include_root_annotations = True):
        return self.as_newick_simmap_string(include_root_annotations)

    def __str__(self):
        return self.as_newick_string()

    def _get_has_extant_leaves(self):
        for node in self.leaf_iter():
            if not node.is_extinct:
                return True
        return False

    has_extant_leaves = property(_get_has_extant_leaves)

    def _prune_first_extinct_clade(self, node):
        for n in node.leafward_iter():
            if not n.has_extant_leaves:
                p = n.parent
                p.remove_child(n)
                return n
        return None

    def prune_extinct_leaves(self):
        if not self.has_extant_leaves:
            return None
        new_root = copy.deepcopy(self)
        pruned = True
        while pruned is not None:
            pruned = self._prune_first_extinct_clade(new_root)
        return new_root.remove_unifurcations()

    def remove_unifurcations(self):
        new_root = copy.deepcopy(self)
        uni_nodes = [n for n in new_root if len(n._children) == 1]
        for node in uni_nodes:
            child = node._children[0]
            child.rootward_state = node.rootward_state
            child.state_changes = node.state_changes + child.state_changes
            child.state_change_times = node.state_change_times + child.state_change_times
            if node.parent is not None:
                p = node.parent
                p._children.remove(node)
                p.add_child(child)
                node._parent = None
                node._children = []
            else:
                assert node is new_root
                child._seed_time = node._seed_time
                child._parent = None
                node._children = []
                new_root = child
        return new_root
