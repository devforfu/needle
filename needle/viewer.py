from __future__ import annotations
from typing import IO

import rich.console
import rich.table

from needle.search import Search


class Viewer:

    def __init__(self, search: Search, output: IO | None = None) -> Viewer:
        self.search = search
        self.console = rich.console.Console(file=output)

    def print(self) -> None:
        table = rich.table.Table(show_header=True, header_style="bold")
        table.add_column("Key")
        table.add_column("Value")
        for key in self.search.flat_keys:
            table.add_row(key, str(self.search.get(key)))
        self.console.print(table)
