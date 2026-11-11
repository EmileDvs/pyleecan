import ast
from pathlib import Path

import pytest

from pyleecan.Generator.ClassGenerator.New import generate_function_new_classes
from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
    _rewrite_source,
    generate_functions,
)
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    _apply_import_style,
    _redirect_experimental_function_imports,
)


def test_rewrite_imports_and_report_unresolved(tmp_path):
    class_dir = tmp_path / "Classes_new"
    class_dir.mkdir()
    for module in ("arc_1", "norm_ref", "segment"):
        (class_dir / (module + ".py")).touch()
    source = (
        "# from ...Classes.Arc1 import Arc1\n"
        "message = 'pyleecan.Classes.Arc1'\n"
        "from ...Classes.Arc1 import Arc1 as Arc\n"
        "from pyleecan.Classes.Norm_ref import Norm_ref\n"
        "from ...Functions.Electrical.helper import helper\n"
        "from pyleecan.Functions.Winding.gen_phase_list import gen_name\n"
        "from ..Load.import_class import import_class\n"
        "from ...Classes.import_all import *\n"
        "def make():\n"
        "    Segment = import_class('pyleecan.Classes', 'Segment')\n"
        "    return Segment\n"
    )
    result, issues = _rewrite_source(
        source, Path("sample.py"), Path("Plot") / "sample.py", class_dir
    )
    assert "# from ...Classes.Arc1 import Arc1" in result
    assert "message = 'pyleecan.Classes.Arc1'" in result
    assert "from pyleecan.Classes_new.arc_1 import Arc1 as Arc" in result
    assert "from pyleecan.Classes_new.norm_ref import NormRef as Norm_ref" in result
    assert "from ...Functions_new.Electrical.helper import helper" in result
    assert (
        "from pyleecan.Functions_new.Winding.gen_phase_list import gen_name" in result
    )
    assert "from pyleecan.Classes_new.segment import Segment" in result
    assert "from ..Load.import_class import import_class" not in result
    assert issues == [(8, "legacy import: pyleecan.Classes.import_all")]
    ast.parse(result)


def test_copy_tree_keeps_resources_and_reports_deferred_loader(tmp_path):
    source = tmp_path / "Functions"
    output = tmp_path / "Functions_new"
    classes = tmp_path / "Classes_new"
    (source / "Electrical").mkdir(parents=True)
    classes.mkdir()
    (classes / "data_time.py").touch()
    (source / "__init__.py").write_text("", encoding="utf-8")
    (source / "Electrical" / "sample.py").write_text(
        "from ...Classes.DataTime import DataTime\n", encoding="utf-8"
    )
    (source / "load.py").write_text(
        "obj = import_class('pyleecan.Classes', 'DataTime')\n", encoding="utf-8"
    )
    (source / "Electrical" / "fixture.lua").write_bytes(b"fixture\x00")
    (source / "__pycache__").mkdir()
    (source / "__pycache__" / "cache.pyc").write_bytes(b"cache")
    output.mkdir()
    (output / "existing.py").write_text("keep", encoding="utf-8")
    issues = generate_functions(source, output, classes)
    assert issues == [(Path("load.py"), 1, "dynamic class loader requires review")]
    assert (output / "Electrical" / "sample.py").read_text(encoding="utf-8") == (
        "from pyleecan.Classes_new.data_time import DataTime\n"
    )
    assert (output / "Electrical" / "fixture.lua").read_bytes() == b"fixture\x00"
    assert not (output / "__pycache__").exists()
    assert (output / "existing.py").read_text() == "keep"
    assert (
        (source / "Electrical" / "sample.py")
        .read_text(encoding="utf-8")
        .startswith("from ...Classes.")
    )
    with pytest.raises(ValueError, match="separate"):
        generate_functions(source, source / "output", classes)


def test_generate_functions_uses_default_package_paths(tmp_path, monkeypatch):
    source = tmp_path / "Functions"
    classes = tmp_path / "Classes_new"
    source.mkdir()
    classes.mkdir()
    (source / "sample.py").write_text(
        "from pyleecan.Functions.load import load\n", encoding="utf-8"
    )
    monkeypatch.setattr(generate_function_new_classes, "MAIN_DIR", str(tmp_path))

    assert generate_functions() == []
    assert (tmp_path / "Functions_new" / "sample.py").read_text(
        encoding="utf-8"
    ) == "from pyleecan.Functions_new.load import load\n"


@pytest.mark.parametrize("style", ["absolute", "relative"])
def test_generated_classes_redirect_functions_but_defer_load_save(style):
    source = (
        "from pyleecan.Functions.Electrical.dqh_transformation import n2dqh\n"
        "from pyleecan.Functions.load import load_init_dict\n"
        "from pyleecan.Functions.Load.retrocompatibility import convert_init_dict\n"
        "from pyleecan.Functions.save import save\n"
    )
    result = _redirect_experimental_function_imports(source, "pyleecan")
    result = _apply_import_style(result, "pyleecan", style, "Classes_new")
    prefix = "pyleecan." if style == "absolute" else ".."
    assert (
        f"from {prefix}Functions_new.Electrical.dqh_transformation import n2dqh"
        in result
    )
    assert f"from {prefix}Functions.load import load_init_dict" in result
    assert (
        f"from {prefix}Functions.Load.retrocompatibility import convert_init_dict"
        in result
    )
    assert f"from {prefix}Functions.save import save" in result


def test_generated_classes_redirect_dynamic_function_imports():
    source = (
        "module = import_module('pyleecan.Functions.SciDataTool.conversions')\n"
        "other = __import__(f'pyleecan.Functions.Converter.MotorCAD.{name}')\n"
        "load = import_module('pyleecan.Functions.load')\n"
        "message = 'pyleecan.Functions.not_an_import'\n"
    )
    result = _redirect_experimental_function_imports(source, "pyleecan")
    assert "import_module('pyleecan.Functions_new.SciDataTool.conversions')" in result
    assert "__import__(f'pyleecan.Functions_new.Converter.MotorCAD.{name}')" in result
    assert "import_module('pyleecan.Functions.load')" in result
    assert "message = 'pyleecan.Functions.not_an_import'" in result


def test_copied_dqh_checker_accepts_experimental_data():
    from pyleecan.Classes_new.data_1d import Data1D
    from pyleecan.Classes_new.data_time import DataTime
    from pyleecan.Functions_new.Electrical.dqh_transformation import _check_data

    data = DataTime(axes=[Data1D(name="time"), Data1D(name="phase")])
    assert _check_data(data) is None
