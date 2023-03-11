from dataclasses import dataclass
from typing import Any

import pytest
from needle.search import Search, parse_key


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
    assert Search(test_case.obj).flat_keys == list(test_case.expected)


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


@pytest.mark.parametrize("test_case", TEST_SUIT, ids=[t.name for t in TEST_SUIT])
def test_getitem_key(test_case: TestCase) -> None:
    search = Search(test_case.obj)
    assert [search[key] for key in test_case.expected] == list(test_case.expected.values())


def test_getitem_raises_error_if_not_found() -> None:
    search = Search({"a": 1, "b": [2]})
    with pytest.raises(KeyError):
        search["c"]
    with pytest.raises(KeyError):
        search["b[1]"]


def test_find() -> None:
    search = Search({}, ["train.batch_size", "valid.batch_size", "model_name"])
    assert search.find("batch_size").flat_keys == ["train.batch_size", "valid.batch_size"]


def test_subsearch_gets_relative_key() -> None:
    search = Search({
        "train": {
            "batch_size": 64,
        },
        "valid": {
            "batch_size": 128,
        }
    })

    assert search.subsearch("train").get("batch_size") == 64
    assert search.subsearch("valid").get("batch_size") == 128


def test_subsearch_reduces_keys_range() -> None:
    search = Search({
        "pipeline": {
            "steps": ["preprocess", "train", "evaluate", "inference"],
            "datasets": {
                "train": "/drive/data/train.pkl",
                "valid": "/drive/data/valid.pkl",
            }
        }
    })

    subsearch = search.subsearch("pipeline.datasets")

    assert subsearch.flat_keys == ["train", "valid"]


def test_subsearch_does_not_copy_obj() -> None:
    search = Search({
        "training": {
            "dataset": "/drive/data",
            "params": {
                "lr": 1e-3,
                "opt": "SGD",
            }
        }
    })

    subsearch = search.subsearch("training.params")

    assert search.get("training.params") is subsearch.obj


def test_max_depth() -> None:
    search = Search({
        "A1": {
            "B1": {
                "C1": 1,
            },
            "B2": {
                "C2": 2,
                "C3": 3,
            },
            "C4": 1
        },
        "X1": 0,
        "X2": ['a', 'b', 'c']
    })

    assert search.max_depth(0).flat_keys == ["X1"]
    assert search.max_depth(1).flat_keys == ['A1.C4', 'X1', 'X2[0]', 'X2[1]', 'X2[2]']
    assert search.max_depth(2).flat_keys == ['A1.B1.C1', 'A1.B2.C2', 'A1.B2.C3', 'A1.C4', 'X1', 'X2[0]', 'X2[1]', 'X2[2]']


def test_fixed_depth() -> None:
    search = Search({
        "A1": {
            "B1": {
                "C1": 1,
            },
            "B2": {
                "C2": 2,
                "C3": 3,
            },
            "C4": 1
        },
        "X1": 0,
        "X2": ['a', 'b', 'c']
    })

    assert search.fixed_depth(0).flat_keys == ["X1"]
    assert search.fixed_depth(1).flat_keys == ["A1.C4", "X2[0]", "X2[1]", "X2[2]"]
    assert search.fixed_depth(2).flat_keys == ["A1.B1.C1", "A1.B2.C2", "A1.B2.C3"]


@pytest.mark.parametrize("max_depth,expected_key", [(0, "A"), (1, "A.B"), (2, "A.B.C")])
def test_depth_limited_search(max_depth: int, expected_key: str) -> None:
    assert Search({"A": {"B": {"C": 1}}}, max_depth=max_depth).flat_keys == [expected_key]
