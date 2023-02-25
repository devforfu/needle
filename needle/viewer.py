from __future__ import annotations

from dataclasses import dataclass
from typing import IO, Protocol

import rich.console
import rich.prompt
import rich.table

from needle.search import Search


class Device(Protocol):

    def render(self, search: Search) -> None:
        raise NotImplementedError

    def query(self, prefix: str) -> str:
        raise NotImplementedError


class RichDevice(Device):

    def __init__(self, output: IO[str]) -> None:
        self.console = rich.console.Console(file=output)

    def render(self, search: Search) -> None:
        self.console.print(_create_table(search))

    def query(self, prefix: str) -> str:
        return rich.prompt.Prompt.ask(
            prompt=f"Key ({prefix}):" if prefix else "Key:",
            console=self.console,
        )


def _create_table(search: Search) -> rich.table.Table:
    table = rich.table.Table(show_header=True, header_style="bold")
    table.add_column("Key")
    table.add_column("Value")
    for key in search.flat_keys:
        table.add_row(key, str(search.get(key)))
    return table


@dataclass
class Viewer:
    search: Search
    device: Device

    def render(self) -> None:
        self.device.render(self.search)

    def interactive(self) -> None:
        stack: list[Search] = [self.search]
        try:
            while True:
                search = stack[-1]
                self.device.render(search)
                new_key = self.device.query(search.prefix)
                if new_key == "..":
                    stack.pop()
                    stack = stack if stack else [self.search]
                else:
                    stack.append(search.subsearch(new_key))
        except KeyboardInterrupt:
            pass
