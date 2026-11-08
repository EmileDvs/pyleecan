import ast
from pathlib import Path

from Tests.generate_test_new_classes import (
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
    source.write_text("from pyleecan.Classes.Arc1 import Arc1\n", encoding="utf-8")
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
    )
    assert (copied.parent / "reference.jpg").read_bytes() == b"\x00\xff"
    assert (
        source.read_text(encoding="utf-8") == "from pyleecan.Classes.Arc1 import Arc1\n"
    )
    assert (tests_dir / "Data" / "fixture.json").read_text(encoding="utf-8") == "data"
    assert result.read_text(encoding="utf-8") == "result"
    copied.write_text("edited", encoding="utf-8")
    generate_tests(tests_dir, class_dir)
    assert (
        copied.read_text(encoding="utf-8")
        == "from pyleecan.Classes_new.arc_1 import Arc1\n"
    )
    assert result.read_text(encoding="utf-8") == "result"
