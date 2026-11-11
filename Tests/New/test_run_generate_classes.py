"""Tests for experimental class generation orchestration."""

import importlib
import importlib.util
import json
import os
import sys
from copy import deepcopy
from pathlib import Path

import pytest

from pyleecan.Generator.ClassGenerator.New.class_generator import class_module_name

runner = importlib.import_module("pyleecan.Generator.ClassGenerator.New.run_generate_classes")


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
        module = class_module_name(name)
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
        str(generation_root),
        {"A": {"mother": "", "properties": []}},
        class_list=["A.csv"],
        )
    assert legacy.read_text(encoding="utf-8") == "legacy"
    assert bookkeeping.read_text(encoding="utf-8") == "legacy switch"
    assert preserved.read_text(encoding="utf-8") == "other"
    assert (generation_root / "Classes_new" / "a.py").is_file()
    assert generator_calls[0][2]["class_import_graph"] == {"A": ()}


@pytest.mark.parametrize("entrypoint", ["generate_code", "run_generate_classes"])
def test_legacy_mode_is_rejected_before_writing(generation_root, entrypoint):
    legacy = generation_root / "Classes" / "A.py"
    legacy.write_text("unchanged", encoding="utf-8")
    with pytest.raises(TypeError, match="is_new"):
        if entrypoint == "generate_code":
            runner.generate_code(str(generation_root), {"A": {}}, is_new=False)
        else:
            runner.run_generate_classes(main_dir=str(generation_root), is_new=False)
    assert legacy.read_text(encoding="utf-8") == "unchanged"
    assert sorted(path.name for path in (generation_root / "Classes_new").iterdir()) == [
        "_pyleecan_class.py"
    ]


def test_partial_generation_rejects_old_experimental_loader(
    generation_root, generator_calls
):
    loader = generation_root / "Classes_new" / "_import.py"
    loader.write_text("def import_class(mod_name, class_name): pass\n", encoding="utf-8")
    with pytest.raises(ValueError, match="full generation"):
        runner.generate_code(
            str(generation_root),
            {"A": {"mother": "", "properties": []}},
            class_list=["A.csv"],
        )
    assert loader.read_text(encoding="utf-8").startswith("def import_class(mod_name")
    assert not generator_calls


def test_shared_error_name_conflict_does_not_remove_existing_classes(
    generation_root, generator_calls, monkeypatch
):
    class_dir = generation_root / "Classes_new"
    existing = class_dir / "existing.py"
    existing.write_text("unchanged", encoding="utf-8")
    first = ("example.Methods.First", "SameError")
    second = ("example.Methods.Second", "SameError")
    monkeypatch.setattr(
        runner,
        "_shared_error_definitions",
        lambda *args: {first: None, second: None},
    )
    with pytest.raises(ValueError, match="SameError"):
        runner.generate_code(
            str(generation_root), {"A": {"mother": "", "properties": []}}
        )
    assert existing.read_text(encoding="utf-8") == "unchanged"
    assert not generator_calls


@pytest.mark.parametrize("class_list", [None, ["A.csv"]])
@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_package_bookkeeping(
    generation_root, generator_calls, class_list, monkeypatch, import_style
):
    gen_dict = {
        "A": {"name": "A", "mother": "", "properties": [], "daughters": ["B"]},
        "B": {"name": "B", "mother": "", "properties": [{"type": "A"}]},
    }
    runner.generate_code(
        str(generation_root), gen_dict, class_list=class_list, import_style=import_style,
    )
    class_dir = generation_root / "Classes_new"
    import_source = (class_dir / "_import.py").read_text(encoding="utf-8")
    assert "_CLASS_MODULES = {'A': 'a', 'B': 'b'}" in import_source
    assert "def import_class(" in import_source
    assert not (class_dir / "_import_all.py").exists()
    with (class_dir / "_class_dict.json").open(encoding="utf-8") as json_file:
        assert json.load(json_file) == gen_dict
    assert not (class_dir / "Class_Dict.json").exists()
    spec = importlib.util.spec_from_file_location(
        "generated_classes_new", class_dir / "__init__.py"
    )
    module = importlib.util.module_from_spec(spec)
    monkeypatch.setitem(sys.modules, spec.name, module)
    monkeypatch.delitem(sys.modules, spec.name + "._error", raising=False)
    spec.loader.exec_module(module)
    error_module = importlib.import_module(spec.name + "._error")
    assert not hasattr(module, "ParentMissingError")
    assert not hasattr(module, "NotImplementedYetError")
    assert module.get_class_dict() == gen_dict
    parent_spec = importlib.util.spec_from_file_location(
        "generated_parent_types", class_dir / "_parent_types.py"
    )
    parent_module = importlib.util.module_from_spec(parent_spec)
    parent_spec.loader.exec_module(parent_module)
    assert parent_module.PARENT_TYPES == {("a", "A"): (("b", "B"),)}
    original = (class_dir / "_parent_types.py").read_text(encoding="utf-8")
    runner._write_parent_types(class_dir, dict(reversed(list(gen_dict.items()))))
    assert (class_dir / "_parent_types.py").read_text(encoding="utf-8") == original
    assert issubclass(error_module.NotImplementedYetError, Exception)
    assert issubclass(error_module.ParentMissingError, Exception)
    with pytest.raises(error_module.ParentMissingError):
        raise error_module.ParentMissingError("missing parent")






@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_experimental_import_uses_generated_names_and_imports(
    generation_root, generator_calls, monkeypatch, import_style
):
    gen_dict = {
        "Norm_ref": {"name": "Norm_ref", "mother": "", "properties": []},
        "OPdq": {"name": "OPdq", "mother": "", "properties": []},
    }

    def generate(gen_dict, name, output_dir, **kwargs):
        symbol = "NormRef" if name == "Norm_ref" else name
        (Path(output_dir) / (class_module_name(name) + ".py")).write_text(
            "class " + symbol + ":\n    pass\n", encoding="utf-8"
        )

    monkeypatch.setattr(runner, "generate_class", generate)
    package = "generated_import_all_" + import_style
    generation_root.joinpath("__init__.py").write_text("", encoding="utf-8")
    monkeypatch.syspath_prepend(str(generation_root.parent))
    generation_root.rename(generation_root.parent / package)
    root = generation_root.parent / package
    runner.generate_code(
        str(root), gen_dict, soft_name=package, import_style=import_style
    )
    module = importlib.import_module(package + ".Classes_new._import")
    assert package + ".Classes_new.norm_ref" not in sys.modules
    assert package + ".Classes_new.op_dq" not in sys.modules
    assert module.NormRef.__name__ == "NormRef"
    assert module.OPdq.__name__ == "OPdq"
    assert not hasattr(module, "Norm_ref")
    assert module.import_class("Norm_ref") is module.NormRef
    assert module.import_class("OPdq") is module.OPdq
    error_module = importlib.import_module(package + ".Classes_new._error")
    with pytest.raises(error_module.InitUnKnowClassError, match="property example"):
        module.import_class("Missing", "example")


@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_generated_class_can_import_loader_without_loading_other_classes(
    generation_root, monkeypatch, import_style
):
    package = "generated_loader_" + import_style
    generation_root.joinpath("__init__.py").write_text("", encoding="utf-8")
    root = generation_root.parent / package
    generation_root.rename(root)
    class_dir = root / "Classes_new"
    monkeypatch.syspath_prepend(str(root.parent))
    gen_dict = {
        "A": {"mother": "", "properties": []},
        "B": {"mother": "", "properties": []},
        "Broken": {"mother": "", "properties": []},
    }
    runner._write_shared_errors(str(class_dir), {})
    runner._write_experimental_bookkeeping(class_dir, gen_dict, package, import_style)
    prefix = "." if import_style == "relative" else package + ".Classes_new."
    (class_dir / "a.py").write_text(
        f"from {prefix}_import import import_class\n"
        "class A:\n"
        "    def load(self): return import_class('B')\n",
        encoding="utf-8",
    )
    (class_dir / "b.py").write_text("class B: pass\n", encoding="utf-8")
    a = importlib.import_module(package + ".Classes_new.a")
    assert package + ".Classes_new.b" not in sys.modules
    assert package + ".Classes" not in sys.modules
    b = a.A().load()
    assert b is importlib.import_module(package + ".Classes_new.b").B
    assert package + ".Classes" not in sys.modules

    (class_dir / "broken.py").write_text(
        "import missing_generated_loader_dependency\n", encoding="utf-8"
    )
    loader = importlib.import_module(package + ".Classes_new._import")
    with pytest.raises(ModuleNotFoundError, match="missing_generated_loader_dependency"):
        loader.import_class("Broken")


def test_experimental_runner_skips_csv_and_legacy_formatter(
    generation_root, generator_calls, monkeypatch
):
    monkeypatch.setattr(
        runner,
        "read_all",
        lambda *args, **kwargs: {"A": {"mother": "", "properties": []}},
    )
    runner.run_generate_classes(
        doc_dir="unused", int_dir="unused", main_dir=str(generation_root)
    )
    assert (generation_root / "Classes_new" / "_pyleecan_class.py").is_file()
    assert (generation_root / "Classes_new" / "a.py").is_file()
    assert not (generation_root / "Classes" / "Class_Dict.json").exists()




@pytest.mark.parametrize("import_style", ["absolute", "relative"])
def test_runner_generates_requested_import_style(
    generation_root, monkeypatch, import_style
):
    gen_dict = runner.read_all(runner.DOC_DIR)
    gen_dict["MagFEMM"] = deepcopy(gen_dict["MagFEMM"])
    gen_dict["MagFEMM"]["methods"] = []
    monkeypatch.setattr(runner, "read_all", lambda *args, **kwargs: gen_dict)
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
        import_style=import_style,
    )
    source = (generation_root / "Classes_new" / "mag_femm.py").read_text(
        encoding="utf-8"
    )
    expected = (
        "from pyleecan.Classes_new.magnetics import Magnetics"
        if import_style == "absolute"
        else "from .magnetics import Magnetics"
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
        runner.generate_code(str(generation_root), {"A": {}}, )


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
            str(generation_root), {"MagFEMM": {}, "MagFemm": {}}, )
    assert sorted(
        path.name for path in (generation_root / "Classes_new").iterdir()
    ) == ["_pyleecan_class.py"]
