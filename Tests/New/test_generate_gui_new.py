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
