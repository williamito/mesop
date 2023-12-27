from dataclasses import dataclass, field

from mesop.dataclass_utils.dataclass_utils import (
  dataclass_with_defaults,
  serialize_dataclass,
  update_dataclass_from_json,
)


@dataclass
class C:
  val: str = "<init>"


@dataclass
class B:
  c: C = field(default_factory=C)


@dataclass
class A:
  b: B = field(default_factory=B)


JSON_STR = """{"b": {"c": {"val": "<init>"}}}"""


@dataclass_with_defaults
class DataclassNoDefaults:
  foo: int


@dataclass_with_defaults
class NestedDataclassNoDefaults:
  a: DataclassNoDefaults
  list_a: list[DataclassNoDefaults]


def test_dataclass_defaults():
  d = DataclassNoDefaults()
  assert d.foo == 0


def test_dataclass_defaults_recursive():
  d = NestedDataclassNoDefaults()
  assert d.a.foo == 0
  assert d.list_a == []


def test_serialize_dataclass():
  val = serialize_dataclass(A())
  assert val == """{"b": {"c": {"val": "<init>"}}}"""


def test_update_dataclass_from_json_nested_dataclass():
  b = B()
  update_dataclass_from_json(b, """{"c": {"val": "<init>"}}""")
  assert b.c.val == "<init>"

  a = A()
  update_dataclass_from_json(a, JSON_STR)
  assert a.b.c.val == "<init>"


if __name__ == "__main__":
  import pytest

  raise SystemExit(pytest.main([__file__]))