"""Step 14: members of the daughters declared on the base classes for the
type checkers only (TYPE_CHECKING_MEMBERS): no field, no attribute at runtime."""

from dataclasses import fields

import pytest

from pyleecan.Classes_new._import import import_class as import_dataclass
from pyleecan.Classes_pydantic._import import import_class as import_pydantic
from pyleecan.Generator.ClassGenerator.New.class_generator import TYPE_CHECKING_MEMBERS


def _members(spec):
    for line in spec["lines"]:
        name = line[4:].split("(")[0] if line.startswith("def ") else line.split(":")[0]
        yield name.strip()


@pytest.mark.parametrize("class_name", sorted(TYPE_CHECKING_MEMBERS))
def test_declared_members_absent_at_runtime(class_name):
    dataclass_cls = import_dataclass(class_name)
    pydantic_cls = import_pydantic(class_name)
    dataclass_fields = {item.name for item in fields(dataclass_cls)}
    for name in _members(TYPE_CHECKING_MEMBERS[class_name]):
        assert name not in dataclass_fields
        assert name not in pydantic_cls.model_fields
        assert name not in vars(dataclass_cls) and name not in vars(pydantic_cls)


def test_daughter_keeps_its_own_member():
    MachineIPMSM = import_dataclass("MachineIPMSM")
    machine = MachineIPMSM()
    assert machine.stator is not None and machine.rotor is not None
