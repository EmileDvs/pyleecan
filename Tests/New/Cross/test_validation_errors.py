"""Phase 1 error contract: a rejected value raises the legacy errors.

Legacy, dataclass and pydantic (legacy layer) implementations raise the same
error class (``CheckMinError``, ``CheckMaxError``, ``CheckTypeError``) with the
same message, on assignment and construction: the GUI and the user code catch
``CheckError`` whatever the backend. Independent of ``--backend``.
"""

import importlib

import pytest
from pydantic import ValidationError

from pyleecan.classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
from pyleecan.Classes_new._import import import_class as import_dataclass
from pyleecan.Classes_pydantic._import import import_class as import_pydantic
from pyleecan.definitions import DOC_DIR
from pyleecan.Generator.read_fct import read_all

GEN_DICT = read_all(DOC_DIR)
NEW_NAMES = dict(NORMALIZATION_CLASS_NAMES)


def _cases():
    """(class, field, rejected value) of the float fields with limits."""
    cases = []
    for class_name, class_dict in sorted(GEN_DICT.items()):
        for prop in class_dict["properties"]:
            if prop["type"] != "float":
                continue
            if prop["min"] not in ("", None):
                cases.append((class_name, prop["name"], float(prop["min"]) - 1))
            if prop["max"] not in ("", None):
                cases.append((class_name, prop["name"], float(prop["max"]) + 1))
            cases.append((class_name, prop["name"], "not a number"))
    return cases


CASES = _cases()


def _legacy_class(name):
    return getattr(importlib.import_module(f"pyleecan.Classes.{name}"), name)


def _outcome(action):
    try:
        action()
    except Exception as error:  # noqa: BLE001 (any error compared)
        return type(error).__name__, str(error)
    return None


@pytest.mark.parametrize(
    "class_name, field, value", CASES, ids=[f"{c}.{f}={v!r}" for c, f, v in CASES]
)
def test_same_error_on_assignment(class_name, field, value):
    legacy = _legacy_class(class_name)
    try:
        legacy_obj = legacy()
    except Exception:  # noqa: BLE001
        pytest.skip("default legacy object not built")
    expected = _outcome(lambda: setattr(legacy_obj, field, value))
    assert expected is not None and expected[0].startswith("Check")
    new_name = NEW_NAMES.get(class_name, class_name)
    for import_class in (import_dataclass, import_pydantic):
        obj = import_class(new_name)()
        name, message = _outcome(lambda obj=obj: setattr(obj, field, value))
        assert name == expected[0]
        if expected[0] != "CheckTypeError":  # Legacy type names: "Double"...
            assert message == expected[1]


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_error_contract(backend):
    from pyleecan.classes_common.errors import (
        CheckError,
        CheckMaxError,
        CheckMinError,
        CheckTypeError,
    )

    import_class = {"dataclass": import_dataclass, "pydantic": import_pydantic}[backend]
    SlotW10 = import_class("SlotW10")
    LamSlotWind = import_class("LamSlotWind")
    with pytest.raises(CheckMinError, match=r"^W0 must be >= 0, -1.0 given$"):
        SlotW10(W0=-1.0)
    with pytest.raises(CheckMinError, match=r"^W0 must be >= 0, -2.0 given$"):
        SlotW10().W0 = -2.0
    with pytest.raises(CheckMaxError, match=r"^Kf1 must be <= 1, 1.5 given$"):
        LamSlotWind().Kf1 = 1.5
    with pytest.raises(CheckTypeError, match=r"^For W0 : float expected, str given$"):
        SlotW10().W0 = "a"
    with pytest.raises(CheckMinError, match=r"^W0 must be >= 0, -1.0 given$"):
        LamSlotWind(slot={"__class__": "SlotW10", "W0": -1.0})  # Nested object
    with pytest.raises(CheckMinError):
        LamSlotWind.from_dict(
            {"__class__": "LamSlotWind", "slot": {"__class__": "SlotW10", "W0": -1}}
        )
    with pytest.raises(TypeError, match="unexpected keyword argument 'foo'"):
        SlotW10(foo=1)
    assert issubclass(CheckMinError, CheckError)
    if backend == "pydantic":  # The pydantic error chained
        with pytest.raises(CheckMinError) as info:
            SlotW10().W0 = -1.0
        assert isinstance(info.value.__cause__, ValidationError)


def test_target_model_keeps_validation_error():
    """Only the legacy layer converts: the target base raises ValidationError."""
    from pydantic import Field

    from pyleecan.Classes_pydantic._pyleecan_model import PyleecanModel

    class Target(PyleecanModel):
        x: float = Field(default=0, ge=0)

    with pytest.raises(ValidationError):
        Target(x=-1.0)
    with pytest.raises(ValidationError):
        Target.model_validate({"x": -1.0})


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_unknown_attribute_rejected_like_legacy(backend):
    from unittest.mock import MagicMock

    import_class = {"dataclass": import_dataclass, "pydantic": import_pydantic}[backend]
    legacy = _legacy_class("Trapeze")()
    expected = _outcome(lambda: setattr(legacy, "unknown", 1))
    assert expected[0] == "FrozenError"
    trapeze = import_class("Trapeze")()
    with pytest.raises(AttributeError) as info:
        trapeze.unknown = 1
    assert str(info.value) == expected[1]
    trapeze.get_lines = MagicMock(return_value=[])  # Existing method: replaced
    assert trapeze.get_lines() == []
