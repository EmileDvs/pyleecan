"""Tests for the experimental generator's integration with class_generator."""

import ast
import importlib
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from dataclasses import fields
from pathlib import Path
from typing import get_type_hints

import pytest

from pyleecan.definitions import DOC_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator import class_generator, class_generator_new
from pyleecan.Generator.read_fct import read_all


@pytest.fixture
def generator_environment(monkeypatch):
    scripts = str(Path(sys.executable).parent)
    monkeypatch.setenv("PATH", scripts + os.pathsep + os.environ.get("PATH", ""))
    gen_dict = read_all(DOC_DIR)
    for name in ("Magnetics", "MagFEMM"):
        gen_dict[name] = deepcopy(gen_dict[name])
        gen_dict[name]["methods"] = []
    return gen_dict


def test_experimental_generator_is_shared(generator_environment, tmp_path):
    assert class_generator_new.generate_class_new is class_generator.generate_class_new
    assert class_generator_new._field_default is class_generator._field_default

    path = class_generator.generate_class(
        generator_environment, "Magnetics", str(tmp_path), is_new=True
    )
    first = Path(path).read_text(encoding="utf-8")
    assert Path(path).name == "magnetics.py"
    assert "from pyleecan.Classes_new._pyleecan_class import PyleecanClass" in first

    path_from_shim = class_generator_new.generate_class_new(
        generator_environment, "Magnetics", str(tmp_path)
    )
    assert Path(path_from_shim).read_text(encoding="utf-8") == first

    module = ast.parse(first)
    generated_class = next(
        node for node in module.body if isinstance(node, ast.ClassDef)
    )
    assert generated_class.name == "Magnetics"
    assert isinstance(generated_class.bases[0], ast.Name)
    assert generated_class.bases[0].id == "PyleecanClass"
    assert any(
        isinstance(node, ast.FunctionDef) and node.name == "_assert_parent_type"
        for node in generated_class.body
    )

    child_path = class_generator.generate_class(
        generator_environment, "MagFEMM", str(tmp_path), is_new=True
    )
    child_source = Path(child_path).read_text(encoding="utf-8")
    assert "from pyleecan.Classes_new.magnetics import Magnetics" in child_source
    child_module = ast.parse(child_source)
    child_class = next(
        node for node in child_module.body if isinstance(node, ast.ClassDef)
    )
    assert child_class.name == "MagFEMM"
    assert isinstance(child_class.bases[0], ast.Name)
    assert child_class.bases[0].id == "Magnetics"


@pytest.mark.parametrize(
    ("class_name", "module_name"),
    [
        ("Magnetics", "magnetics"),
        ("MagFEMM", "mag_femm"),
        ("CondType11", "cond_type_11"),
        ("Data1D", "data_1d"),
        ("LUT", "lut"),
        ("LUTdq", "lut_dq"),
        ("LUTslip", "lut_slip"),
        ("ElecLUTdq", "elec_lut_dq"),
        ("PostLUT", "post_lut"),
        ("LUTdqLUTslip", "lut_dq_lut_slip"),
        ("ScalarProductL2", "scalar_product_l2"),
        ("Import", "import_"),
        ("OP", "op"),
        ("OPdq", "op_dq"),
        ("OPdqf", "op_dqf"),
        ("OPslip", "op_slip"),
        ("OPMatrix", "op_matrix"),
    ],
)
def test_class_module_name(class_name, module_name):
    assert class_generator.class_module_name(class_name) == module_name


def test_experimental_module_names_are_unambiguous(generator_environment):
    class_generator.validate_class_module_names(generator_environment)
    with pytest.raises(ValueError, match="both map to module"):
        class_generator.validate_class_module_names({"MagFEMM": {}, "MagFemm": {}})


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_self_imports_and_recursive_types(
    generator_environment, tmp_path, monkeypatch, import_style
):
    class_dict = deepcopy(generator_environment["Output"])
    class_dict["mother"] = ""
    class_dict["methods"] = ["comp_axes"]
    recursive_prop = deepcopy(generator_environment["VarSimu"]["properties"][0])
    recursive_prop.update({"name": "child", "type": "Output", "value": ""})
    recursive_list = deepcopy(generator_environment["ImportData"]["properties"][0])
    recursive_list.update({"name": "children", "type": "[Output]", "value": None})
    class_dict["properties"] = [recursive_prop, recursive_list]
    owner = deepcopy(generator_environment["OutElec"])
    owner["mother"] = "Output"
    owner["properties"] = [recursive_prop]
    gen_dict = {"Output": class_dict, "OutElec": owner}

    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Output" / "Output"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from pyleecan.Classes.Output import Output\n"
        "def comp_axes(self, other: Output = None) -> Output:\n"
        "    return Output\n",
        encoding="utf-8",
    )
    path = class_generator.generate_class(
        gen_dict,
        "Output",
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    assert "from .output import Output" not in source
    assert "from pyleecan.Classes_new.output import Output" not in source

    name = "pyleecan.Classes_new.test_recursive_output"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    assert get_type_hints(module.Output)["child"] == module.Output | None
    assert get_type_hints(module.Output)["children"] == list[module.Output] | None
    assert get_type_hints(module.Output.comp_axes)["other"] is module.Output
    assert get_type_hints(module.Output.comp_axes)["return"] is module.Output
    instance = module.Output()
    assert instance.comp_axes() is module.Output
    instance._assert_parent_type(module.Output())
    with pytest.raises(TypeError):
        instance._assert_parent_type(object())


def test_self_module_imports_preserve_other_symbols():
    source = (
        "from pyleecan.Classes_new.example import Example, SHARED, external\n"
        "SHARED = 1\n"
        "class Example:\n"
        "    pass\n"
    )
    result = class_generator._remove_experimental_self_imports(
        source, "pyleecan", "Example", "example"
    )
    assert "from pyleecan.Classes_new.example import external" in result
    assert "SHARED = 1" in result


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_domain_module_names_in_generated_classes(
    generator_environment, tmp_path, import_style
):
    names = {
        "Data1D": "data_1d",
        "DataTime": "data_time",
        "ElecLUTdq": "elec_lut_dq",
        "LUTdq": "lut_dq",
        "LUTslip": "lut_slip",
        "ScalarProductL2": "scalar_product_l2",
    }
    gen_dict = dict(generator_environment)
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "SciDataTool" / "DataTime"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "SciDataTool" / "DataTime" / "time_to_freq.py",
        methods,
    )
    for name, module in names.items():
        gen_dict[name] = deepcopy(gen_dict[name])
        gen_dict[name]["methods"] = ["time_to_freq"] if name == "DataTime" else []
        path = class_generator.generate_class(
            gen_dict,
            name,
            str(output),
            is_new=True,
            import_style=import_style,
            class_import_graph={},
        )
        assert Path(path).name == module + ".py"

    data_time = (output / "data_time.py").read_text(encoding="utf-8")
    expected = (
        "from .data_1d import Data1D"
        if import_style == "relative"
        else "from pyleecan.Classes_new.data_1d import Data1D"
    )
    assert expected in data_time

    source = (
        "\n".join(f"from pyleecan.Classes.{name} import {name}" for name in names)
        + "\n"
    )
    transformed = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", gen_dict
    )
    transformed = class_generator._apply_import_style(
        transformed, "pyleecan", import_style, "Classes_new"
    )
    for name, module in names.items():
        prefix = "." if import_style == "relative" else "pyleecan.Classes_new."
        assert f"from {prefix}{module} import {name}" in transformed


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_operating_point_module_names(
    generator_environment, tmp_path, import_style
):
    names = ("OP", "OPdq", "OPdqf", "OPslip")
    gen_dict = {name: deepcopy(generator_environment[name]) for name in names}
    for class_dict in gen_dict.values():
        class_dict["methods"] = []
        class_dict["properties"] = []
    for name in names:
        path = class_generator.generate_class(
            gen_dict,
            name,
            str(tmp_path),
            is_new=True,
            import_style=import_style,
            class_import_graph={},
        )
        assert Path(path).name == class_generator.class_module_name(name) + ".py"
    source = (tmp_path / "op_dqf.py").read_text(encoding="utf-8")
    expected = (
        "from .op_dq import OPdq"
        if import_style == "relative"
        else "from pyleecan.Classes_new.op_dq import OPdq"
    )
    assert expected in source
    assert not list(tmp_path.glob("o_p*.py"))


@pytest.mark.parametrize(
    ("import_style", "machine_import", "femm_import", "package_import"),
    [
        (
            "relative",
            "from .machine import ARC_NPOINT_D as POINTS",
            "from .mag_femm import MagFEMM as Model",
            "from . import ParentMissingError as Missing, get_class_dict",
        ),
        (
            "absolute",
            "from pyleecan.Classes_new.machine import ARC_NPOINT_D as POINTS",
            "from pyleecan.Classes_new.mag_femm import MagFEMM as Model",
            "from pyleecan.Classes_new import ParentMissingError as Missing, get_class_dict",
        ),
    ],
)
def test_experimental_class_import_redirect(
    import_style, machine_import, femm_import, package_import
):
    source = (
        "from pyleecan.Classes.Machine import ARC_NPOINT_D as POINTS\n"
        "from pyleecan.Classes._check import check_var as validate\n"
        "from pyleecan.Classes._FEMMHandler import _FEMMHandler as Handler\n"
        "from pyleecan.Classes import ParentMissingError as Missing, get_class_dict, unknown\n"
        "from other.Classes.Machine import Machine\n"
        "def method():\n"
        "    from pyleecan.Classes.MagFEMM import MagFEMM as Model\n"
        "    return POINTS, Model\n"
    )
    transformed = class_generator._redirect_experimental_class_imports(
        source, "pyleecan", {"Machine": {}, "MagFEMM": {}}
    )
    transformed = class_generator._apply_import_style(
        transformed, "pyleecan", import_style, "Classes_new"
    )
    assert machine_import in transformed
    assert femm_import in transformed
    if import_style == "relative":
        assert "from ._check import check_var as validate" in transformed
        assert "from ._femm_handler import _FEMMHandler as Handler" in transformed
    else:
        assert "from pyleecan.Classes_new._check import check_var as validate" in transformed
        assert (
            "from pyleecan.Classes_new._femm_handler import _FEMMHandler as Handler"
            in transformed
        )
    assert package_import in transformed
    assert "from pyleecan.Classes import unknown" in transformed or (
        import_style == "relative" and "from ..Classes import unknown" in transformed
    )
    assert "from other.Classes.Machine import Machine" in transformed


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_femm_handler_import(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["MagFEMM"])
    class_dict["methods"] = ["comp_flux_airgap"]
    methods = tmp_path / "Methods" / "Simulation" / "MagFEMM"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "MagFEMM" / "comp_flux_airgap.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict["MagFEMM"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "MagFEMM",
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from ._femm_handler import _FEMMHandler"
        if import_style == "relative"
        else "from pyleecan.Classes_new._femm_handler import _FEMMHandler"
    )
    assert expected in source
    assert "_FEMMHandler()" in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_method_uses_package_exception(
    generator_environment, tmp_path, import_style
):
    class_dict = deepcopy(generator_environment["MagElmer"])
    class_dict["methods"] = ["solve_FEA"]
    methods = tmp_path / "Methods" / "Simulation" / "MagElmer"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "MagElmer" / "solve_FEA.py",
        methods,
    )
    gen_dict = dict(generator_environment)
    gen_dict["MagElmer"] = class_dict
    output = tmp_path / "Classes_new"
    output.mkdir()
    path = class_generator.generate_class(
        gen_dict,
        "MagElmer",
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from . import NotImplementedYetError"
        if import_style == "relative"
        else "from pyleecan.Classes_new import NotImplementedYetError"
    )
    assert expected in source
    assert "raise NotImplementedYetError(" in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_arc_constant_import(
    generator_environment, tmp_path, monkeypatch, import_style
):
    class_dict = deepcopy(generator_environment["Arc1"])
    class_dict["methods"] = ["discretize"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Geometry" / "Arc1"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Geometry" / "Arc1" / "discretize.py", methods
    )
    gen_dict = dict(generator_environment)
    gen_dict["Arc1"] = class_dict
    path = class_generator.generate_class(
        gen_dict,
        "Arc1",
        str(output),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from .machine import ARC_NPOINT_D"
        if import_style == "relative"
        else "from pyleecan.Classes_new.machine import ARC_NPOINT_D"
    )
    assert expected in source
    assert "Classes.Machine import ARC_NPOINT_D" not in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_property_types_import_new_modules(
    generator_environment, tmp_path, import_style
):
    gen_dict = dict(generator_environment)
    gen_dict["Machine"] = deepcopy(gen_dict["Machine"])
    gen_dict["Machine"]["methods"] = []
    path = class_generator.generate_class(
        gen_dict,
        "Machine",
        str(tmp_path),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    source = Path(path).read_text(encoding="utf-8")
    expected = (
        "from .frame import Frame"
        if import_style == "relative"
        else "from pyleecan.Classes_new.frame import Frame"
    )
    assert expected in source
    assert "Classes.Frame import Frame" not in source


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_legacy_arc_constant_import_unchanged(
    generator_environment, tmp_path, import_style
):
    gen_dict = dict(generator_environment)
    gen_dict["Arc1"] = deepcopy(gen_dict["Arc1"])
    gen_dict["Arc1"]["methods"] = ["discretize"]
    output = tmp_path / "Classes"
    output.mkdir()
    methods = tmp_path / "Methods" / "Geometry" / "Arc1"
    methods.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Geometry" / "Arc1" / "discretize.py", methods
    )
    class_generator.generate_class(
        gen_dict, "Arc1", str(output), import_style=import_style, class_import_graph={}
    )
    source = (output / "Arc1.py").read_text(encoding="utf-8")
    expected = (
        "from .Machine import ARC_NPOINT_D"
        if import_style == "relative"
        else "from pyleecan.Classes.Machine import ARC_NPOINT_D"
    )
    assert expected in source


@pytest.mark.parametrize(
    ("class_name", "module_constants", "class_constants"),
    [
        ("Machine", {"ARC_NPOINT_D": 99, "LINE_NPOINT_D": 1}, {}),
        (
            "Skew",
            {
                "TYPE_SKEW_LIST": [
                    "linear",
                    "vshape",
                    "zig-zag",
                    "user-defined",
                    "function",
                ]
            },
            {},
        ),
        ("Input", {"ROT_DIR_REF": -1, "CURRENT_DIR_REF": -1, "PHASE_DIR_REF": -1}, {}),
        (
            "SolverInputFile",
            {"WHITESPACE": " ", "INDENT": "  "},
            {"WHITESPACE": " ", "COMMENT": "! ", "MESH_FILE": "Mesh"},
        ),
    ],
)
@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_module_and_class_constants(
    generator_environment,
    tmp_path,
    monkeypatch,
    class_name,
    module_constants,
    class_constants,
    import_style,
):
    class_dict = deepcopy(generator_environment[class_name])
    class_dict["mother"] = ""
    class_dict["properties"] = []
    class_dict["methods"] = []
    class_dict["constants"] = [{"name": "INNER_TEST_CONSTANT", "value": "42"}]
    path = class_generator.generate_class(
        {class_name: class_dict},
        class_name,
        str(tmp_path),
        is_new=True,
        import_style=import_style,
        class_import_graph={},
    )
    module_name = (
        "pyleecan.Classes_new.test_constants_"
        + class_generator.class_module_name(class_name)
    )
    spec = importlib.util.spec_from_file_location(module_name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, module_name, module)
    spec.loader.exec_module(module)
    generated_class = getattr(module, class_name)
    imported_module = __import__(module_name, fromlist=list(module_constants))
    for name, value in module_constants.items():
        assert getattr(imported_module, name) == value
        if name not in class_constants:
            assert name not in generated_class.__dict__
    for name, value in class_constants.items():
        assert generated_class.__dict__[name] == value
    assert generated_class.INNER_TEST_CONSTANT == 42
    assert "INNER_TEST_CONSTANT" not in module.__dict__
    assert "INNER_TEST_CONSTANT" not in {
        field.name for field in fields(generated_class)
    }


def test_experimental_method_uses_exported_module_constant(
    generator_environment, tmp_path, monkeypatch
):
    class_dict = deepcopy(generator_environment["Machine"])
    class_dict["mother"] = ""
    class_dict["properties"] = []
    class_dict["methods"] = ["comp_axes"]
    output = tmp_path / "Classes_new"
    output.mkdir()
    methods = tmp_path / "Methods" / "Machine" / "Machine"
    methods.mkdir(parents=True)
    (methods / "comp_axes.py").write_text(
        "from pyleecan.Methods.Machine import ARC_NPOINT_D\n"
        "def comp_axes(self, count=ARC_NPOINT_D):\n"
        "    return count, ARC_NPOINT_D\n",
        encoding="utf-8",
    )
    path = class_generator.generate_class(
        {"Machine": class_dict},
        "Machine",
        str(output),
        is_new=True,
        class_import_graph={},
    )
    name = "pyleecan.Classes_new.test_constants_method"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, name, module)
    spec.loader.exec_module(module)
    assert module.Machine().comp_axes() == (99, 99)
    assert module.Machine().comp_axes(3) == (3, 99)


def test_ruff_uses_utf8_for_captured_text(tmp_path, monkeypatch):
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return subprocess.CompletedProcess(
            command, 0, stdout=kwargs.get("input", ""), stderr=""
        )

    monkeypatch.setattr(class_generator.subprocess, "run", run)
    source = 'from pyleecan.Classes.Magnetics import Magnetics\n\nclass Sample:\n    """Unicode \uff1a"""\n'
    path = str(tmp_path / "sample.py")
    organized = class_generator._organize_header_imports(source, "Sample", path)
    regrouped = class_generator._regroup_pyleecan_imports(organized, "Sample", path)
    assert "\uff1a" in class_generator._format_source_with_ruff(regrouped, path)
    assert len(calls) == 4
    assert all(kwargs["encoding"] == "utf-8" for _, kwargs in calls)


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_generated_inheritance_imports(
    generator_environment, tmp_path, monkeypatch, import_style
):
    import pyleecan.Classes_new
    from pyleecan.Classes_new._pyleecan_class import PyleecanClass

    output_dir = tmp_path / "Classes_new"
    output_dir.mkdir()
    methods_dir = tmp_path / "Methods" / "Simulation" / "Magnetics"
    methods_dir.mkdir(parents=True)
    shutil.copy2(
        Path(MAIN_DIR) / "Methods" / "Simulation" / "Magnetics" / "get_slice_model.py",
        methods_dir / "get_slice_model.py",
    )
    gen_dict = {
        name: deepcopy(generator_environment[name])
        for name in ("Magnetics", "MagFEMM", "SliceModel")
    }
    for class_dict in gen_dict.values():
        class_dict["methods"] = []
        class_dict["properties"] = []
    gen_dict["Magnetics"]["methods"] = ["get_slice_model"]
    monkeypatch.setattr(
        pyleecan.Classes_new,
        "__path__",
        [str(output_dir), *pyleecan.Classes_new.__path__],
    )
    for name in ("magnetics", "mag_femm", "slice_model"):
        monkeypatch.delitem(sys.modules, f"pyleecan.Classes_new.{name}", raising=False)
    for name in ("SliceModel", "Magnetics", "MagFEMM"):
        class_generator.generate_class(
            gen_dict,
            name,
            str(output_dir),
            is_new=True,
            import_style=import_style,
            class_import_graph={},
        )
    importlib.invalidate_caches()
    try:
        parent = importlib.import_module("pyleecan.Classes_new.magnetics")
        child = importlib.import_module("pyleecan.Classes_new.mag_femm")
        assert issubclass(child.MagFEMM, parent.Magnetics)
        assert issubclass(parent.Magnetics, PyleecanClass)
        assert parent.SliceModel.__module__ == "pyleecan.Classes_new.slice_model"
        assert hasattr(parent.Magnetics, "get_slice_model")
        instance = child.MagFEMM()
        assert instance.parent is None
    finally:
        sys.modules.pop("pyleecan.Classes_new.mag_femm", None)
        sys.modules.pop("pyleecan.Classes_new.magnetics", None)
        sys.modules.pop("pyleecan.Classes_new.slice_model", None)


def test_experimental_custom_output_name(generator_environment, tmp_path, monkeypatch):
    def unexpected_graph_lookup(*args):
        raise AssertionError("A supplied import graph must not be recomputed")

    monkeypatch.setattr(
        class_generator, "get_class_import_graph", unexpected_graph_lookup
    )
    path = class_generator.generate_class(
        generator_environment,
        "Magnetics",
        str(tmp_path),
        is_new=True,
        output_name="custom",
        class_import_graph={},
    )
    assert Path(path).name == "custom.py"
    module = ast.parse(Path(path).read_text(encoding="utf-8"))
    assert any(
        isinstance(node, ast.ClassDef) and node.name == "Magnetics"
        for node in module.body
    )
    with pytest.raises(ValueError, match="output_name"):
        class_generator.generate_class(
            generator_environment, "Magnetics", str(tmp_path), output_name="custom"
        )


def test_original_generation_remains_available(generator_environment, tmp_path):
    class_generator.generate_class(generator_environment, "Magnetics", str(tmp_path))

    source = (tmp_path / "Magnetics.py").read_text(encoding="utf-8")
    module = ast.parse(source)
    generated_class = next(
        node
        for node in module.body
        if isinstance(node, ast.ClassDef) and node.name == "Magnetics"
    )
    assert isinstance(generated_class.bases[0], ast.Name)
    assert generated_class.bases[0].id == "FrozenClass"
