from dataclasses import dataclass
from typing import Any

import pytest
from needle import Search, parse_key


@dataclass
class TestCase:
    __test__ = False
    obj: Any
    expected: dict[str]
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
        expected={
            "pipeline[0].name": "training",
            "pipeline[0].params.model": "conv_net",
            "pipeline[0].params.layers[0]": 10,
            "pipeline[0].params.layers[1]": 20,
            "pipeline[0].params.layers[2]": 10,
            "pipeline[0].params.dataset_path": "/drive/dataset.train",
            "pipeline[1].name": "validation",
            "pipeline[1].params.dataset_path": "/drive/dataset.validation",
            "task.type": "classification",
            "task.n_classes": 10,
            "version": 1,
        },
        name="heterogeneous containers",
    ),
    TestCase(
        obj={"one": {"two": {"three": 1}}},
        expected={"one.two.three": 1},
        name="nested dict",
    ),
    TestCase(
        obj=["one", "two", "three"],
        expected={
            "[0]": "one",
            "[1]": "two",
            "[2]": "three"
        },
        name="one level list",
    ),
    TestCase(
        obj=[[["one"]], ["two"], "three", []],
        expected={
            "[0][0][0]": "one",
            "[1][0]": "two",
            "[2]": "three"
        },
        name="nested list"
    ),
    TestCase(
        obj=(((1,), (2,), (3, 4)), (5,)),
        expected={
            "[0][0][0]": 1,
            "[0][1][0]": 2,
            "[0][2][0]": 3,
            "[0][2][1]": 4,
            "[1][0]": 5
        },
        name="nested tuple",
    ),
    TestCase(
        obj={},
        expected={},
        name="empty",
    )
]


@pytest.mark.parametrize("test_case", TEST_SUIT, ids=[t.name for t in TEST_SUIT])
def test_flat_keys(test_case: TestCase) -> None:
    assert Search.create(test_case.obj).flat_keys == list(test_case.expected)


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


@pytest.mark.parametrize("test_case", TEST_SUIT, ids=[t.name for t in TEST_SUIT])
def test_get_key(test_case: TestCase) -> None:
    search = Search(test_case.obj)
    assert [search.get(key) for key in test_case.expected] == list(test_case.expected.values())


def test_find() -> None:
    search = Search.create({}, ["train.batch_size", "valid.batch_size", "model_name"])
    keys = search.find("batch_size")
    assert keys == ["train.batch_size", "valid.batch_size"]
