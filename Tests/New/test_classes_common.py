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
from pyleecan.Classes_pydantic import _import as _import_pydantic
from pyleecan.Classes_pydantic._class_info import PYLEECAN_BASES as PYDANTIC_BASES
from pyleecan.Classes_pydantic._class_info import ClassInfo as PydanticClassInfo
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
    for base in PYLEECAN_BASES + PYDANTIC_BASES:
        assert issubclass(base, PyleecanBase)
        assert not is_generated_class(base)


def test_is_generated_class():
    from pyleecan.Classes_new.geometry.segment import Segment
    from pyleecan.Classes_pydantic.geometry.segment import Segment as PydanticSegment

    assert is_generated_class(Segment)  # dataclass
    assert is_generated_class(PydanticSegment)  # pydantic model
    assert not is_generated_class(Segment())
    assert not is_generated_class(int)


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_backend_bases(backend):
    """Each package holds only classes of its own base"""
    lookup, bases = {
        "dataclass": (_import.LOOKUP, PYLEECAN_BASES),
        "pydantic": (_import_pydantic.LOOKUP, PYDANTIC_BASES),
    }[backend]
    for name in ("Segment", "SurfLine", "LamSlotWind", "Simu1", "MagFEMM"):
        assert issubclass(lookup.import_class(name), bases), name


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


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_class_info_bound_to_package(backend):
    info_class, package = {
        "dataclass": (ClassInfo, "Classes_new"),
        "pydantic": (PydanticClassInfo, "Classes_pydantic"),
    }[backend]
    class_dict = info_class().get_dict()
    assert len(class_dict) == len(find_module_paths(Path(MAIN_DIR) / package))
    assert class_dict["LamSlotWind"]["module"].startswith(f"pyleecan.{package}.")
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


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_method_errors_are_shared(backend):
    """Both implementations raise the same error class (classes_common.errors)"""
    from pyleecan.classes_common.errors import PointSegmentError

    lookup = {"dataclass": _import.LOOKUP, "pydantic": _import_pydantic.LOOKUP}[backend]
    with pytest.raises(PointSegmentError):
        lookup.import_class("Segment")(begin=0, end=0).check()


def test_redirect_legacy_method_error_import():
    from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
        _redirect_shared_error_imports,
    )

    source = "from pyleecan.Methods.Geometry.Segment import PointSegmentError, helper\n"
    result = _redirect_shared_error_imports(
        source, "Tests", method_error_names={"PointSegmentError"}
    )
    assert "from pyleecan.Methods.Geometry.Segment import helper" in result
    assert "import PointSegmentError" in result and "_error" in result
