from __future__ import annotations

from typing import Any
from pprint import pprint


class Search:
    """Searching keys in a tree-like container.

    A `Search` object wraps a given `obj` container and provides a simplistic search interface that allows listing all
    available (hierarchical) keys, and slice and dice that container to zoom-in its different sub-containers.
    """
    def __init__(
        self,
        obj: Any,
        cache: list[str] | None = None,
        prefix: str | None = None,
        max_depth: int | None = None,
    ) -> Search:
        """Creates a new `Search` object.

        Parameters
        ----------
        obj
            The container to search in.
        cache
            A list of keys to look up in the object. If `None`, the cache is computed from `obj`.
        prefix
            Section of the object that is being searched. This is used to compute the full key of a node in case if
            the currently searched object is a sub-container of the original object.
        max_depth
            Maximum depth of the object to search in. If `None`, the object is searched until the leaves. Might be
            helpful to avoid too long searches, or prevent infinite loops.
        """
        self.obj = obj
        self._cache = _flatten(obj, max_depth) if cache is None else cache
        self._prefix = prefix

    @property
    def flat_keys(self) -> list[str]:
        """Returns a list of all available keys in the object.

        Each key is a string that represents the path to the node in the object.

        Returns
        -------
        A list of all available keys in the object.

        Examples
        --------
        >>> search = Search({"a": {"one": 1, "two": 2}, "b": [{"x": 3}, {"y": 4}]})
        >>> search.flat_keys
        ['a.one', 'a.two', 'b[0].x', 'b[1].y']
        """
        return list(self._cache)

    @property
    def prefix(self) -> str:
        """Returns the prefix of the object that is being searched.

        If the searched object is the original object, the prefix is an empty string.
        """
        return self._prefix or ""

    def get(self, key: str) -> Any:
        """Gets the value of a node in the object.

        Note that a returned value might be a sub-container of the original object that (in turn) can be further
        searched.

        Parameters
        ----------
        key
            The key of the node to get.

        Returns
        -------
        The value of the node.
        """
        node = self.obj
        for part in parse_key(key):
            node = node[part]
        return node

    def find(self, suffix: str) -> Search:
        """Finds all keys that contain a given suffix.

        Parameters
        ----------
        suffix
            The suffix to search for.

        Returns
        -------
        A new `Search` object that contains only the nodes that contain the given suffix.
        """
        return Search(self.obj, [key for key in self._cache if suffix in key], self.prefix)

    def subsearch(self, prefix: str) -> Search:
        """Starts a new search from a given node.

        Parameters
        ----------
        prefix
            The key of the node to start the new search from.

        Returns
        -------
        A new `Search` object where all keys start with the given prefix.
        """
        node = self.get(prefix)
        cache = [key.removeprefix(prefix).strip(".") for key in self._cache if key.startswith(prefix)]
        return Search(node, cache, prefix)

    def max_depth(self, depth: int) -> Search:
        """Limits the search to a given depth.

        Parameters
        ----------
        depth
            The maximum depth to search in.

        Returns
        -------
        A new `Search` object that contains only the nodes that are at most `depth` levels deep.
        """
        cache = [key for key in self._cache if key_depth(key) <= depth]
        return Search(self.obj, cache, self.prefix)

    def fixed_depth(self, depth: int) -> Search:
        """Strictly limits the search to a given depth.

        All nodes that are not at the given depth are excluded from the search.

        Parameters
        ----------
        depth
            The depth to search in.

        Returns
        -------
        A new `Search` object that contains only the nodes that are at the given depth.
        """
        cache = [key for key in self._cache if key_depth(key) == depth]
        return Search(self.obj, cache, self.prefix)

    def pprint(self) -> None:
        """Pretty prints the search results.

        Returns
        -------
        None
        """
        pprint({key: self[key] for key in self._cache})

    def __getitem__(self, key: str) -> Any:
        try:
            return self.get(key)
        except (KeyError, IndexError):
            raise KeyError(f"key {key} not found")

    def __eq__(self, other: Search) -> bool:
        return self._cache == other._cache and self._prefix == other._prefix

    def __repr__(self) -> str:
        prefix = self.prefix or "\"\""
        return f"Search(prefix={prefix}, n_keys={len(self.flat_keys)})"

    def __str__(self) -> str:
        return str({key: self[key] for key in self._cache})


def _flatten(obj: Any, max_depth: int | None) -> list[str]:

    def _visit(node: Any, parent: str, depth: int) -> list[str]:
        if atomic(node):
            return []
        collected = []
        if isinstance(node, dict):
            for key, child in node.items():
                new_key = f"{parent}.{key}"
                if atomic(child) or (max_depth is not None and depth >= max_depth):
                    collected.append(new_key)
                else:
                    collected.extend(_visit(child, new_key, depth + 1))
        elif isinstance(node, (list, tuple)):
            for index, child in enumerate(node):
                new_key = f"{parent}[{index}]"
                if atomic(child) or (max_depth is not None and depth >= max_depth):
                    collected.append(new_key)
                else:
                    collected.extend(_visit(child, new_key, depth + 1))
        return collected

    return [k.strip(".") for k in _visit(obj, "", 0)]


def atomic(obj: Any) -> bool:
    """Checks if an object is atomic.

    Atomic objects are the objects that aren't built-in containers.

    Returns
    -------
    True if the object is atomic, False otherwise.
    """
    return isinstance(obj, (int, float, bool, str)) or obj is None


def key_depth(key: str) -> int:
    """Returns a key depth (zero-indexed).

    The depth defines how deeply located a value in a config structure. The top-level keys (i.e., the keys
    that point directly to an atomic value) have zero depth. The keys that point to a value in a dictionary
    located right beneath the top level have depth of one, etc.

    Parameters
    ----------
    key
        Key which depth to compute.

    Returns
    -------
    The depth of the key.

    Examples
    --------
    >>> key_depth("key")
    0
    >>> key_depth("A.B.C")
    2
    >>> key_depth("A[0].B[1].C")
    4
    """
    try:
        return len(parse_key(key)) - 1
    except ValueError:
        raise ValueError(f"cannot compute depth: the key {key} is not a valid key")


def parse_key(key: str) -> list[str | int]:
    """Parses a key into a list of parts.

    Parameters
    ----------
    key
        The key to parse.

    Examples
    --------
    >>> parse_key("one.two.three")
    ['one', 'two', 'three']
    >>> parse_key("[0][1][2]")
    [0, 1, 2]
    >>> parse_key("root.child[0].leaf")
    ['root', 'child', 0, 'leaf']
    """
    str_key, int_key = "", ""
    digit = False
    parts = []
    for ch in key:
        if ch == ".":
            if str_key:
                parts.append(str_key)
            str_key = ""
        elif ch == "[":
            if str_key:
                parts.append(str_key)
            str_key = ""
            digit = True
        elif ch == "]":
            parts.append(int(int_key))
            int_key = ""
            digit = False
        elif digit:
            if not ch.isdigit():
                raise ValueError(f"cannot parse key: {key}")
            int_key += ch
        else:
            str_key += ch
    if str_key:
        parts.append(str_key)
    return parts


def assemble_key(parts: list[str | int]) -> str:
    """

    Parameters
    ----------
    parts

    Returns
    -------

    Examples
    --------
    >>> assemble_key(["one", "two", "three"])
    'one.two.three'
    >>> assemble_key([0, 1, 2])
    '[0][1][2]'
    >>> assemble_key(["root", "child", 0, "leaf"])
    'root.child[0].leaf'
    >>> assemble_key(["root", "child", "[0]", "leaf"])
    'root.child[0].leaf'
    """
    prepared = [""] * len(parts)
    for i, part in enumerate(parts):
        if isinstance(part, int):
            prepared[i] = f"[{part}]"
        elif part.startswith("[") and part.endswith("]"):
            prepared[i] = part
        else:
            prepared[i] = f".{part}"
    return "".join(prepared).strip(".")
