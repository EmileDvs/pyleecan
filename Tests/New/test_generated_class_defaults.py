"""Regression coverage for experimental class-valued defaults."""

import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New import class_generator
from pyleecan.Generator.ClassGenerator.New.run_generate_classes import (
    _write_parent_types,
)
from pyleecan.Generator.read_fct import read_all


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_defaults_and_sentinel_in_isolated_package(
    tmp_path, import_style, monkeypatch
):
    root = Path(MAIN_DIR)
    for folder in ("Classes", "Classes_new", "Methods"):
        shutil.copytree(
            root / folder,
            tmp_path / folder,
            ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
        )
    generation = read_all(DOC_DIR)
    _write_parent_types(str(tmp_path / "Classes_new"), generation)
    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    for name in (
        "Output",
        "Simulation",
        "MachineSIPMSM",
        "Material",
        "MatMagnetics",
        "Winding",
        "MeshSolution",
    ):
        class_generator.generate_class(
            generation,
            name,
            str(tmp_path / "Classes_new"),
            is_new=True,
            import_style=import_style,
            shared_error_definitions={},
        )

    script = f"""
import pyleecan
pyleecan.__path__.insert(0, {str(tmp_path)!r})
from pyleecan.Classes_new.output import Output
from pyleecan.Classes_new.out_geo import OutGeo
from pyleecan.Classes_new.simulation import Simulation
from pyleecan.Classes_new.machine_sipmsm import MachineSIPMSM
from pyleecan.Classes_new.material import Material
from pyleecan.Classes_new.winding import Winding
from pyleecan.Classes_new.mesh import Mesh
from pyleecan.Classes_new.mesh_solution import MeshSolution
from pyleecan.Classes_new.xoutput import XOutput

fields = {{
    "simu": "Simulation", "geo": "OutGeo", "elec": "OutElec",
    "mag": "OutMag", "struct": "OutStruct", "post": "OutPost",
    "force": "OutForce", "loss": "OutLoss",
}}
first, second = Output(), Output()
for name, expected in fields.items():
    child = getattr(first, name)
    assert type(child).__name__ == expected, name
    assert child is not getattr(second, name), name
    assert child.parent is first, name

geo = OutGeo()
supplied = Output(simu=None, geo=geo, elec=None, mag=None, struct=None,
                  post=None, force=None, loss=None)
assert supplied.geo is geo and geo.parent is supplied
assert supplied.simu is None and supplied.elec is None
assert Output(simu=None, geo=-1).geo.parent is not None
supplied.geo = -1
assert isinstance(supplied.geo, OutGeo) and supplied.geo.parent is supplied
supplied.geo = None
assert supplied.geo is None

loaded = Output.from_dict({{"simu": None, "geo": -1, "elec": None}})
assert isinstance(loaded.geo, OutGeo) and loaded.geo.parent is loaded
assert loaded.simu is None and loaded.elec is None
assert Output.from_dict({{"simu": None, "geo": None}}).geo is None

derived = XOutput(simu=None)
assert isinstance(derived.geo, OutGeo) and derived.geo.parent is derived
assert derived.copy().geo.parent is not derived
assert type(MachineSIPMSM().rotor).__name__ == "LamSlotM"
assert type(Material().elec).__name__ == "MatElectrical"
material = Material()
assert type(material.mag.BH_curve).__name__ == "ImportMatrix"
assert material.mag.BH_curve.parent is material.mag
assert type(Winding().conductor).__name__ == "Conductor"
mesh_solution = MeshSolution()
assert isinstance(mesh_solution.mesh, Mesh)
assert mesh_solution.mesh.parent is mesh_solution
simulation = Simulation(machine=None, input=None, var_simu=-1)
assert type(simulation.var_simu).__name__ == "VarSimu"
simulation.var_simu = -1
assert type(simulation.var_simu).__name__ == "VarSimu"
loaded_simulation = Simulation.from_dict({{"machine": None, "input": None, "var_simu": -1}})
assert type(loaded_simulation.var_simu).__name__ == "VarSimu"
assert loaded_simulation.var_simu.parent is loaded_simulation
simulation.index = -1
assert simulation.index == -1
"""
    result = subprocess.run(
        [sys.executable, "-c", script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


def test_object_default_metadata_and_docs():
    generation = read_all(DOC_DIR)
    output = deepcopy(generation["Output"])
    geo = next(prop for prop in output["properties"] if prop["name"] == "geo")
    default = class_generator._field_default(geo, gen_dict=generation)
    assert "default_factory=lambda: import_class('OutGeo')()" in default
    assert "'default_class': 'OutGeo'" in default
    assert "Default: OutGeo()" in class_generator._class_docstring(output, generation)

    optional = next(
        prop
        for prop in generation["Simulation"]["properties"]
        if prop["name"] == "var_simu"
    )
    default = class_generator._field_default(optional, gen_dict=generation)
    assert "default=None" in default
    assert "'default_class': 'VarSimu'" in default


def test_parent_mapping_includes_owners_of_child_types():
    generation = read_all(DOC_DIR)
    mapping = class_generator.parent_type_mapping(generation)
    assert ("mat_magnetics", "MatMagnetics") in mapping[("import_", "Import")]


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_factory_reuses_static_mesh_import(
    tmp_path, monkeypatch, import_style
):
    generation = read_all(DOC_DIR)
    class_dict = deepcopy(generation["MeshSolution"])
    class_dict["methods"] = []
    generation["MeshSolution"] = class_dict
    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    path = class_generator.generate_class(
        generation,
        "MeshSolution",
        str(tmp_path),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
        shared_error_definitions={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "default_factory=lambda: Mesh()" in source
    assert 'import_class("Mesh")' not in source
    expected_import = (
        "from .mesh import Mesh"
        if import_style == "relative"
        else "from pyleecan.Classes_new.mesh import Mesh"
    )
    assert expected_import in source
    assert "import_class" not in source


@pytest.mark.parametrize(
    ("extra", "expected"),
    [
        ("", "Alias()"),
        ("Alias = other\n", "import_class('Mesh')()"),
        ("from another import Alias\n", "import_class('Mesh')()"),
        ("if flag:\n    Alias = other\n", "import_class('Mesh')()"),
        ("from another import *\n", "import_class('Mesh')()"),
    ],
)
def test_static_factory_respects_module_bindings(extra, expected):
    source = (
        "from pyleecan.Classes_new.mesh import Mesh as Alias\n"
        + extra
        + "class Example:\n"
        "    mesh: object = field(default_factory=lambda: import_class('Mesh')())\n"
    )
    result = class_generator._use_static_default_factories(
        source, "pyleecan", {"Mesh": {}}, "Example"
    )
    assert f"default_factory=lambda: {expected}" in result


def test_factory_without_static_import_stays_dynamic():
    source = (
        "class Example:\n"
        "    mesh: object = field(default_factory=lambda: import_class('Mesh')())\n"
    )
    assert (
        class_generator._use_static_default_factories(
            source, "pyleecan", {"Mesh": {}}, "Example"
        )
        == source
    )


def test_static_factory_handles_renamed_classes():
    source = (
        "from pyleecan.Classes_new.norm_ref import NormRef\n"
        "class Example:\n"
        "    norm: object = field(default_factory=lambda: import_class('Norm_ref')())\n"
    )
    result = class_generator._use_static_default_factories(
        source, "pyleecan", {"Norm_ref": {}}, "Example"
    )
    assert "default_factory=lambda: NormRef()" in result
