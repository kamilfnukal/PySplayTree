class SplayTree:
    def __init__(self):
        self.root_node = None

    @staticmethod
    def split(node, value):
        if value < node.value:
            return node.left, Node(value=node.value, right=node.right)
        return Node(value=node.value, left=node.left), node.right

    @staticmethod
    def splay(node, value):
        header = Node(None)
        header_left = header_right = header
        yi = False

        while True:
            if value < node.value:
                if not node.left:
                    break
                if value < node.left.value:
                    node = node.rotate_right()
                    if not node.left:
                        break
                header_right.left = node  # link right
                header_right = node
                node = node.left
            elif value > node.value:
                if not node.right:
                    break
                if value > node.right.value:
                    node = node.rotate_left()
                    if not node.right:
                        break
                header_left.right = node  # link left
                header_left = node
                node = node.right
            else:
                break
            sent = yield node.value
            yi = True
            if sent is not None:
                break

        header_left.right = node.left  # assembly
        header_right.left = node.right
        node.left = header.right
        node.right = header.left
        if not yi:
            yield node.value
        return node

    def insert(self, value):
        if not self.root_node:
            self.root_node = Node(value)
            return

        if (yield from self.find(value)):
            return

        left_subtree, right_subtree = self.split(self.root_node, value)
        self.root_node = Node(value=value, left=left_subtree, right=right_subtree)

    def find(self, value):
        if not self.root_node:
            return False

        self.root_node = yield from self.splay(self.root_node, value)
        return self.root_node.value == value

    def erase(self, value):
        if not (yield from self.find(value)):
            return

        if not self.root_node.left:
            self.root_node = self.root_node.right
        else:
            right_subtree = self.root_node.right
            self.root_node = yield from self.splay(self.root_node.left, self.root_node.value)
            self.root_node.right = right_subtree

    @staticmethod
    def inorder(node):
        if not node:
            return

        yield from SplayTree.inorder(node.left)
        yield node.value
        yield from SplayTree.inorder(node.right)

    def __iter__(self):
        yield from self.inorder(self.root_node)

    def filter_rec(self, node, predicate):
        if not node:
            return

        if not predicate(node.value):
            yield from self.erase(node.value)
        yield from self.filter_rec(node.left, predicate)
        yield from self.filter_rec(node.right, predicate)

    def filter(self, predicate):
        assert predicate
        yield from self.filter_rec(self.root_node, predicate)

    def root(self):
        return self.root_node


class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

    def rotate_right(self):
        left_node = self.left
        self.left = left_node.right
        left_node.right = self
        return left_node

    def rotate_left(self):
        right_node = self.right
        self.right = right_node.left
        right_node.left = self
        return right_node