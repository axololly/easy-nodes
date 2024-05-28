from node import Node

def left(node: Node) -> Node:
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

    assert type(node) is Node, f"node argument must be a Node - currently it is a {type(node)}"
    
    return node.__left__()

def right(node: Node) -> Node:
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

    assert type(node) is Node, f"node argument must be a Node - currently it is a {type(node)}"
    
    return node.__right__()