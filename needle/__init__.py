from __future__ import annotations
from typing import Any

from needle.search import Search
from needle.stack import Stack
from needle.viewer import RichDevice, Viewer


__all__ = ["search", "view", "Search", "Viewer"]


def view(obj: Any, max_depth: int | None = None) -> None:
    Viewer(Search(obj, max_depth=max_depth), RichDevice()).interactive()


def search(obj: Any, max_depth: int | None = None) -> Stack:
    return Stack(Search(obj, max_depth))
