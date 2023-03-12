from __future__ import annotations
from dataclasses import dataclass
from typing import Any, IO, Protocol

import rich.console
import rich.prompt
import rich.table

from needle.stack import Stack
from needle.search import Search


class Device(Protocol):

    def render(self, search: Search) -> None:
        raise NotImplementedError

    def query(self, prefix: str) -> str:
        raise NotImplementedError

    def clear(self) -> None:
        pass


class RichDevice(Device):

    def __init__(self, output: IO[str] | None = None) -> None:
        self.console = rich.console.Console(file=output)

    def render(self, search: Search) -> None:
        self.console.print(create_table(search))

    def query(self, prefix: str) -> str:
        return rich.prompt.Prompt.ask(
            prompt=f"Key ({prefix})" if prefix else "Key",
            console=self.console,
        )

    def clear(self) -> None:
        self.console.clear()


def create_table(search: Search) -> rich.table.Table:
    table = rich.table.Table(show_header=True, header_style="bold")
    table.add_column("Key")
    table.add_column("Value")
    for key in search.flat_keys:
        table.add_row(key, format_value(search.get(key)))
    return table


def format_value(value: Any) -> str:
    if isinstance(value, bool):
        return f"[yellow]{value}[/yellow]"
    elif isinstance(value, int):
        return f"[blue]{value}[/blue]"
    elif isinstance(value, float):
        return f"[blue]{value:.4f}[/blue]"
    elif isinstance(value, str):
        return f"[green]\"{value}\"[/green]"
    elif value is None:
        return f"[red]{value}[/red]"
    return str(value)


@dataclass
class Viewer:
    search: Search
    device: Device

    def render(self) -> None:
        self.device.render(self.search)

    def interactive(self) -> None:
        stack = Stack(self.search)
        try:
            while True:
                self.device.clear()
                self.device.render(stack.top)
                new_key = self.device.query(stack.top.prefix)
                if new_key == "..":
                    stack.pop()
                    stack = Stack(self.search) if stack.empty else stack
                else:
                    try:
                        stack.subsearch(new_key)
                    except KeyError:
                        pass

        except KeyboardInterrupt:
            pass
