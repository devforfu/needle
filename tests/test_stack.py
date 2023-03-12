import copy
from dataclasses import dataclass
from typing import Any

import pytest

from needle.search import Search
from needle.stack import Stack


@pytest.fixture(scope="module")
def search() -> Search:
    return Search({
        "A1": [{}, {"first": 1}, {"second": 2}],
        "A2": {"B21": [1, 2, 3], "B22": "string"},
        "A3": {"B3": {"C3": ["one", "two"]}},
        "A4": None,
    })


@pytest.fixture
def stack(search: Search) -> Stack:
    return Stack(search)


@dataclass
class TestCase:
    __test__ = False
    method: str
    param: Any
    expected: Search


@pytest.fixture
def delegates(search: Search) -> list[TestCase]:
    return [
        TestCase(method="find", param="first", expected=search.find("first")),
        TestCase(method="subsearch", param="A1[1]", expected=search.subsearch("A1[1]")),
        TestCase(method="max_depth", param=2, expected=search.max_depth(2)),
        TestCase(method="fixed_depth", param=2, expected=search.fixed_depth(2)),
    ]


def test_top(stack: Stack, search: Search) -> None:
    assert stack.top.flat_keys == search.flat_keys


def test_delegates(stack: Stack, delegates: list[TestCase]) -> None:
    for delegate in delegates:
        cloned_stack = copy.deepcopy(stack)
        assert getattr(cloned_stack, delegate.method)(delegate.param).top == delegate.expected


def test_tracking_search_method_calls(stack: Stack, search: Search) -> None:
    assert stack.top == search
    assert stack.subsearch("A1").top == search.subsearch("A1")
    assert stack.find("first").top == search.subsearch("A1").find("first")
    assert stack.pop().pop().top == search
