from __future__ import annotations

from typing import Any


class Search:

    def __init__(self, obj: Any, cache: list[str] | None = None, prefix: str | None = None) -> Search:
        self.obj = obj
        self._cache = self.flatten() if cache is None else cache
        self._prefix = prefix

    @property
    def flat_keys(self) -> list[str]:
        return list(self._cache)

    @property
    def prefix(self) -> str:
        return self._prefix or ""

    def flatten(self) -> list[str]:

        def _flatten(node: Any, parent: str) -> list[str]:
            if atomic(node):
                return []
            collected = []
            if isinstance(node, dict):
                for key, child in node.items():
                    new_key = f"{parent}.{key}"
                    if atomic(child):
                        collected.append(new_key)
                    collected.extend(_flatten(child, new_key))
            elif isinstance(node, (list, tuple)):
                for index, child in enumerate(node):
                    new_key = f"{parent}[{index}]"
                    if atomic(child):
                        collected.append(new_key)
                    collected.extend(_flatten(child, new_key))
            return collected

        return [k.strip(".") for k in _flatten(self.obj, "")]

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

    def find(self, suffix: str) -> list[str]:
        return [key for key in self._cache if suffix in key]

    def subsearch(self, prefix: str) -> Search:
        node = self.get(prefix)
        cache = [key.removeprefix(prefix).strip(".") for key in self._cache if key.startswith(prefix)]
        return Search(node, cache, prefix)

    def max_depth(self, depth: int) -> Search:
        cache = [key for key in self._cache if key.count(".") <= depth]
        return Search(self.obj, cache)

    def fixed_depth(self, depth: int) -> Search:
        cache = [key for key in self._cache if key.count(".") == depth]
        return Search(self.obj, cache)


def atomic(obj: Any) -> bool:
    return isinstance(obj, (int, float, bool, str)) or obj is None


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
