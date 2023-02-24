from dataclasses import dataclass
from typing import Any

import pytest
from needle import Search


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
def test_search(test_case: TestCase) -> None:
    assert Search(test_case.obj).flat_keys == test_case.expected