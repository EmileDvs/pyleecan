"""Tests for the experimental generator's integration with class_generator."""

import ast
import importlib
import os
import shutil
import subprocess
import sys
from copy import deepcopy
from pathlib import Path

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
        ("Data1D", "data_1_d"),
        ("Import", "import_"),
    ],
)
def test_class_module_name(class_name, module_name):
    assert class_generator.class_module_name(class_name) == module_name


def test_experimental_module_names_are_unambiguous(generator_environment):
    class_generator.validate_class_module_names(generator_environment)
    with pytest.raises(ValueError, match="both map to module"):
        class_generator.validate_class_module_names({"MagFEMM": {}, "MagFemm": {}})


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
    generator_environment["Magnetics"]["methods"] = ["get_slice_model"]
    monkeypatch.setattr(
        pyleecan.Classes_new,
        "__path__",
        [str(output_dir), *pyleecan.Classes_new.__path__],
    )
    for name in ("magnetics", "mag_femm"):
        monkeypatch.delitem(sys.modules, f"pyleecan.Classes_new.{name}", raising=False)
    for name in ("Magnetics", "MagFEMM"):
        class_generator.generate_class(
            generator_environment,
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
        assert parent.SliceModel.__module__ == "pyleecan.Classes.SliceModel"
        assert hasattr(parent.Magnetics, "get_slice_model")
        instance = child.MagFEMM()
        assert instance.parent is None
    finally:
        sys.modules.pop("pyleecan.Classes_new.mag_femm", None)
        sys.modules.pop("pyleecan.Classes_new.magnetics", None)


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
