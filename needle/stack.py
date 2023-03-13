from __future__ import annotations

from dataclasses import dataclass, field
from typing import Type

from needle.search import Search, assemble_key


@dataclass
class Delegate:
    method_name: str = field(init=False)
    stack: Stack = field(init=False)

    def __set_name__(self, owner: Type[Stack], name: str) -> None:
        self.method_name = name

    def __get__(self, instance: Stack, owner: Type[Stack]) -> "Delegate":
        self.stack = instance
        return self

    def __call__(self, *args, **kwargs) -> Stack:
        self.stack.push(getattr(self.stack.top, self.method_name)(*args, **kwargs))
        return self.stack


class Stack:

    def __init__(self, search: Search) -> None:
        self.stack = [search]

    @property
    def top(self) -> Search:
        return self.stack[-1]

    @property
    def empty(self) -> bool:
        return not self.stack

    @property
    def prefix(self) -> str:
        return assemble_key([s.prefix for s in self.stack])

    def push(self, search: Search) -> Stack:
        self.stack.append(search)
        return self

    def pop(self) -> Stack:
        self.stack.pop(-1)
        return self

    def __repr__(self) -> str:
        stack = "\n\t" + "\n\t".join([repr(search) for search in self.stack])
        return f"Stack({stack}\n)"


    find = Delegate()
    subsearch = Delegate()
    max_depth = Delegate()
    fixed_depth = Delegate()
