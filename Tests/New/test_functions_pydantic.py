"""Functions_pydantic: Functions_new rewritten for the pydantic classes."""

import importlib
import re
from glob import glob
from os.path import basename, join
from pathlib import Path

import pytest

from pyleecan.classes_common.equality import values_equal
from pyleecan.definitions import DATA_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.generate_function_pydantic import (
    rewrite_function_source,
)

ROOT = Path(MAIN_DIR)
VENDORED = ("_smoot", "_swat_em")


def _modules(package):
    """Python modules of a function package (vendored code excluded)."""
    modules = []
    for path in sorted((ROOT / package).rglob("*.py")):
        relative = path.relative_to(ROOT / package)
        if relative.parts[0] in VENDORED or "__pycache__" in relative.parts:
            continue
        parts = list(relative.with_suffix("").parts)
        if parts[-1] == "__init__":
            parts = parts[:-1]
        modules.append(".".join(parts))
    return modules


def test_rewrite_function_source():
    source = (
        "from ...Classes_new.geometry.segment import Segment\n"
        "from ...Classes_new._import import import_class\n"
        "from ...Classes_new._swat_em import datamodel\n"
        "from ...classes_common.errors import CheckTypeError\n"
        "from ..init_fig import init_fig\n"
        "from .._swat_em.config import config\n"
        "\n"
        "\n"
        "def f():\n"
        "    from ...Classes_new.machine.lam_slot import LamSlot\n"
        "\n"
        "    return import_module('pyleecan.Functions_new.Geometry.x')\n"
    )
    expected = (
        "from ...Classes_pydantic.geometry.segment import Segment\n"
        "from ...Classes_pydantic._import import import_class\n"
        "from ...Classes_new._swat_em import datamodel\n"  # vendored: kept
        "from ...classes_common.errors import CheckTypeError\n"
        "from ..init_fig import init_fig\n"  # relative: same package tree
        "from ...Functions_new._swat_em.config import config\n"  # vendored: kept
        "\n"
        "\n"
        "def f():\n"
        "    from ...Classes_pydantic.machine.lam_slot import LamSlot\n"
        "\n"
        "    return import_module('pyleecan.Functions_pydantic.Geometry.x')\n"
    )
    assert rewrite_function_source(source, ["Geometry"]) == expected


def test_same_module_tree():
    assert _modules("Functions_pydantic") == _modules("Functions_new")


@pytest.mark.parametrize("package", ["Functions_pydantic", "Classes_pydantic"])
def test_no_dataclass_reference(package):
    """The pydantic packages only use Classes_new/Functions_new for vendored code"""
    pattern = re.compile(r"(Classes_new|Functions_new)\.(?!_smoot|_swat_em)\w")
    found = [
        f"{path.relative_to(ROOT)}:{number}"
        for path in (ROOT / package).rglob("*.py")
        if "__pycache__" not in path.parts
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1)
        if pattern.search(line)
    ]
    assert not found


@pytest.mark.parametrize("module", _modules("Functions_pydantic"))
def test_import(module):
    importlib.import_module("pyleecan.Functions_pydantic." + module if module else "pyleecan.Functions_pydantic")


@pytest.mark.parametrize(
    "path",
    sorted(glob(join(DATA_DIR, "Machine", "*.json"))),
    ids=lambda path: basename(path),
)
def test_load_machine_like_legacy(path):
    """A machine file loads the same with the legacy, dataclass and pydantic load"""
    from pyleecan.Functions.load import load as load_legacy
    from pyleecan.Functions_new.load import load as load_dataclass
    from pyleecan.Functions_pydantic.load import load as load_pydantic

    reference = load_legacy(path).as_dict()
    dataclass_machine = load_dataclass(path)
    pydantic_machine = load_pydantic(path)
    assert type(dataclass_machine).__module__.startswith("pyleecan.Classes_new.")
    assert type(pydantic_machine).__module__.startswith("pyleecan.Classes_pydantic.")
    assert values_equal(dataclass_machine.as_dict(), reference)
    assert values_equal(pydantic_machine.as_dict(), reference)


@pytest.mark.parametrize("backend", ["dataclass", "pydantic"])
def test_save_load_round_trip(backend, tmp_path):
    """obj.save uses the functions of its own backend"""
    if backend == "dataclass":
        from pyleecan.Functions_new.load import load
    else:
        from pyleecan.Functions_pydantic.load import load
    machine = load(join(DATA_DIR, "Machine", "Toyota_Prius.json"))
    path = str(tmp_path / "machine.json")
    machine.save(path)
    loaded = load(path)
    assert type(loaded) is type(machine)
    assert values_equal(loaded.as_dict(), machine.as_dict())
