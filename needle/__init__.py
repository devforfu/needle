from dataclasses import dataclass, field
from typing import Any


@dataclass
class Search:
    obj: Any
    _cache: list[str] = field(init=False, default_factory=list)

    def __post_init__(self):
        self._cache = self.flatten()

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

    @property
    def flat_keys(self) -> list[str]:
        return list(self._cache)


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
