from __future__ import annotations

from typing import Any
from pprint import pprint


class Search:

    def __init__(
        self,
        obj: Any,
        cache: list[str] | None = None,
        prefix: str | None = None,
        max_depth: int | None = None,
    ) -> Search:
        self.obj = obj
        self._cache = _flatten(obj, max_depth) if cache is None else cache
        self._prefix = prefix

    @property
    def flat_keys(self) -> list[str]:
        return list(self._cache)

    @property
    def prefix(self) -> str:
        return self._prefix or ""

    def get(self, key: str) -> Any:
        node = self.obj
        for part in parse_key(key):
            node = node[part]
        return node

    def __getitem__(self, key: str) -> Any:
        try:
            return self.get(key)
        except (KeyError, IndexError):
            raise KeyError(f"key {key} not found")

    def find(self, suffix: str) -> Search:
        return Search(self.obj, [key for key in self._cache if suffix in key], self.prefix)

    def subsearch(self, prefix: str) -> Search:
        node = self.get(prefix)
        cache = [key.removeprefix(prefix).strip(".") for key in self._cache if key.startswith(prefix)]
        return Search(node, cache, prefix)

    def max_depth(self, depth: int) -> Search:
        cache = [key for key in self._cache if key_depth(key) <= depth]
        return Search(self.obj, cache, self.prefix)

    def fixed_depth(self, depth: int) -> Search:
        cache = [key for key in self._cache if key_depth(key) == depth]
        return Search(self.obj, cache, self.prefix)

    def __eq__(self, other: Search) -> bool:
        return self._cache == other._cache and self._prefix == other._prefix

    def pprint(self) -> None:
        pprint({key: self[key] for key in self._cache})

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
    return isinstance(obj, (int, float, bool, str)) or obj is None


def key_depth(key: str) -> int:
    """Returns a key depth (zero-indexed).

    The depth defines how deeply located a value in a config structure. The top-level keys (i.e., the keys
    that point directly to an atomic value) have zero depth. The keys that point to a value in a dictionary
    located right beneath the top level have depth of one, etc.

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
