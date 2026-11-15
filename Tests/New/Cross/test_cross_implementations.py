"""Phase 1 integrity: legacy, dataclass and pydantic implementations compared.

Independent of ``--backend``: each test uses the three implementations.
"""

import importlib
import json

import pytest

from pyleecan.classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
from pyleecan.classes_common.equality import values_equal
from pyleecan.Classes_new._import import import_class as import_dataclass
from pyleecan.Classes_pydantic._import import import_class as import_pydantic
from pyleecan.definitions import DOC_DIR
from pyleecan.Generator.read_fct import read_all

CLASS_NAMES = sorted(read_all(DOC_DIR))
LEGACY_NAMES = {new: legacy for legacy, new in NORMALIZATION_CLASS_NAMES.items()}
"""New name -> legacy name of the renamed classes (accepted difference)"""

IMPLEMENTATIONS = {"dataclass": import_dataclass, "pydantic": import_pydantic}


def _legacy_class(name):
    return getattr(importlib.import_module(f"pyleecan.Classes.{name}"), name)


def _with_legacy_names(data):
    """as_dict with the legacy names of the renamed classes."""
    if isinstance(data, dict):
        return {
            key: LEGACY_NAMES.get(value, value)
            if key == "__class__"
            else _with_legacy_names(value)
            for key, value in data.items()
        }
    if isinstance(data, list):
        return [_with_legacy_names(item) for item in data]
    return data


@pytest.mark.parametrize("implementation", sorted(IMPLEMENTATIONS))
@pytest.mark.parametrize("class_name", CLASS_NAMES)
def test_default_as_dict_like_legacy(class_name, implementation):
    """The default object has the same legacy dictionary as the legacy class"""
    legacy = _legacy_class(class_name)().as_dict()
    new = IMPLEMENTATIONS[implementation](class_name)().as_dict()
    assert values_equal(_with_legacy_names(new), legacy)


@pytest.mark.parametrize("implementation", sorted(IMPLEMENTATIONS))
@pytest.mark.parametrize("class_name", CLASS_NAMES)
def test_load_legacy_dict(class_name, implementation):
    """The legacy dictionary (through JSON) loads as the default object"""
    cls = IMPLEMENTATIONS[implementation](class_name)
    data = json.loads(json.dumps(_legacy_class(class_name)().as_dict()))
    assert cls.from_dict(data) == cls()


@pytest.mark.parametrize("class_name", CLASS_NAMES)
def test_same_target_dump(class_name):
    """Both implementations have the same JSON dump (target API)"""
    dataclass_dump = import_dataclass(class_name)().model_dump(mode="json")
    pydantic_dump = import_pydantic(class_name)().model_dump(mode="json")
    assert values_equal(dataclass_dump, pydantic_dump)
