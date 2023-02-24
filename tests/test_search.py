from dataclasses import dataclass
from typing import Any

import pytest
from needle import Search, parse_key


@dataclass
class TestCase:
    __test__ = False
    obj: Any
    expected: list[str]
    name: str


TEST_SUIT = [
    TestCase(
        obj={
            "pipeline": [
                {
                    "name": "training",
                    "params": {
                        "model": "conv_net",
                        "layers": [10, 20, 10],
                        "dataset_path": "/drive/dataset.train",
                    }
                },
                {
                    "name": "validation",
                    "params": {
                        "dataset_path": "/drive/dataset.validation",
                    }
                }
            ],
            "task": {
                "type": "classification",
                "n_classes": 10,
            },
            "version": 1
        },
        expected=[
            "pipeline[0].name",
            "pipeline[0].params.model",
            "pipeline[0].params.layers[0]",
            "pipeline[0].params.layers[1]",
            "pipeline[0].params.layers[2]",
            "pipeline[0].params.dataset_path",
            "pipeline[1].name",
            "pipeline[1].params.dataset_path",
            "task.type",
            "task.n_classes",
            "version"
        ],
        name="heterogeneous containers",
    ),
    TestCase(
        obj={"one": {"two": {"three": 1}}},
        expected=["one.two.three"],
        name="nested dict",
    ),
    TestCase(
        obj=["one", "two", "three"],
        expected=["[0]", "[1]", "[2]"],
        name="one level list",
    ),
    TestCase(
        obj=[[["one"]], ["two"], "three", []],
        expected=["[0][0][0]", "[1][0]", "[2]"],
        name="nested list"
    ),
    TestCase(
        obj=(((1,), (2,), (3, 4)), (5,)),
        expected=["[0][0][0]", "[0][1][0]", "[0][2][0]", "[0][2][1]", "[1][0]"],
        name="nested tuple",
    ),
    TestCase(
        obj={},
        expected=[],
        name="empty",
    )
]


@pytest.mark.parametrize("test_case", TEST_SUIT, ids=[t.name for t in TEST_SUIT])
def test_flat_keys(test_case: TestCase) -> None:
    assert Search(test_case.obj).flat_keys == test_case.expected


@pytest.mark.parametrize("key,expected", [
    ("one.two.three", ["one", "two", "three"]),
    ("[0][1][2]", [0, 1, 2]),
    ("x[1].y[2].z", ["x", 1, "y", 2, "z"]),
    ("x.y.z[0]", ["x", "y", "z", 0]),
    ("pipeline.train.datasets[1].path", ["pipeline", "train", "datasets", 1, "path"])
])
def test_parse_key(key: str, expected: list) -> None:
    assert parse_key(key) == expected


@pytest.mark.parametrize("key", ["obj[key]", "obj[[1]]"])
def test_parse_key_fails_on_wrong_format(key: str) -> None:
    with pytest.raises(ValueError):
        parse_key(key)
