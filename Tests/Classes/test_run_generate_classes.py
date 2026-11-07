"""Tests for legacy and experimental class generation orchestration."""

import importlib
import os
import subprocess
import sys
from copy import deepcopy
from pathlib import Path
from types import SimpleNamespace

import pytest

from pyleecan.Generator.ClassGenerator.class_generator import class_module_name

runner = importlib.import_module("pyleecan.Generator.run_generate_classes")


@pytest.fixture
def generation_root(tmp_path):
    for folder in ("Classes", "Classes_new", "Functions"):
        (tmp_path / folder).mkdir()
    (tmp_path / "Classes_new" / "_pyleecan_class.py").write_text("", encoding="utf-8")
    return tmp_path


@pytest.fixture
def generator_calls(monkeypatch):
    calls = []
    monkeypatch.setattr(runner, "get_class_import_graph", lambda *args: {"A": ()})

    def generate(gen_dict, name, output_dir, **kwargs):
        calls.append((name, Path(output_dir), kwargs))
        module = class_module_name(name) if kwargs["is_new"] else name
        (Path(output_dir) / (module + ".py")).write_text(
            "class " + name + ":\n    pass\n", encoding="utf-8"
        )

    monkeypatch.setattr(runner, "generate_class", generate)
    return calls


def test_experimental_generation_leaves_legacy_files_untouched(
    generation_root, generator_calls
):
    legacy = generation_root / "Classes" / "A.py"
    legacy.write_text("legacy", encoding="utf-8")
    bookkeeping = generation_root / "Functions" / "load_switch.py"
    bookkeeping.write_text("legacy switch", encoding="utf-8")
    preserved = generation_root / "Classes_new" / "Other_new.py"
    preserved.write_text("other", encoding="utf-8")
    runner.generate_code(
        str(generation_root), {"A": {}}, class_list=["A.csv"], is_new=True
    )
    assert legacy.read_text(encoding="utf-8") == "legacy"
    assert bookkeeping.read_text(encoding="utf-8") == "legacy switch"
    assert preserved.read_text(encoding="utf-8") == "other"
    assert (generation_root / "Classes_new" / "a.py").is_file()
    assert generator_calls[0][2]["is_new"] is True
    assert generator_calls[0][2]["class_import_graph"] == {"A": ()}


def test_legacy_generation_and_ruff_formatting(
    generation_root, generator_calls, monkeypatch
):
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: {"A": {}})
    monkeypatch.setattr(runner, "write_file", lambda value: None)
    calls = []

    def run(command, **kwargs):
        calls.append((command, kwargs))
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(runner.subprocess, "run", run)
    runner.run_generate_classes(
        doc_dir="unused",
        int_dir="unused",
        main_dir=str(generation_root),
        class_list=["A.csv"],
    )
    assert generator_calls[0][2]["is_new"] is False
    assert generator_calls[0][2]["import_style"] == "absolute"
    assert (generation_root / "Classes" / "A.py").is_file()
    assert (generation_root / "Classes" / "Class_Dict.json").is_file()
    assert calls == [
        (
            ["ruff", "format", str(generation_root / "Classes" / "A.py")],
            {"check": True},
        )
    ]


def test_experimental_runner_skips_csv_and_legacy_formatter(
    generation_root, generator_calls, monkeypatch
):
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: {"A": {}})
    monkeypatch.setattr(
        runner, "write_file", lambda value: pytest.fail("CSV must not be rewritten")
    )
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Dataclasses already use Ruff"),
    )
    runner.run_generate_classes(
        doc_dir="unused", int_dir="unused", main_dir=str(generation_root), is_new=True
    )
    assert generator_calls[0][2]["is_new"] is True
    assert (generation_root / "Classes_new" / "_pyleecan_class.py").is_file()
    assert (generation_root / "Classes_new" / "a.py").is_file()
    assert not (generation_root / "Classes" / "Class_Dict.json").exists()


def test_legacy_runner_can_skip_ruff(generation_root, generator_calls, monkeypatch):
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: {"A": {}})
    monkeypatch.setattr(runner, "write_file", lambda value: None)
    monkeypatch.setattr(
        runner.subprocess,
        "run",
        lambda *args, **kwargs: pytest.fail("Ruff should be disabled"),
    )
    runner.run_generate_classes(
        doc_dir="unused",
        int_dir="unused",
        main_dir=str(generation_root),
        class_list=["A.csv"],
        is_ruff=False,
    )
    assert generator_calls[0][2]["is_new"] is False


@pytest.mark.parametrize("is_new", [False, True])
@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_runner_generates_requested_import_style(
    generation_root, monkeypatch, is_new, import_style
):
    gen_dict = runner.read_all(runner.DOC_DIR)
    gen_dict["MagFEMM"] = deepcopy(gen_dict["MagFEMM"])
    gen_dict["MagFEMM"]["methods"] = []
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: gen_dict)
    monkeypatch.setattr(runner, "write_file", lambda value: None)
    monkeypatch.setattr(
        runner, "get_class_import_graph", lambda *args: dict.fromkeys(gen_dict, ())
    )
    monkeypatch.setenv(
        "PATH",
        str(Path(sys.executable).parent) + os.pathsep + os.environ.get("PATH", ""),
    )
    runner.run_generate_classes(
        main_dir=str(generation_root),
        class_list=["MagFEMM.csv"],
        is_new=is_new,
        is_ruff=False,
        import_style=import_style,
    )
    folder = "Classes_new" if is_new else "Classes"
    module = "mag_femm.py" if is_new else "MagFEMM.py"
    source = (generation_root / folder / module).read_text(encoding="utf-8")
    if is_new:
        expected = (
            "from pyleecan.Classes_new.magnetics import Magnetics"
            if import_style == "absolute"
            else "from .magnetics import Magnetics"
        )
    else:
        expected = (
            "from pyleecan.Classes.Magnetics import Magnetics"
            if import_style == "absolute"
            else "from .Magnetics import Magnetics"
        )
    assert expected in source


@pytest.mark.parametrize("entrypoint", ["generate_code", "run_generate_classes"])
def test_invalid_import_style_does_not_modify_files(
    generation_root, monkeypatch, entrypoint
):
    legacy = generation_root / "Classes" / "A.py"
    legacy.write_text("unchanged", encoding="utf-8")
    monkeypatch.setattr(
        runner,
        "read_all",
        lambda *args, **kwargs: pytest.fail("Must fail before reading"),
    )
    with pytest.raises(ValueError, match="import_style"):
        if entrypoint == "generate_code":
            runner.generate_code(
                str(generation_root), {"A": {}}, import_style="invalid"
            )
        else:
            runner.run_generate_classes(
                main_dir=str(generation_root), import_style="invalid"
            )
    assert legacy.read_text(encoding="utf-8") == "unchanged"


def test_experimental_generation_requires_shared_base(generation_root):
    (generation_root / "Classes_new" / "_pyleecan_class.py").unlink()
    with pytest.raises(FileNotFoundError, match="_pyleecan_class.py"):
        runner.generate_code(str(generation_root), {"A": {}}, is_new=True)


def test_experimental_collision_is_rejected_before_writing(
    generation_root, monkeypatch
):
    monkeypatch.setattr(
        runner,
        "get_class_import_graph",
        lambda *args: pytest.fail("Names must be checked before generation"),
    )
    with pytest.raises(ValueError, match="both map to module"):
        runner.generate_code(
            str(generation_root), {"MagFEMM": {}, "MagFemm": {}}, is_new=True
        )
    assert sorted(
        path.name for path in (generation_root / "Classes_new").iterdir()
    ) == ["_pyleecan_class.py"]


def test_legacy_formatter_failure_is_reported(
    generation_root, generator_calls, monkeypatch
):
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: {"A": {}})
    monkeypatch.setattr(runner, "write_file", lambda value: None)

    def fail(command, **kwargs):
        raise subprocess.CalledProcessError(1, command)

    monkeypatch.setattr(runner.subprocess, "run", fail)
    with pytest.raises(subprocess.CalledProcessError):
        runner.run_generate_classes(
            doc_dir="unused",
            int_dir="unused",
            main_dir=str(generation_root),
            class_list=["A.csv"],
        )
