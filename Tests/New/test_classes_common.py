"""Support shared by the class implementations (pyleecan.classes_common)."""

from pathlib import Path

import pytest

from pyleecan.classes_common.base import PyleecanBase, is_generated_class
from pyleecan.classes_common.class_lookup import (
    ClassLookup,
    class_module_name,
    find_module_paths,
)
from pyleecan.classes_common.errors import CheckTypeError, InitUnKnowClassError
from pyleecan.Classes_new import _import
from pyleecan.Classes_new._class_info import PYLEECAN_BASES, ClassInfo
from pyleecan.Classes_new._pyleecan_class import PyleecanClass
from pyleecan.Classes_new._pyleecan_model import PyleecanModel
from pyleecan.definitions import MAIN_DIR

CLASS_DIR = Path(MAIN_DIR) / "Classes_new"
COMMON_DIR = Path(MAIN_DIR) / "classes_common"


@pytest.mark.parametrize(
    "class_name, module_name",
    [
        ("LamSlotWind", "lam_slot_wind"),
        ("EEC_SCIM", "eec_scim"),
        ("SlotW11_2", "slot_w_11_2"),
        ("ElecLUTdq", "elec_lut_dq"),
        ("Data1D", "data_1d"),  # special name
        ("OPdq", "op_dq"),  # special name
    ],
)
def test_class_module_name(class_name, module_name):
    assert class_module_name(class_name) == module_name


def test_bases_share_the_marker():
    for base in PYLEECAN_BASES:
        assert issubclass(base, PyleecanBase)
        assert not is_generated_class(base)


def test_is_generated_class():
    from pyleecan.Classes_new.geometry.segment import Segment
    from pyleecan.Classes_new.machine.lam_slot_wind import LamSlotWind

    assert is_generated_class(Segment)  # pydantic model (WiP)
    assert is_generated_class(LamSlotWind)  # dataclass
    assert not is_generated_class(Segment())
    assert not is_generated_class(int)


def test_lookup_bound_to_package():
    """The lookup of Classes_new is the shared one bound to Classes_new"""
    assert isinstance(_import.LOOKUP, ClassLookup)
    assert _import.LOOKUP.package == "pyleecan.Classes_new"
    assert _import.LOOKUP.module_paths() == find_module_paths(CLASS_DIR)
    lam = _import.import_class("LamSlotWind")
    assert lam.__module__ == "pyleecan.Classes_new.machine.lam_slot_wind"
    assert _import.LamSlotWind is lam  # lazy module attribute


def test_lookup_legacy_and_unknown_names():
    assert _import.import_class("Norm_ref").__name__ == "NormRef"
    with pytest.raises(InitUnKnowClassError):
        _import.import_class("NotAPyleecanClass")
    with pytest.raises(InitUnKnowClassError):
        _import.import_class("_private")
    with pytest.raises(AttributeError):
        _import.NotAPyleecanClass


def test_lookup_rejects_duplicate_module(tmp_path):
    for subpackage in ("a", "b"):
        (tmp_path / subpackage).mkdir()
        (tmp_path / subpackage / "__init__.py").write_text("")
        (tmp_path / subpackage / "segment.py").write_text("")
    with pytest.raises(ImportError):
        find_module_paths(tmp_path)


def test_class_info_bound_to_package():
    class_dict = ClassInfo().get_dict()
    assert len(class_dict) == len(find_module_paths(CLASS_DIR))
    assert class_dict["LamSlotWind"]["module"].startswith("pyleecan.Classes_new.")
    assert class_dict["LamSlotWind"]["mother"] == "LamSlot"
    assert "LamSlotWind" in class_dict["Lamination"]["daughters"]


def test_shared_errors():
    """One exception class, whatever the implementation that raises it"""
    from pyleecan.classes_common import check

    with pytest.raises(CheckTypeError):
        check.check_var("x", "a", "float")


def test_support_moved_out_of_classes_new():
    for name in ("_check.py", "_error.py", "_femm_handler.py", "_parent_types.py"):
        assert not (CLASS_DIR / name).exists(), name
    for name in ("check.py", "errors.py", "femm_handler.py", "parent_types.py"):
        assert (COMMON_DIR / name).is_file(), name
