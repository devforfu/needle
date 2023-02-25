import io

from needle import Search, Viewer


def test_viewer() -> None:
    buf = io.StringIO()

    search = Search({"a": {"one": 1, "two": 2}, "b": [{"x": 3}, {"y": 4}]})
    viewer = Viewer(search, buf)
    viewer.print()

    assert buf.getvalue() == (
        "┏━━━━━━━━┳━━━━━━━┓\n"
        "┃ Key    ┃ Value ┃\n"
        "┡━━━━━━━━╇━━━━━━━┩\n"
        "│ a.one  │ 1     │\n"
        "│ a.two  │ 2     │\n"
        "│ b[0].x │ 3     │\n"
        "│ b[1].y │ 4     │\n"
        "└────────┴───────┘\n"
    )
