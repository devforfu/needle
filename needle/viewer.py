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


class RichDevice(Device):

    def __init__(self, output: IO[str] | None = None) -> None:
        self.console = rich.console.Console(file=output)

    def render(self, search: Search) -> None:
        self.console.print(create_table(search))

    def query(self, prefix: str) -> str:
        return rich.prompt.Prompt.ask(
            prompt=f"Key ({prefix}):" if prefix else "Key:",
            console=self.console,
        )


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
                self.device.render(stack.top)
                new_key = self.device.query(stack.top.prefix)
                if new_key == "..":
                    stack.pop()
                    stack = Stack(self.search) if stack.empty else stack
                else:
                    stack.subsearch(new_key)

        except KeyboardInterrupt:
            pass


def main() -> None:
    search = Search({
        "dataset": {
            "path": "/drive/dataset",
            "metadata": "/drive/metadata.json",
            "stats": ([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        },
        "split": "/drive/split.json",
        "training": {
            "model": {
                "backbone": "resnet18",
                "head": {
                    "n_classes": 10
                },
                "aux": None
            },
            "data_loader": {
                "batch_size": 128,
                "num_workers": 8,
            }
        },
        "evaluation": {
            "data_loader": {
                "batch_size": 256,
                "num_workers": 8
            }
        },
        "test": {
            "dataset": "/data/test",
            "enabled": True,
        }
    })
    viewer = Viewer(search, RichDevice())
    viewer.render()


if __name__ == '__main__':
    main()
