"""Pydantic base of the classes of the PYDANTIC_PACKAGES (Geometry)."""

import json
from unittest.mock import MagicMock

import numpy as np
import pytest
from pydantic import ValidationError

from pyleecan.Classes_new._pyleecan_model import PyleecanModel
from pyleecan.Classes_new.geometry.arc_1 import Arc1
from pyleecan.Classes_new.geometry.polar_arc import PolarArc
from pyleecan.Classes_new.geometry.segment import Segment
from pyleecan.Classes_new.geometry.surf_line import SurfLine
from pyleecan.Classes_new.geometry.surf_ring import SurfRing
from pyleecan.Classes_new.geometry.trapeze import Trapeze
from pyleecan.Classes_new.slot.slot_ud import SlotUD


def test_geometry_classes_are_pydantic_models():
    for cls in (Arc1, PolarArc, Segment, SurfLine, SurfRing, Trapeze):
        assert issubclass(cls, PyleecanModel)


def test_validation_at_construction_and_assignment():
    with pytest.raises(ValidationError):
        Trapeze(height=-1)  # Minimum 0
    trapeze = Trapeze()
    with pytest.raises(ValidationError):
        trapeze.W1 = "1"  # No silent conversion
    with pytest.raises(ValidationError):
        trapeze.unknown = 1  # No new attribute
    trapeze.W1 = 2  # int accepted for a float
    assert trapeze.W1 == 2.0
    with pytest.raises(TypeError):
        Segment(0, 1)  # Keyword arguments only


def test_legacy_values():
    segment = Segment(begin=np.complex128(1 + 1j), end=2)
    assert segment.begin == 1 + 1j and segment.end == 2 + 0j
    segment.prop_dict = None  # Every field accepts None
    ring = SurfRing(out_surf=-1)  # -1 sets the default object
    assert type(ring.out_surf).__name__ == "Surface"


def test_parent_links():
    lines = [Segment(begin=0, end=1), Segment(begin=1, end=1j)]
    surface = SurfLine(line_list=lines)
    assert all(line.parent is surface for line in surface.line_list)
    # A dataclass holding pydantic objects
    slot = SlotUD(line_list=[Segment(begin=0, end=1)])
    assert slot.line_list[0].parent is slot


def test_round_trip_through_a_dataclass():
    slot = SlotUD(line_list=[Segment(begin=0, end=1j), Arc1(begin=1j, end=1, radius=1)])
    data = json.loads(json.dumps(slot.as_dict()))
    assert data["line_list"][0] == {
        "prop_dict": None,
        "begin": "0j",
        "end": "1j",
        "__class__": "Segment",
    }
    loaded = SlotUD.from_dict(data)
    assert [type(line) for line in loaded.line_list] == [Segment, Arc1]
    assert loaded == slot
    assert loaded.line_list[0].parent is loaded


def test_load_ignores_unknown_keys_like_init_dict():
    """Saved files hold keys that are not fields (metadata, removed properties)."""
    segment = Segment.from_dict(
        {
            "__class__": "Segment",
            "__save_date__": "2021_10_21",
            "__version__": "pyleecan_1.3.6",
            "begin": 0,
            "end": "1j",
            "label": "",  # Property removed since this file was saved
        }
    )
    assert segment.end == 1j
    with pytest.raises(ValidationError):
        Segment(begin=0, end=1, label="")  # The constructor rejects them


def test_existing_method_can_be_replaced_on_an_object():
    """Like FrozenClass: e.g. a mock in tests (not a field)."""
    surface = PolarArc()
    surface.get_lines = MagicMock(return_value=[])
    assert surface.get_lines() == []
    assert "get_lines" not in surface.as_dict()
    assert PolarArc().get_lines() != []
