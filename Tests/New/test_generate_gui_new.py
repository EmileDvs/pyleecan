"""GUI_new / GUI_pydantic generator (PLAN.md Step 10)."""

import ast

from pyleecan.Generator.ClassGenerator.New.generate_gui_new import (
    MODULE_REDIRECTS,
    package_redirect,
    pydantic_gui_source,
    redirect_imports,
)


def test_package_redirect():
    redirect = package_redirect("GUI", "GUI_new")
    assert redirect("pyleecan.GUI") == "pyleecan.GUI_new"
    assert (
        redirect("pyleecan.GUI.Tools.FloatEdit") == "pyleecan.GUI_new.Tools.FloatEdit"
    )
    assert redirect("pyleecan.GUI_other") is None
    assert redirect("pyleecan.Classes.LamSlot") is None


def test_redirect_imports():
    source = (
        "from ....GUI.Tools.FloatEdit import FloatEdit\n"
        "from ....GUI import gui_option\n"
        "from pyleecan.GUI.Resources import pyleecan_rc\n"
        "from ..Ui_x import Ui_x\n"
        "from ....GUI.Dialog.DMachineSetup import (\n"
        "    DMachineSetup,\n"
        "    SMachineType as SMT,\n"
        ")\n"
    )
    package = "pyleecan.GUI_new.Dialog.DMachineSetup"
    result = redirect_imports(source, package, package_redirect("GUI", "GUI_new"))
    ast.parse(result)
    assert result == (
        "from ....GUI_new.Tools.FloatEdit import FloatEdit\n"
        "from ....GUI_new import gui_option\n"
        "from pyleecan.GUI_new.Resources import pyleecan_rc\n"
        "from ..Ui_x import Ui_x\n"
        "from ....GUI_new.Dialog.DMachineSetup import (\n"
        "    DMachineSetup,\n"
        "    SMachineType as SMT,\n"
        ")\n"
    )
    # Idempotent
    assert (
        redirect_imports(result, package, package_redirect("GUI", "GUI_new")) == result
    )


def test_module_redirects():
    source = "from ...Classes._ClassInfo import ClassInfo\n"
    result = redirect_imports(source, "pyleecan.GUI_new.Tools", MODULE_REDIRECTS.get)
    assert result == "from ...Classes_new._class_info import ClassInfo\n"


def test_pydantic_gui_source():
    source = (
        "from ....Classes_new.machine.lam_slot import LamSlot\n"
        "from ....Functions_new.load import load\n"
        "from ....GUI_new.Tools.FloatEdit import FloatEdit\n"
        "from ....classes_common.errors import SlotCheckError\n"
    )
    result = pydantic_gui_source(source, "pyleecan.GUI_pydantic.Dialog.DMachineSetup")
    assert result == (
        "from ....Classes_pydantic.machine.lam_slot import LamSlot\n"
        "from ....Functions_pydantic.load import load\n"
        "from ....GUI_pydantic.Tools.FloatEdit import FloatEdit\n"
        "from ....classes_common.errors import SlotCheckError\n"
    )


def test_redirect_dynamic_imports():
    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import (
        redirect_dynamic_imports,
    )

    source = (
        'm = __import__(PACKAGE_NAME + ".GUI.Dialog.DMachineSetup", fromlist=["x"])\n'
        'n = import_module("pyleecan.GUI.Tools")\n'
        'o = __import__(PACKAGE_NAME + ".GUI_other")\n'
    )
    result = redirect_dynamic_imports(source, "GUI", "GUI_new")
    assert result == (
        'm = __import__(PACKAGE_NAME + ".GUI_new.Dialog.DMachineSetup", fromlist=["x"])\n'
        'n = import_module("pyleecan.GUI_new.Tools")\n'
        'o = __import__(PACKAGE_NAME + ".GUI_other")\n'
    )
    assert redirect_dynamic_imports(result, "GUI_new", "GUI_pydantic").count("GUI_pydantic") == 2


def test_retire_replaced_widgets():
    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import (
        retire_replaced_widgets,
    )

    source = (
        "def s_update(self):\n"
        "    self.w_bore.setParent(None)\n"
        "    self.w_bore = Page(self.lam)\n"
        "    for wid in self.w_list:\n"
        "        wid.setParent(None)\n"
        "    self.w_other.setParent(self)\n"
    )
    result = retire_replaced_widgets(source)
    assert (
        "    self.w_bore.hide()  # Deleted by Qt (no garbage collection crash)\n"
        "    self.w_bore.deleteLater()\n"
        "    self.w_bore = Page(self.lam)\n"
    ) in result
    assert "        wid.hide()" in result and "        wid.deleteLater()\n" in result
    assert "    self.w_other.setParent(self)\n" in result
    assert retire_replaced_widgets(result) == result


def test_redirect_class_loader():
    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import (
        redirect_class_loader,
    )

    package = "pyleecan.GUI_new.Tools.WTreeEdit"
    source = (
        "from ....Functions.Load.import_class import import_class\n"
        "\n"
        "def f(name):\n"
        '    a = import_class("pyleecan.Classes", name, "")()\n'
        '    return import_class(PACKAGE_NAME + ".Classes", "Arc1")\n'
    )
    result = redirect_class_loader(source, package)
    assert result == (
        "from ....Classes_new._import import import_class\n"
        "\n"
        "def f(name):\n"
        '    a = import_class(name, "")()\n'
        '    return import_class("Arc1")\n'
    )
    assert redirect_class_loader(result, package) == result
    # Unused import: redirected too
    unused = "from ....Functions.Load.import_class import import_class\n"
    assert "Classes_new._import" in redirect_class_loader(unused, package)
    # Another package named: unchanged
    other = unused + 'X = import_class("other.Classes", "X")\n'
    assert redirect_class_loader(other, package) == other


def test_gui_legacy_fixes_apply_to_legacy_gui():
    import tokenize
    from pathlib import Path

    from pyleecan.definitions import MAIN_DIR
    from pyleecan.Generator.ClassGenerator.New.legacy_fixes import (
        GUI_LEGACY_FIXES,
        apply_fixes,
    )

    for name, fixes in GUI_LEGACY_FIXES.items():
        with tokenize.open(Path(MAIN_DIR, "GUI", name)) as file:
            apply_fixes(file.read(), fixes, name)  # Raises if legacy changed


def test_write_tree_applies_fixes(tmp_path):
    import pytest

    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import _write_tree
    from pyleecan.Generator.ClassGenerator.New.legacy_fixes import LegacyFix

    source_dir = tmp_path / "GUI"
    (source_dir / "Tools").mkdir(parents=True)
    (source_dir / "Tools" / "Edit.py").write_text("def f(unit='', *args):\n    pass\n")
    target_dir = tmp_path / "GUI_new"
    fixes = {"Tools/Edit.py": (LegacyFix(old="unit='', *args", new="*args, unit=''"),)}
    _write_tree(source_dir, target_dir, lambda source, package: source, fixes=fixes)
    assert "def f(*args, unit='')" in (target_dir / "Tools" / "Edit.py").read_text()
    with pytest.raises(FileNotFoundError):
        _write_tree(source_dir, target_dir, lambda s, p: s, fixes={"Tools/No.py": ()})


def test_clear_gui_results(tmp_path):
    from Tests.New.conftest import clear_gui_results

    folder = tmp_path / "GUI"
    (folder / "Old").mkdir(parents=True)
    (folder / "Old" / "left.csv").write_text("x")
    clear_gui_results(folder)
    assert folder.is_dir() and not any(folder.iterdir())
    clear_gui_results(tmp_path / "New")  # Created when missing
    assert (tmp_path / "New").is_dir()


def test_gen_class_source():
    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import (
        MAX_SPIN,
        gen_class_source,
    )

    gen_list = [
        {"cls": "Hole", "name": "Zh", "widget": ["in_Zh", "si_Zh"]},
        {"cls": "VentilationCirc", "name": "D0", "widget": "lf_D0"},
    ]
    metadata = {
        ("Hole", "Zh"): {"min": 0, "max": None, "desc": "Number of 'holes'"},
        ("VentilationCirc", "D0"): {"min": 0.0, "max": 1e-3, "desc": "Diameter"},
    }
    source = gen_class_source("PVent", ".Ui_PVent", gen_list, metadata)
    assert "from .Ui_PVent import Ui_PVent\n" in source
    assert "class Gen_PVent(Ui_PVent):" in source
    assert "        self.si_Zh.setMinimum(0)\n" in source
    assert f"        self.si_Zh.setMaximum({MAX_SPIN})\n" in source
    assert "self.in_Zh.setMinimum" not in source  # Label: help only
    assert "        txt = self.tr(\"Number of 'holes'\")\n" in source
    assert "        self.lf_D0.validator().setBottom(0)\n" in source
    assert "        self.lf_D0.validator().setTop(0.001)\n" in source
    compile(source, "Gen_PVent.py", "exec")


def test_widget_metadata_from_class_info():
    from pyleecan.Generator.ClassGenerator.New.generate_gui_new import widget_metadata

    metadata = widget_metadata([("VentilationCirc", "D0"), ("Hole", "Zh")])
    assert metadata[("VentilationCirc", "D0")] == {
        "min": 0,
        "max": None,
        "desc": "Hole diameters",
    }
    assert metadata[("Hole", "Zh")]["min"] == 0
