"""Assignment 2: Trees for Treemap

=== CSC148 Winter 2019 ===
This code is provided solely for the personal and private use of
students taking the CSC148 course at the University of Toronto.
Copying for purposes other than this use is expressly prohibited.
All forms of distribution of this code, whether as given or with
any changes, are expressly prohibited.

All of the files in this directory and all sub-directories are:
Copyright (c) 2019 Bogdan Simion, David Liu, Diane Horton, Jacqueline Smith

=== Module Description ===
This module contains the basic tree interface required by the treemap
visualiser. You will both add to the abstract class, and complete a
concrete implementation of a subclass to represent files and folders on your
computer's file system.
"""
from __future__ import annotations
import os
import math
from random import randint
from typing import List, Tuple, Optional


class TMTree:
    """A TreeMappableTree: a tree that is compatible with the treemap
    visualiser.

    This is an abstract class that should not be instantiated directly.

    You may NOT add any attributes, public or private, to this class.
    However, part of this assignment will involve you implementing new public
    *methods* for this interface.
    You should not add any new public methods other than those required by
    the client code.
    You can, however, freely add private methods as needed.

    === Public Attributes ===
    rect:
        The pygame rectangle representing this node in the treemap
        visualization.
    data_size:
        The size of the data represented by this tree.

    === Private Attributes ===
    _colour:
        The RGB colour value of the root of this tree.
    _name:
        The root value of this tree, or None if this tree is empty.
    _subtrees:
        The subtrees of this tree.
    _parent_tree:
        The parent tree of this tree; i.e., the tree that contains this tree
        as a subtree, or None if this tree is not part of a larger tree.
    _expanded:
        Whether or not this tree is considered expanded for visualization.

    === Representation Invariants ===
    - data_size >= 0
    - If _subtrees is not empty, then data_size is equal to the sum of the
      data_size of each subtree.

    - _colour's elements are each in the range 0-255.

    - If _name is None, then _subtrees is empty, _parent_tree is None, and
      data_size is 0.
      This setting of attributes represents an empty tree.

    - if _parent_tree is not None, then self is in _parent_tree._subtrees

    - if _expanded is True, then _parent_tree._expanded is True
    - if _expanded is False, then _expanded is False for every tree
      in _subtrees
    - if _subtrees is empty, then _expanded is False
    """

    rect: Tuple[int, int, int, int]
    data_size: int
    _colour: Tuple[int, int, int]
    _name: Optional[str]
    _subtrees: List[TMTree]
    _parent_tree: Optional[TMTree]
    _expanded: bool

    def __init__(self, name: str, subtrees: List[TMTree],
                 data_size: int = 0) -> None:
        """Initialize a new TMTree with a random colour and the provided <name>.

        If <subtrees> is empty, use <data_size> to initialize this tree's
        data_size.

        If <subtrees> is not empty, ignore the parameter <data_size>,
        and calculate this tree's data_size instead.

        Set this tree as the parent for each of its subtrees.

        Precondition: if <name> is None, then <subtrees> is empty.
        """
        self.rect = (0, 0, 0, 0)
        self._name = name
        self._subtrees = subtrees[:]
        self._parent_tree = None
        self._expanded = False

        # 1. Initialize self._colour and self.data_size, according to the
        # docstring.
        # 2. Set this tree as the parent for each of its subtrees.

        self._colour = (randint(0, 255), randint(0, 255), randint(0, 255))
        # if it's not a folder, then use the passed in file size
        if len(self._subtrees) == 0:
            self.data_size = data_size
        else:  # loop through all the trees and add all the sizes together
            for subtree in self._subtrees:
                subtree._parent_tree = self
            self.data_size = sum([tree.data_size for tree in self._subtrees])

    def is_empty(self) -> bool:
        """Return True iff this tree is empty.
        """
        return self._name is None

    def update_rectangles(self, rect: Tuple[int, int, int, int]) -> None:
        """Update the rectangles in this tree and its descendents using the
        treemap algorithm to fill the area defined by pygame rectangle <rect>.
        """
        # Read the handout carefully to help get started identifying base cases,
        # then write the outline of a recursive step.
        #
        # Programming tip: use "tuple unpacking assignment" to easily extract
        # elements of a rectangle, as follows.
        # x, y, width, height = rect

        if self.data_size == 0 or self.is_empty():
            self.rect = (0, 0, 0, 0)
        else:
            self.rect = rect
            x, y, width, height = rect
            pre_width, pre_height = 0, 0

            for subtree in self._subtrees:

                new_width = int((subtree.data_size / self.data_size) * width)
                new_height = int((subtree.data_size / self.data_size) * height)

                if subtree == self._subtrees[-1]:
                    new_width = abs(width - pre_width)
                    new_height = abs(height - pre_height)

                if width > height:
                    subtree.update_rectangles((x, y, new_width, height))
                    pre_width += new_width
                    x += new_width
                else:
                    subtree.update_rectangles((x, y, width, new_height))
                    pre_height += new_height
                    y += new_height

    def get_rectangles(self) -> List[Tuple[Tuple[int, int, int, int],
                                           Tuple[int, int, int]]]:
        """Return a list with tuples for every leaf in the displayed-tree
        rooted at this tree. Each tuple consists of a tuple that defines the
        appropriate pygame rectangle to display for a leaf, and the colour
        to fill it with.
        """
        # I returned every rectangle in the displayed tree (leaf or not)???
        if self.is_empty():
            return []
        elif not self._expanded:
            return [(self.rect, self._colour)]
        else:
            a = []
            for subtrees in self._subtrees:
                a.extend(subtrees.get_rectangles())
            return a

    def get_tree_at_position(self, pos: Tuple[int, int]) -> Optional[TMTree]:
        """Return the leaf in the displayed-tree rooted at this tree whose
        rectangle contains position <pos>, or None if <pos> is outside of this
        tree's rectangle.

        If <pos> is on the shared edge between two rectangles, return the
        tree represented by the rectangle that is closer to the origin.
        """
        if self.is_empty():
            return None
        elif pos[0] > (self.rect[2] + self.rect[0]) \
                or pos[1] > \
                (self.rect[3] + self.rect[1]) and self._parent_tree is None:
            return None
        elif not self._expanded:
            if self.rect[0] <= pos[0] <= (self.rect[2] + self.rect[0]) and \
                    self.rect[1] <= pos[1] <= (self.rect[3] + self.rect[1]):
                return self
            else:
                return None
        else:
            a = []
            for subtrees in self._subtrees:
                if subtrees.get_tree_at_position(pos) is not None:
                    a.extend([subtrees.get_tree_at_position(pos)])
            return _helper_get_tree(a)

    def update_data_sizes(self) -> int:
        """Update the data_size for this tree and its subtrees, based on the
        size of their leaves, and return the new size.

        If this tree is a leaf, return its size unchanged.
        """
        # I worked on the first function of task 4
        if self.is_empty():
            return 0
        elif self._subtrees == []:
            return self.data_size
        else:
            a = 0
            for subtrees in self._subtrees:
                a += subtrees.update_data_sizes()
            self.data_size = a
            return a

    def move(self, destination: TMTree) -> None:
        """If this tree is a leaf, and <destination> is not a leaf, move this
        tree to be the last subtree of <destination>. Otherwise, do nothing.
        """
        if not self.is_empty():
            if self._subtrees == [] and destination._subtrees != []:

                self._parent_tree._subtrees.remove(self)
                if self._parent_tree._subtrees == []:
                    self._parent_tree.data_size = 0

                self._parent_tree = destination

                if not destination.is_empty():
                    destination._subtrees.append(self)

    def change_size(self, factor: float) -> None:
        """Change the value of this tree's data_size attribute by <factor>.

        Always round up the amount to change, so that it's an int, and
        some change is made.

        Do nothing if this tree is not a leaf.
        """

        if factor >= 0:
            self.data_size += math.ceil(self.data_size * factor)
        else:
            self.data_size -= math.ceil(self.data_size * abs(factor))
        if self.data_size < 1:
            self.data_size = 1

    def expand(self) -> None:
        """Expand this tree
        """
        if not self.is_empty():
            if self._subtrees == []:
                self._expanded = False
            elif self._parent_tree is None:
                self._expanded = True
            else:
                self._expanded = True
                self._parent_tree.expand()

    def collapse(self) -> None:
        """Collapse this tree
        """
        if not self.is_empty():
            if self._subtrees == []:
                self._expanded = False
                if self._parent_tree is not None:
                    self._parent_tree._expanded = False
            else:
                self._expanded = False
                if self._parent_tree is not None:
                    self._parent_tree._expanded = False
                for subtree in self._subtrees:
                    subtree.collapse()

    def collapse_all(self) -> None:
        """ The tree and all of its subtrees are gonna collapse
        - if _expanded is True, then _parent_tree._expanded is True
        - if _expanded is False, then _expanded is False for every tree
        in _subtrees, lee
        - if _subtrees is empty, then _expanded is False
        """
        if not self.is_empty():
            if self._parent_tree is None:
                self.collapse()
            else:
                self.collapse()
                self._parent_tree.collapse_all()

    def expand_all(self) -> None:
        """ The tree and all of its subtrees are gonna expand
        """
        if not self.is_empty():
            if self._subtrees == []:
                self._expanded = False
            else:
                self.expand()
                for subtree in self._subtrees:
                    subtree.expand_all()

    # Methods for the string representation
    def get_path_string(self, final_node: bool = True) -> str:
        """Return a string representing the path containing this tree
        and its ancestors, using the separator for this tree between each
        tree's name. If <final_node>, then add the suffix for the tree.
        """
        if self._parent_tree is None:
            path_str = self._name
            if final_node:
                path_str += self.get_suffix()
            return path_str
        else:
            path_str = (self._parent_tree.get_path_string(False) +
                        self.get_separator() + self._name)
            if final_node or len(self._subtrees) == 0:
                path_str += self.get_suffix()
            return path_str

    def get_separator(self) -> str:
        """Return the string used to separate names in the string
        representation of a path from the tree root to this tree.
        """
        raise NotImplementedError

    def get_suffix(self) -> str:
        """Return the string used at the end of the string representation of
        a path from the tree root to this tree.
        """
        raise NotImplementedError


def _helper_get_tree(a: List) -> Optional[TMTree]:
    """This function will return the rectangle needed for the
    get_tree_at_pos method.
    """
    if len(a) == 0:
        return None
    elif len(a) == 2:
        x1 = a[0].rect[0]
        y1 = a[0].rect[1]
        x2 = a[1].rect[0]
        y2 = a[1].rect[1]
        if x1 > x2:
            return a[1]
        elif x2 > x1:
            return a[0]
        else:
            if y1 > y2:
                return a[0]
            else:
                return a[1]
    elif len(a) == 3:
        x1 = a[0].rect[0]
        y1 = a[0].rect[1]
        x2 = a[1].rect[0]
        y2 = a[1].rect[1]
        x3 = a[2].rect[0]
        y3 = a[2].rect[1]
        if x3 < x2 and x3 < x1:
            return a[2]
        elif x2 < x1 and x2 < x3:
            return a[1]
        elif x1 < x2 and x1 < x3:
            return a[0]
        elif y1 > y2 and y1 > y3:
            return a[0]
        elif y2 > y3 and y2 > y1:
            return a[1]
        elif y3 > y2 and y3 > y1:
            return a[2]
        else:
            return a[0]
    else:
        return a[0]


class FileSystemTree(TMTree):
    """A tree representation of files and folders in a file system.

    The internal nodes represent folders, and the leaves represent regular
    files (e.g., PDF documents, movie files, Python source code files, etc.).

    The _name attribute stores the *name* of the folder or file, not its full
    path. E.g., store 'assignments', not '/Users/Diane/csc148/assignments'

    The data_size attribute for regular files is simply the size of the file,
    as reported by os.path.getsize.
    """

    def __init__(self, path: str) -> None:
        """Store the file tree structure contained in the given file or folder.

        Precondition: <path> is a valid path for this computer.
        """
        # Remember that you should recursively go through the file system
        # and create new FileSystemTree objects for each file and folder
        # encountered.
        #
        # Also remember to make good use of the superclass constructor!
        all_sub_tree = []  # all the sub-folders of this folder
        op = os.path

        if not os.path.isdir(path):  # if current item is not a folder, thus a
            op = os.path  # file,
            TMTree.__init__(self, op.basename(path), [], op.getsize(path))
        else:
            # current item is a folder
            for filename in os.listdir(path):
                # path for the next item in this folder
                subitem = os.path.join(path, filename)
                # recursively make the sub-folders
                all_sub_tree.append(FileSystemTree(subitem))
            # create the current folder
            TMTree.__init__(self, op.basename(path), all_sub_tree)

    def get_separator(self) -> str:
        """Return the file separator for this OS.
        """
        return os.sep

    def get_suffix(self) -> str:
        """Return the final descriptor of this tree.
        """
        if len(self._subtrees) == 0:
            return ' (file)'
        else:
            return ' (folder)'


if __name__ == '__main__':
    import python_ta

    python_ta.check_all(config={
        'allowed-import-modules': [
            'python_ta', 'typing', 'math', 'random', 'os', '__future__'
        ]
    })
