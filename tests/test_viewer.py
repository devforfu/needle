from dataclasses import dataclass, field

from needle import Search, Viewer
from needle.viewer import Device


@dataclass
class FakeDevice(Device):
    tables: list[list[tuple]] = field(default_factory=list)
    queries: list[str] = field(default_factory=list)
    commands: list[str] = field(default_factory=list)

    def render(self, search: Search) -> None:
        self.tables.append([(key, search.get(key)) for key in search.flat_keys])

    def query(self, prefix: str) -> str:
        self.queries.append(prefix)
        if self.commands:
            return self.commands.pop(0)
        raise KeyboardInterrupt()


def test_viewer() -> None:
    device = FakeDevice()

    search = Search({"a": {"one": 1, "two": 2}, "b": [{"x": 3}, {"y": 4}]})
    viewer = Viewer(search, device)
    viewer.render()

    assert not device.queries
    assert device.tables == [
        [
            ("a.one", 1),
            ("a.two", 2),
            ("b[0].x", 3),
            ("b[1].y", 4),
        ]
    ]


def test_viewer_interaction() -> None:
    device = FakeDevice(commands=["layers", "backbone", "..", "head"])

    search = Search({
        "layers": {
            "backbone": {
                "name": "resnet18",
            },
            "head": {
                "name": "linear",
                "in_features": 512,
                "out_features": 10,
            }
        }
    })
    viewer = Viewer(search, device)
    viewer.interactive()

    assert device.tables == [
        [
            ('layers.backbone.name', 'resnet18'),
            ('layers.head.name', 'linear'),
            ('layers.head.in_features', 512),
            ('layers.head.out_features', 10)
        ],
        [
            ('backbone.name', 'resnet18'),
            ('head.name', 'linear'),
            ('head.in_features', 512),
            ('head.out_features', 10)
        ],
        [
            ('name', 'resnet18')
        ],
        [
            ('backbone.name', 'resnet18'),
            ('head.name', 'linear'),
            ('head.in_features', 512),
            ('head.out_features', 10)
        ],
        [
            ('name', 'linear'),
            ('in_features', 512),
            ('out_features', 10)
        ]
    ]
