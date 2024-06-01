import pickle, io
from __future__ import annotations
from typing import List, Any, Optional, Generator, Callable
from errors import LimitReached, NoArgumentsGiven

class _MissingSentinel:
    def __repr__(self) -> str:
        return "MISSING"

    def __reduce__(self) -> str:
        return "MISSING"
    
MISSING: Any = _MissingSentinel

SearchCheck = Callable[[Any], bool]

class Node:
    """
    ### Overview:

    A simple but effective singular node, with the capabilities of attaching children, having siblings and more.
    
    You can export a node by serialising it into a `.pkl` file and all its accompanying children will follow,
    allowing for easy and efficient exportation, storage and importation.

    There's also a collection feature in which it will collect all child nodes below a certain node into a list
    which you can then access and modify however you wish.

    You can add other nodes, remove any nodes on the list.

    ### Parameters:

    - name: `str` - The name of the node. This must be a valid Python variable name as the class
    allows you to mention child nodes as attributes of the current node. This would not be possible
    if the names were not allowed in Python.
        
    - value: `Any` - The value the node possesses.

    - node_cap: `int` - The number of children this node can possess. If left unfilled, it defaults
    to `None` which allows for an unlimited amount of nodes as children of one node.
    
    ### Raises:

    - `TypeError` - raised when:
        - `name` is not a string
        - `node_cap` is not an integer and is not `None` (there is a value but it's not a number)
    
    - `ValueError` - raised when the name is not a valid Python variable name.

    - `ArithmeticError` - raised when `node_cap` is not a positive integer.
    """
    
    def __init__(self, name: str, value: Any, node_cap: int = None) -> None:
        # type checks
        if type(name) is not str:
            raise TypeError("name must be a string.")
        
        if not name.isalnum() or name[0].isdigit():
            raise ValueError("name must be a valid variable name.")
        
        if type(node_cap) is not int and node_cap is not None:
            raise TypeError(f"node_cap must be of type int or None. Node cap variable is of type {type(node_cap)}")
        
        # check if node cap has been reached
        if node_cap and not node_cap > 0:
            raise ArithmeticError(f"node_cap must be above 0, not {node_cap}.")

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
        
        Returns:
            - `List[Node]`
        """
        
        return self.__children
    
    @property
    def siblings(self) -> List[Node]:
        """
        The siblings of the current node.
        
        Returns:
            - `List[Node]`
        """
        
        return self.__siblings
    
    @property
    def parent(self) -> Node:
        """
        The parent of the current node.
        
        Returns:
            - `List[Node]`.
        """
        
        return self.__parent
    
    def add(self, *children: Node) -> Node:
        """
        Add children to the current node.

        Parameters:
            - children: `Node` - the children to be added to the node.
        
        Raises:
            - `ArithmeticError`: raised when the node cap on the parent is exceeded or when not all children are Node instances.
            
            - `TypeError`: raised when a child in `children` is found to not be of type `Node`.
            
            - `ValueError`: raised when a child's tier is equal to or greater than the current node's tier,
            meaning it is attempting to be placed beside or above the current node, creating problems when searching.
            
            - `NameError`: one of the children's names is a duplicate of a child of the current node, thus creating
            naming errors when referencing as attributes.

        Returns:
            `self` - the node itself to allow for fluent-style chaining.
        """

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
            
            setattr(self, child.name, child)

            child.full_path += child.name + '/'
            child.__parent = self
            
            child.__siblings = self.__children.copy()
            child.__siblings.remove(child)
            
            child.__tier = self.__tier + 1
            child.__index = len(self.__children) - 1
        
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

        Returns:
            - `self` - the node itself to allow for fluent-style chaining.
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

    def __search_for(
            self,
            *,
            name: Optional[str] = MISSING,
            value: Optional[Any] = MISSING,
            check: Optional[SearchCheck] = None
        ) -> Optional[Node]:
        """
        Base method for searching for a given node using a variety of checks like:
            - name checks
            - value checks
            - lambda / function checks
        
        Parameters:
            - name: `Optional[str]` - the name of the node to search for. Defaults to `MISSING`.
            - value: `Optional[Any]` - the value of the node to search for. Defaults to `MISSING`.
            - check: `Optional[SearchCheck]` - the lambda / function to check for a matching node with. Defaults to `None`.
        
        Returns:
            - `Optional[Node]` - the matching node or `None`.
        """

        if name is not MISSING and value == self.name:
            return self
        
        if value is not MISSING and value == self.value:
            return self
        
        if check is not None and check(self):
            return self
        
        for child in self.__children:
            result = child.search_for(name = name, value = value, check = check)

            if result is not None:
                return result
        
        return None

    def search_for(
            self,
            *,
            name: Optional[str] = MISSING,
            value: Optional[Any] = MISSING,
            check: Optional[SearchCheck] = None
        ) -> Optional[Node]:
        """
        Search for a target node below the current node using kwargs.

        Includes type checks.

        Parameters:
            name: `Optional[str]` - the name to look for when checking each node (or `MISSING`)
            value: `Optional[Any]` - the value to look for when checking each node (or `MISSING`)
            check: `Optional[SearchCheck]` - a check function used to find a node instead of a kwarg.

        Returns:
            - `Optional[Node]`: the node being looked for in the recursive search, or `None`.

        Raises:
            - `TypeError` - raised when an incorrect type for an argument is given.
            - `NoArgumentsGiven` - raised when both `name` and `value` are `MISSING` and `check` is `None`.
            - `ImproperArgument` - raised when `name` is not a valid Python variable name.
        
        Thank you to Chai (@trevorfl) for correcting this.
        """

        if not isinstance(name, str) and name is not MISSING:
            message = "name of the node to search for must be a string."
            raise TypeError(message)

        if not name.isalnum() or name[0].isdigit():
            message = "name of the node to search for must be a valid Python variable name."
            raise ValueError(message)

        if name is MISSING and value is MISSING and check is None:
            message = "no arguments were given to the function."
            raise NoArgumentsGiven(message)
        
        return self.__search_for(name = name, value = value, check = check)
    
    def __collect(self, starting_node: Node) -> Generator[Node]:
        """
        Returns the base generator for `.collect()` to turn into a list.

        Parameters:
            - starting_node: `Node` - the node to collect all descendants from.
        
        Returns:
            - `Generator[Node]` - an iterable of `Node` instances.
        """

        if not isinstance(node, Node):
            raise TypeError(f"starting node must be of type Node. Currently, it is of type {type(starting_node)}")
        
        for node in starting_node.__children:
            if node.__children:
                for new in self.search(node):
                    yield new

            yield node
    
    def collect(self, starting_node: Node) -> List[Node]:
        """
        Recursively and iteratively yield descendants from the current node and return in the form of a flattened list.

        Parameters:
            - starting_node: `Node` - the node to collect descendants from.
        
        Returns:
            - `List[Node]` - a list of descendants from the starting node.
        
        Raises:
            - `TypeError` - raised when `starting_node` is not a `Node` instance.
        """

        return list(self.__collect(starting_node))[::-1]
    
    def pickle(self, fp: io.BufferedWriter, node: Node = None) -> None:
        """
        Dump the node and its accompanying children in a .pkl file for easy storage.
        
        To retrieve the contents from a .pkl file, use `.unpickle()`.

        Parameters:
            - fp: `io.BufferedWriter` - the file pointer to dump the node with.
            - node: `Node` - the node to serialise.
        
        Raises:
            - `ValueError` - raised when the `node` argument is not an instance of `Node`.
            - `pickle.PicklingError` - raised when the `node` argument cannot be pickled.

        Returns:
            - `self` - the instance running the method.
        """

        if not isinstance(node, Node):
            raise ValueError(f"node parameter is not of type Node - currently it is of type {type(node)}s")
        
        node = node or self
        pickle.dump(obj = node, file = fp)

    def unpickle(self, fp: io.BufferedReader) -> Node | Any:
        """
        Retrieve a node and its accompanying children from a .pkl file and return it.
        
        To dump the contents into a `.pkl` file, use `.pickle()`.

        Parameters:
            - fp: `io.BufferedReader` - the file pointer to dump the node with.

        Returns:
            - `Node` - the node retrieved from the file.
            - `Any` - may return something unexpected if the file doesn't only contain the node or contains something else.
        
        Raises:
            - `pickle.UnpicklingError` - raised when the file cannot be deserealised.
            - `io.UnsupportedOperation` - raised when the wrong mode for the file is used.
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
    
    def left(self):
        """
        Executes the special dunder method to move left through the given node's siblings.

        Parameters:
            - node: `Node` - the node to move left from.

        Returns:
            - `Node` - the sibling left of the given node in the tree.

        Raises:
            - `AssertionError` - raised when the given argument isn't a `Node` instance.
            - `LimitReached` - raised when you can no longer go left, ie. the limit is reached for moving left.
        """
        
        siblings = self.parent.__children

        if self.__index == 0:
            raise LimitReached(f"cannot go further left. Index is already at 0 out of {len(siblings) - 1}.")

        self.__index -= 1
        return siblings[self.__index]
    
    def right(self) -> Node:
        """
        Executes the special dunder method to move right through the given node's siblings.

        Parameters:
            - node: `Node` - the node to move right from.

        Returns:
            - `Node` - the sibling right of the given node in the tree.

        Raises:
            - `AssertionError` - raised when the given argument isn't a `Node` instance.
            - `LimitReached` - raised when you can no longer go right, ie. the limit is reached for moving right.
        """
        
        siblings = self.parent.__children

        if self.__index == len(siblings) - 1:
            raise LimitReached(f"cannot go further right. Index is already at {self.__index} out of {len(siblings) - 1}.")

        self.__index += 1
        return siblings[self.__index]