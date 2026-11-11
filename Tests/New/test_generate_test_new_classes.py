import ast
from pathlib import Path

from pyleecan.Generator.ClassGenerator.New import generate_test_new_classes
from pyleecan.Generator.ClassGenerator.New.generate_test_new_classes import (
    TEST_FOLDERS,
    _rewrite_source,
    generate_tests,
)


def test_rewrite_imports_preserves_bindings_and_other_text(tmp_path):
    class_dir = tmp_path / "Classes_new"
    class_dir.mkdir()
    for name in ("norm_ref", "arc_1", "_check"):
        (class_dir / (name + ".py")).touch()
    source = (
        "# from pyleecan.Classes.Arc1 import Arc1\n"
        "message = 'pyleecan.Classes.Arc1'\n"
        "from pyleecan.Classes.Norm_ref import Norm_ref\n"
        "from pyleecan.Classes.Arc1 import Arc1 as Arc\n"
        "from pyleecan.Classes._check import CheckTypeError\n"
        "from pyleecan.Classes.import_all import *\n"
        "from Tests import save_plot_path as save_path, TEST_DATA_DIR\n"
        "from Tests.Plot.LamWind import wind_mat\n"
    )
    result, issues = _rewrite_source(source, Path("sample.py"), class_dir)
    assert "# from pyleecan.Classes.Arc1 import Arc1" in result
    assert "message = 'pyleecan.Classes.Arc1'" in result
    assert "from pyleecan.Classes_new.norm_ref import NormRef as Norm_ref" in result
    assert "from pyleecan.Classes_new.arc_1 import Arc1 as Arc" in result
    assert "from pyleecan.Classes_new._check import CheckTypeError" in result
    assert "from pyleecan.Classes.import_all import *" in result
    assert "from Tests import TEST_DATA_DIR" in result
    assert "from Tests.New._test_paths import save_plot_path as save_path" in result
    assert "from Tests.New.Plot.LamWind import wind_mat" in result
    assert issues == [(6, "pyleecan.Classes.import_all")]
    ast.parse(result)


def test_generation_copies_trees_and_preserves_data_and_results(tmp_path):
    tests_dir = tmp_path / "Tests"
    class_dir = tmp_path / "Classes_new"
    class_dir.mkdir()
    (class_dir / "arc_1.py").touch()
    for folder in TEST_FOLDERS:
        (tests_dir / folder).mkdir(parents=True)
    (tests_dir / "Data").mkdir()
    (tests_dir / "Data" / "fixture.json").write_text("data", encoding="utf-8")
    source = tests_dir / "Methods" / "sample.py"
    source.write_text(
        "from pyleecan.Classes.Arc1 import Arc1\n"
        "from pyleecan.Functions.load import load\n",
        encoding="utf-8",
    )
    binary = tests_dir / "Methods" / "reference.jpg"
    binary.write_bytes(b"\x00\xff")
    result = tests_dir / "New" / "Results" / "keep.txt"
    result.parent.mkdir(parents=True)
    result.write_text("result", encoding="utf-8")

    assert generate_tests(tests_dir, class_dir) == []
    copied = tests_dir / "New" / "Methods" / "sample.py"
    assert (
        copied.read_text(encoding="utf-8")
        == "from pyleecan.Classes_new.arc_1 import Arc1\n"
        "from pyleecan.Functions_new.load import load\n"
    )
    assert (copied.parent / "reference.jpg").read_bytes() == b"\x00\xff"
    assert (
        source.read_text(encoding="utf-8")
        == "from pyleecan.Classes.Arc1 import Arc1\n"
        "from pyleecan.Functions.load import load\n"
    )
    assert (tests_dir / "Data" / "fixture.json").read_text(encoding="utf-8") == "data"
    assert result.read_text(encoding="utf-8") == "result"
    copied.write_text("edited", encoding="utf-8")
    generate_tests(tests_dir, class_dir)
    assert (
        copied.read_text(encoding="utf-8")
        == "from pyleecan.Classes_new.arc_1 import Arc1\n"
        "from pyleecan.Functions_new.load import load\n"
    )
    assert result.read_text(encoding="utf-8") == "result"


def test_rewrite_vendored_class_packages(tmp_path):
    for package in ("_smoot", "_swat_em"):
        folder = tmp_path / package
        folder.mkdir()
        (folder / "__init__.py").touch()
        (folder / "helper.py").touch()
    source = (
        "from pyleecan.Classes._smoot import MOO as Optimizer\n"
        "from pyleecan.Classes._swat_em.helper import item\n"
    )
    result, issues = _rewrite_source(source, Path("sample.py"), tmp_path)
    assert result == source.replace("pyleecan.Classes.", "pyleecan.Classes_new.")
    assert issues == []
    (tmp_path / "_swat_em" / "helper.py").unlink()
    result, issues = _rewrite_source(source, Path("sample.py"), tmp_path)
    assert "from pyleecan.Classes._swat_em.helper import item" in result
    assert issues == [(2, "pyleecan.Classes._swat_em.helper")]


def test_rewrite_shared_error_imports(tmp_path):
    source = "from pyleecan.Functions.load import load, LoadWrongTypeError as BadType\n"
    result, issues = _rewrite_source(source, Path("sample.py"), tmp_path)
    assert "from pyleecan.Functions_new.load import load" in result
    assert "from pyleecan.Classes_new._error import LoadWrongTypeError as BadType" in result
    assert issues == []
    ast.parse(result)


def test_rewrite_function_imports_preserves_format_and_bindings(tmp_path):
    source = (
        "# from pyleecan.Functions.load import load\n"
        "text = 'pyleecan.Functions.load'\n"
        "from pyleecan.Functions.load import (\n"
        "    load as read,  # comment\n"
        ")\n"
        "from pyleecan.Functions import load\n"
        "import pyleecan.Functions.Winding.gen_phase_list as phase\n"
        "import pyleecan.Functions.load\n"
        "from pyleecan.Functions_extra import value\n"
        "from pyleecan import Functions, definitions\n"
        "from pyleecan import Functions as funcs\n"
    )
    result, issues = _rewrite_source(source, Path("sample.py"), tmp_path)
    assert result == source.replace(
        "from pyleecan.Functions.load import (\n",
        "from pyleecan.Functions_new.load import (\n",
    ).replace(
        "from pyleecan.Functions import load",
        "from pyleecan.Functions_new import load",
    ).replace(
        "import pyleecan.Functions.Winding.gen_phase_list as phase",
        "import pyleecan.Functions_new.Winding.gen_phase_list as phase",
    ).replace(
        "from pyleecan import Functions, definitions",
        "from pyleecan import Functions_new as Functions, definitions",
    ).replace(
        "from pyleecan import Functions as funcs",
        "from pyleecan import Functions_new as funcs",
    )
    assert issues == [(8, "pyleecan.Functions.load")]
    ast.parse(result)


def test_generation_uses_default_repository_paths(tmp_path, monkeypatch):
    tests_dir = tmp_path / "Tests"
    class_dir = tmp_path / "src" / "pyleecan" / "Classes_new"
    class_dir.mkdir(parents=True)
    for folder in TEST_FOLDERS:
        (tests_dir / folder).mkdir(parents=True)
    (tests_dir / "Methods" / "sample.py").write_text(
        "from pyleecan.Functions.load import load\n", encoding="utf-8"
    )
    monkeypatch.setattr(generate_test_new_classes, "TEST_DIR", str(tests_dir))

    assert generate_tests() == []
    assert (tests_dir / "New" / "Methods" / "sample.py").read_text(
        encoding="utf-8"
    ) == "from pyleecan.Functions_new.load import load\n"
