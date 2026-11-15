"""Contract of the target bases (Phase 2 design, see PLAN.md).

The same specification for the dataclass base (PyleecanClass) and the
pydantic base (PyleecanModel), on small hand-written models: no legacy layer.
"""

import json
from dataclasses import dataclass, field
from typing import ClassVar

import numpy as np
import pytest
from dacite import DaciteError
from pydantic import Field

from pyleecan.classes_common.errors import CheckError
from pyleecan.Classes_new import _import as dataclass_import
from pyleecan.Classes_new._pyleecan_class import PyleecanClass
from pyleecan.Classes_pydantic import _import as pydantic_import
from pyleecan.Classes_pydantic._pyleecan_model import Complex, NDArray, PyleecanModel

INVALID = (ValueError, TypeError, DaciteError, CheckError)
"""Errors of an invalid value or dump: pydantic ValidationError (a ValueError),
dacite errors and the shared check errors (CheckTypeError, CheckMinError...)"""


# Dataclass models
@dataclass(eq=False)
class DShape(PyleecanClass):
    name: str = ""
    _package: ClassVar[str] = "Test"


@dataclass(eq=False)
class DCircle(DShape):
    radius: float = field(default=1.0, metadata={"min": 0})
    center: complex = 0j
    values: np.ndarray | None = None
    _package: ClassVar[str] = "Test"


@dataclass(eq=False)
class DDrawing(PyleecanClass):
    main: DShape | None = None
    shapes: list[DShape] = field(default_factory=list)
    _package: ClassVar[str] = "Test"


# Pydantic models
class MShape(PyleecanModel):
    name: str = ""
    _package: ClassVar[str] = "Test"


class MCircle(MShape):
    radius: float = Field(default=1.0, ge=0)
    center: Complex = 0j
    values: NDArray | None = None
    _package: ClassVar[str] = "Test"


class MDrawing(PyleecanModel):
    main: MShape | None = None
    shapes: list[MShape] = Field(default_factory=list)
    _package: ClassVar[str] = "Test"


MODELS = {
    "dataclass": (dataclass_import.LOOKUP, DShape, DCircle, DDrawing),
    "pydantic": (pydantic_import.LOOKUP, MShape, MCircle, MDrawing),
}


@pytest.fixture(params=sorted(MODELS))
def models(request, monkeypatch):
    """(Shape, Circle, Drawing) of a backend, known by the class lookup"""
    lookup, shape, circle, drawing = MODELS[request.param]
    registry = {cls.__name__: cls for cls in (shape, circle, drawing)}
    find_class = lookup.find_class
    monkeypatch.setattr(
        lookup, "find_class", lambda name: registry.get(name) or find_class(name)
    )
    return shape, circle, drawing


def _drawing(circle, drawing):
    return drawing(
        main=circle(name="c", radius=2.0, center=1 + 2j, values=np.array([1.0, 2.0])),
        shapes=[circle(radius=3.0)],
    )


def test_keyword_construction(models):
    _, circle, _ = models
    obj = circle(radius=2.0)
    assert obj.radius == 2.0 and obj.name == "" and obj.center == 0j


def test_no_parent_link(models):
    _, circle, drawing = models
    obj = _drawing(circle, drawing)
    assert not hasattr(obj.main, "parent")


def test_dump_python(models):
    _, circle, drawing = models
    obj = _drawing(circle, drawing)
    data = obj.model_dump()
    assert data["__class__"] == drawing.__name__
    assert data["main"]["__class__"] == circle.__name__  # actual class
    assert data["main"]["center"] == 1 + 2j  # values kept
    assert isinstance(data["main"]["values"], np.ndarray)


def test_dump_json(models):
    _, circle, drawing = models
    data = _drawing(circle, drawing).model_dump(mode="json")
    assert data["main"]["center"] == "1+2j"
    assert data["main"]["values"] == [1.0, 2.0]
    json.dumps(data)  # JSON-ready


@pytest.mark.parametrize("mode", ["python", "json"])
def test_validate_round_trip(models, mode):
    _, circle, drawing = models
    obj = _drawing(circle, drawing)
    loaded = drawing.model_validate(obj.model_dump(mode=mode))
    assert loaded == obj
    assert type(loaded.main) is circle  # polymorphic loading
    assert isinstance(loaded.main.values, np.ndarray)


def test_validate_subclass_from_base(models):
    shape, circle, _ = models
    loaded = shape.model_validate(circle(radius=5.0).model_dump())
    assert type(loaded) is circle and loaded.radius == 5.0


def test_validate_rejects_unknown_key(models):
    _, circle, _ = models
    data = circle().model_dump()
    data["unknown"] = 1
    with pytest.raises(INVALID):
        circle.model_validate(data)


def test_validate_rejects_other_class(models):
    _, circle, drawing = models
    with pytest.raises(INVALID):
        circle.model_validate(drawing().model_dump())


def test_copy(models):
    _, circle, drawing = models
    obj = _drawing(circle, drawing)
    deep = obj.model_copy(deep=True)
    assert deep == obj and deep.main is not obj.main
    deep.main.values[0] = 10.0
    assert obj.main.values[0] == 1.0
    shallow = obj.model_copy()
    assert shallow.main is obj.main
    updated = obj.model_copy(update={"main": None})
    assert updated.main is None and obj.main is not None


def test_equality(models):
    shape, circle, _ = models
    assert circle(values=np.array([1.0, np.nan])) == circle(
        values=np.array([1.0, np.nan])
    )
    assert circle(values=np.array([1.0])) != circle(values=np.array([2.0]))
    assert circle() != shape()


def test_type_validation(models):
    _, circle, drawing = models
    with pytest.raises(INVALID):
        circle(radius="a")
    obj = circle()
    with pytest.raises(INVALID):
        obj.radius = "a"
    with pytest.raises(INVALID):
        obj.name = None  # not optional
    with pytest.raises(INVALID):
        drawing(shapes=[circle(), "a"])  # list items are checked


def test_int_and_bool_strict(models):
    _, circle, _ = models
    with pytest.raises(INVALID):
        circle(radius=True)  # bool is not a number
    circle(radius=2)  # int accepted for float


def test_min_validation(models):
    _, circle, _ = models
    with pytest.raises(INVALID):
        circle(radius=-1.0)
    obj = circle(radius=0.0)  # bound included
    with pytest.raises(INVALID):
        obj.radius = -0.5


def test_nested_dict_is_built(models):
    _, circle, drawing = models
    obj = drawing(main=circle(radius=4.0).model_dump())
    assert type(obj.main) is circle and obj.main.radius == 4.0


def test_native_complex(models):
    _, circle, _ = models
    assert circle(center=1).center == 1 + 0j
    assert circle.model_validate({"center": "(1+2j)"}).center == 1 + 2j
