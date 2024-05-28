import pickle, io
from typing import List, Any, Optional, Mapping, Generator

class LimitReached(Exception):
    pass

class Node:
    ... # only for typehinting

class Node:
    """
    ### Overview
    A simple but effective singular node, with the capabilities of attaching children, having siblings and more.
    
    You can export a node by serialising it into a `.pkl` file and all its accompanying children will follow,
    allowing for easy and efficient exportation, storage and importation.

    There's also a collection feature in which it will collect all child nodes below a certain node into a list
    which you can then access and modify however you wish.

    You can add other nodes, remove any nodes on the list.

    ### Parameters:
        - name: `str` - The name of the node. This `must` be a valid Python variable name as the class
        allows you to mention child nodes as attributes of the current node. This would not be possible
        if the names were not allowed in Python.
        
        - value: `Any` - Simply just the value the node possesses. As depicted by the typehint, it can
        be anything - no limits.

        - node_cap: `int` - The number of children one node can possess. If left unfilled, it defaults
        to `None` which allows for an unlimited amount of nodes as children of one node.
    
    
    ### Guide

    """
    
    def __init__(self, name: str, value: Any, node_cap: int = None) -> None:
        # assertions
        assert type(name) is str, "name must be a string."
        assert name.isalnum() and not name[0].isdigit(), "name must be a valid variable name."
        assert type(node_cap) is int or node_cap is None, f"node_cap must be of type int or None. Node cap variable is of type {type(node_cap)}"
        
        # check if node cap has been reached
        if node_cap:
            assert node_cap > 0, f"node_cap must be above 0, not {node_cap}."

        # parameters
        self.name = name
        self.value = value
        self.node_cap = node_cap

        # private defaults
        self.__parent: Node = None
        self.__siblings: List[Node] = []
        self.__children: List[Node] = []

        # "file path" for __repr__
        self.full_path = './'

        # tiers for checking when adding children
        self.__tier = 0

        # child index for moving left and right through nodes
        self.__index = 0
    
    @property
    def children(self) -> List[Node]:
        """
        The children of the current node.
        
        Given in the form of a list of `Node`.
        """
        
        return self.__children
    
    @property
    def siblings(self) -> List[Node]:
        """
        The siblings of the current node.
        
        Given in the form of a list of `Node`.
        """
        
        return self.__siblings
    
    @property
    def parent(self) -> Node:
        """
        The parent of the current node.
        
        Given in the form of a `Node`.
        """
        
        return self.__parent
    
    def add(self, *children: Node) -> Node:
        """
        Add children to the current node.
        Note that this will raise a TypeError if any of the children given are not of type Node.

        Parameters:
            - children: `Node` - the children to be added to the node.
        
        Raises:
            - `ArithmeticError`: raised when the node cap on the parent is exceeded or when not all children are Node instances.
            - `TypeError`: raised when a child in `children` is found to not be of type `Node`.
            - `ValueError`: raised when a child's tier is equal to or greater than the current node's tier,
            meaning it is attempting to be placed beside or above the current node, creating problems when searching.
            - `NameError`: one of the children's names is a duplicate of a child of the current node, thus creating
            naming errors when referencing as attributes.

        This also returns the node itself to allow for fluent-style chaining.
        """

        assert all(isinstance(child, Node) for child in children), f"not all children given are Node instances."

        if self.node_cap:
            total_node_count = len(self.__children) + len(children)

            if total_node_count > self.node_cap:
                too_many_nodes_message = f"Too many nodes. Node is capped to {self.node_cap} nodes with {self.node_cap - len(self.__children)} empty spaces.\nAdding {total_node_count} more nodes leads to there being {total_node_count - self.node_cap} more nodes than allowed.\n\nTo remove this limit, remove the node_cap argument and it will default to an unlimited amount."
                raise ArithmeticError(too_many_nodes_message)
        
        for child in children:
            if type(child) is not Node:
                raise TypeError(f"children must be of type Node. Child {child} is of type {type(child)}")
            
            if child.__tier > self.__tier:
                incorrect_tier_msg = f"child has attempted to attach beside or above current node.\nChild is on tier {child.__tier} while current node is on tier {self.__tier}."
                raise ValueError(incorrect_tier_msg)
            
            if child.name in self.__children:
                name_error_msg = f"child has a duplicate name, which creates naming errors when referencing as attributes. Correct the name and run the function again."
                raise NameError(name_error_msg)
            
            self.__children.append(child)
            child.full_path += child.name + '/'
            
            setattr(self, child.name, child)

            child.__parent = self
            child.__siblings = self.__children.copy()
            child.__siblings.remove(child)
            child.__tier = self.__tier + 1
        
        return self
    
    def remove(self, *children: Node) -> Node:
        """
        Removes children from the node.
        
        If some children given are not present, they are skipped in the process.
        
        Parameters:
            - children: `Node` - the children to be removed from the node.
        
        Raises:
            - `TypeError`: raised when a child in `children` is found to not be of type `Node`

        Note that if children are not entirely of type Node, a TypeError is raised.

        This also returns the node itself to allow for fluent-style chaining.
        """
        
        for child in children:
            if type(child) is not Node:
                raise TypeError(f"children must be of type Node. Child {child} is of type {type(child)}")
            
            if child not in self.__children:
                continue

            delattr(self, child.name)

            child.__siblings = []
            self.__children.remove(child)
        
        return self

    def search_for(self, strict: bool = False, **search_kwargs) -> Optional[Node]:
        """
        Search for a target node below the current node using kwargs.
        
        If an `AttributeError` is encountered, it is skipped and the search will continue by default.
        This behaviour can be toggled using the `strict` argument.

        Parameters:
            - strict: `bool` - whether or not to raise an `AttributeError` upon searching for a nonexistent attribute.
            - `search_kwargs` - the search terms to compare each node against.

        Returns;
            - `Node`: the node being looked for in the recursive search.
            - `None`: poof - nothing.
        """

        for child in self.__children:
            for kwarg in search_kwargs.keys():
                try:
                    if getattr(child, kwarg) == search_kwargs[kwarg]:
                        return child # found match

                except AttributeError as e:
                    if strict:
                        raise e
                    
                    continue

            result = child.search_for(strict, **search_kwargs)

            if result:
                return result

        return None
    
    def __collect(self, starting_node: Node) -> Generator:
        """
        Returns the base generator for `.collect()` to turn into a list.

        I advise you use `.collect()` instead of this method. That's where the more complete docstring is found.
        """

        assert type(starting_node) is Node, f"starting node must be of type Node. Currently, it is of type {type(starting_node)}"
        
        for node in starting_node.__children:
            if node.__children:            
                for new in self.search(node):
                    yield new

            yield node
    
    def collect(self, starting_node: Node) -> List:
        """
        Recursively and iteratively yield children from the current node in the form of a flattened list.

        Parameters:
            - starting_node: `Node` - the node to start collecting children from.
        
        Returns:
            - `List[Node]` - a list of children nodes (depth is ignored)
        
        Raises:
            - `AssertionError` - raised when `starting_node` is not a `Node` instance
        """

        return list(self.__collect(starting_node))[::-1]
    
    def pickle(self, fp: io.BufferedWriter, node: Node = None) -> None:
        """
        Dump the node and its accompanying children in a .pkl file for easy storage.
        
        To retrieve the contents from a .pkl file, use `.unpickle()`.

        Note: `fp` must be in `wb` (write bytes) mode, otherwise the function will fail.

        Parameters:
            - fp: `io.BufferedWriter` - the file pointer to dump the node with.
            - node: `Node` - the node to dump into the file along with its children.

        Note that if `node` is left out then it will default to `self`.
        """
        
        node = node or self
        pickle.dump(obj = node, file = fp)

    def unpickle(self, fp: io.BufferedReader) -> Node | Any:
        """
        Retrieve a node and its accompanying children from a .pkl file and return it.
        To dump the contents into a .pkl file, use `.pickle()`.

        `fp` must be in `wb` (write bytes) mode, otherwise the function will fail.

        Parameters:
            - fp: `io.BufferedReader` - the file pointer to dump the node with.

        Returns:
            - `Node` - the node retrieved from the file.
            - `Any` - may return something unexpected if the file doesn't only contain the node.
        """

        node = pickle.load(fp)
        return node

    def __repr__(self) -> str:
        "Represent the node as a file path when printing."

        current = self
        path = []

        while current.__parent:
            path.append(current.name)
            current = current.__parent

        path.reverse()
        return f"Node('{'./' + '/'.join(path)}')"
    
    def __next__(self) -> List[Node]:
        "Return the next set of nodes that are children of the current node."
        return self.__children
    
    def __left__(self):
        "Custom dunder method for the `left()` function."
        
        siblings = self.parent.__children

        if self.__index == 0:
            raise LimitReached(f"cannot go further left. Index is already at 0 out of {len(siblings) - 1}.")

        self.__index -= 1
        return siblings[self.__index]
    
    def __right__(self) -> Node:
        "Custom dunder method for the `right()` function."

        siblings = self.parent.__children

        if self.__index == len(siblings) - 1:
            raise LimitReached(f"cannot go further right. Index is already at {self.__index} out of {len(siblings) - 1}.")

        self.__index += 1
        return siblings[self.__index]