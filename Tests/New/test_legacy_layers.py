"""The legacy layers of both implementations apply the same legacy rules.

LegacyClass (Classes_new) and LegacyModel (Classes_pydantic) are checked on
the same generated classes: Phase 1 compares both implementations to legacy.
"""

import numpy as np
import pytest

from pyleecan.classes_common.errors import CheckError
from pyleecan.classes_common.functions import SourceFunction
from pyleecan.Classes_new._import import LOOKUP as DATACLASS_LOOKUP
from pyleecan.Classes_pydantic._import import LOOKUP as PYDANTIC_LOOKUP

INVALID = (ValueError, TypeError, CheckError)


@pytest.fixture(params=["dataclass", "pydantic"])
def import_class(request):
    lookup = {"dataclass": DATACLASS_LOOKUP, "pydantic": PYDANTIC_LOOKUP}[request.param]
    return lookup.import_class


def test_none_everywhere(import_class):
    lam = import_class("Lamination")(L1=None)  # float field, not optional
    assert lam.L1 is None
    lam.is_internal = None
    assert lam.is_internal is None


def test_integral_float_for_int(import_class):
    obj = import_class("InputCurrent")(Nt_tot=8.0)
    assert obj.Nt_tot == 8 and type(obj.Nt_tot) is int
    with pytest.raises(INVALID):
        obj.Nt_tot = 8.5


def test_min_still_checked(import_class):
    with pytest.raises(INVALID):
        import_class("InputCurrent")(Nt_tot=0)
    with pytest.raises(INVALID):
        import_class("Lamination")(L1=-1.0)


def test_type_still_checked(import_class):
    with pytest.raises(INVALID):
        import_class("Lamination")(L1="a")
    with pytest.raises(INVALID):
        import_class("Lamination")(is_internal=1)


def test_function_source(import_class):
    post = import_class("PostFunction")(run="lambda x: 2 * x")
    assert isinstance(post.run, SourceFunction) and post.run(2) == 4
    assert post.as_dict()["run"] == "lambda x: 2 * x"
    assert import_class("PostFunction").from_dict(post.as_dict()) == post
    with pytest.raises(INVALID):
        post.run = "not a function"


def test_import_matrix_from_array(import_class):
    obj = import_class("InputCurrent")(Is=np.array([[1.0, 2.0]]))
    assert type(obj.Is).__name__ == "ImportMatrixVal"
    assert np.array_equal(obj.Is.value, [[1.0, 2.0]])


def test_minus_one_default(import_class):
    obj = import_class("InputCurrent")()
    obj.Is = -1
    assert type(obj.Is).__name__ == "ImportMatrix"


def test_parent_links(import_class):
    lam = import_class("LamSlotWind")()
    assert lam.winding.parent is lam


def test_legacy_compare_paths(import_class):
    surf = import_class("SurfLine")
    segment = import_class("Segment")
    left = surf(line_list=[segment(begin=0, end=1), segment(begin=1, end=2)])
    right = surf(line_list=[segment(begin=0, end=1), segment(begin=1, end=3)])
    assert left.compare(right) == ["self.line_list[1].end"]
    assert left.compare(surf(line_list=[segment()])) == ["len(self.line_list)"]


def test_init_dict(import_class):
    SlotW10 = import_class("SlotW10")
    data = SlotW10(W0=1.0, H0=2.0).as_dict()
    data["__save_date__"] = "2020_01_01"  # Serialization key: ignored
    slot = SlotW10(init_dict=data, W1=3.0)
    assert type(slot) is SlotW10
    assert (slot.W0, slot.H0, slot.W1) == (1.0, 2.0, data["W1"])  # init_dict wins
    slot = SlotW10(init_dict={"W0": 4.0}, H0=5.0)  # Keyword kept when not in init_dict
    assert (slot.W0, slot.H0) == (4.0, 5.0)
    lam = import_class("LamSlot")(init_dict={"slot": data})  # Nested object built
    assert type(lam.slot) is SlotW10 and lam.slot.parent is lam
    with pytest.raises(TypeError):
        SlotW10(init_dict=[1.0])


def test_init_str(import_class, tmp_path):
    SlotW10 = import_class("SlotW10")
    path = str(tmp_path / "slot.json")
    SlotW10(W0=1.5).save(path)
    assert SlotW10(init_str=path).W0 == 1.5
