"""Step 12 freeze: the generators leave the hand-written code unchanged."""

from pathlib import Path

import pytest

from pyleecan.definitions import MAIN_DIR


def test_all_methods_new_packages_frozen():
    from pyleecan.Generator.ClassGenerator.New.generate_methods_new import (
        FROZEN_PACKAGES,
    )

    subpackages = {
        path.name
        for path in Path(MAIN_DIR, "Methods_new").iterdir()
        if path.is_dir() and not path.name.startswith("_")
    }
    assert subpackages == set(FROZEN_PACKAGES)


def test_hand_written_function_modules_exist():
    from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
        HAND_WRITTEN_FUNCTION_MODULES,
    )

    for name in HAND_WRITTEN_FUNCTION_MODULES:
        assert Path(MAIN_DIR, "Functions_new", name).is_file(), name


def test_functions_generator_keeps_hand_written_modules(tmp_path):
    from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
        generate_functions,
    )

    source = tmp_path / "Functions"
    source.mkdir()
    (source / "helper.py").write_text("def helper():\n    return 1\n")
    (source / "kept.py").write_text("def kept():\n    return 'legacy'\n")
    classes = tmp_path / "Classes_new"
    classes.mkdir()
    output = tmp_path / "Functions_new"
    output.mkdir()
    (output / "kept.py").write_text("# Hand-written\n")
    with pytest.raises(FileNotFoundError):
        generate_functions(source, output, classes, hand_written={"missing.py"})
    generate_functions(source, output, classes, hand_written={"kept.py"})
    assert (output / "kept.py").read_text() == "# Hand-written\n"
    assert (output / "helper.py").is_file()


def test_frozen_gui_writes_only_gen_modules_and_pydantic(tmp_path, monkeypatch):
    from pyleecan.Generator.ClassGenerator.New import generate_gui_new

    root = tmp_path
    (root / "GUI" / "Page").mkdir(parents=True)
    (root / "GUI" / "Page" / "Page.py").write_text("# legacy\n")
    gui_new = root / "GUI_new" / "Page"
    gui_new.mkdir(parents=True)
    (gui_new / "Page.py").write_text("# Hand-written\n")
    calls = []
    monkeypatch.setattr(
        generate_gui_new,
        "write_gen_classes",
        lambda legacy, target: calls.append((legacy, target)) or [],
    )
    written = generate_gui_new.generate_gui(root=root, gen_dict={}, frozen=True)
    assert (gui_new / "Page.py").read_text() == "# Hand-written\n"
    assert calls == [(root / "GUI", root / "GUI_new")]
    assert (root / "GUI_pydantic" / "Page" / "Page.py").is_file()
    assert written["GUI_pydantic"] == 1
