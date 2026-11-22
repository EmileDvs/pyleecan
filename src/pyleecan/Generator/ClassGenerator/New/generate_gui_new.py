"""Generate GUI_new and GUI_pydantic from the legacy GUI (PLAN.md Step 10).

``GUI_new`` is the legacy GUI (``GUI``) on the dataclass classes: every module
goes through the shared modernization pipeline of the methods (FEMM interface
object, moved functions, loggers, ``Methods`` imports, class and function
imports with their new names, keyword constructors, shared errors), then the
imports of the GUI itself are redirected to ``GUI_new``. The other files (Qt
Designer ``.ui``, images, resources) are copied.

``GUI_pydantic`` is ``GUI_new`` on the pydantic classes, by import rewriting
only (``Classes_new`` -> ``Classes_pydantic``, ``Functions_new`` ->
``Functions_pydantic``, ``GUI_new`` -> ``GUI_pydantic``).

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_gui_new``
after generating the classes and the functions. Both folders are deleted and
written again: do not edit them by hand (until the freeze of Step 12).
"""

import ast
import shutil
import tokenize
from importlib.util import resolve_name
from pathlib import Path

GUI_PACKAGES = {"dataclass": "GUI_new", "pydantic": "GUI_pydantic"}
"""GUI package of each class backend"""

LEGACY_GUI_PACKAGE = "GUI"

MODULE_REDIRECTS = {
    "pyleecan.Classes._ClassInfo": "pyleecan.Classes_new._class_info",
}
"""Legacy modules imported by the GUI and their new location (the modules not
handled by the shared pipeline)"""


def _absolute(node, package):
    if node.level:
        return resolve_name("." * node.level + (node.module or ""), package)
    return node.module


def redirect_imports(source, package, redirect):
    """Redirect the ``from X import ...`` imports of a module.

    Parameters
    ----------
    source : str
        Source of the module
    package : str
        Package of the module (to resolve its relative imports)
    redirect : callable
        Absolute module name -> new absolute module name, or None (unchanged)

    Returns
    -------
    source : str
        Source with the redirected imports; a relative import stays relative,
        from the root of the software package (``from ....GUI_new.Tools...``)
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    replacements = []
    package_parts = package.split(".")
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or (not node.module and not node.level):
            continue
        absolute = _absolute(node, package)
        new = redirect(absolute)
        if new is None or new == absolute:
            continue
        new_parts = new.split(".")
        if node.level:
            if new_parts[0] != package_parts[0]:
                raise ValueError(f"{new} is not in the package of {package}")
            level = len(package_parts)
            replacement = ast.ImportFrom(
                module=".".join(new_parts[1:]) or None, names=node.names, level=level
            )
        else:
            replacement = ast.ImportFrom(module=new, names=node.names, level=0)
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        text = ast.unparse(replacement)
        if node.end_lineno > node.lineno:  # Parenthesized import: same layout
            text = _parenthesized(text, node.col_offset)
        replacements.append((start, end, text))
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return source


def redirect_dynamic_imports(source, old, new, soft_name="pyleecan"):
    """Redirect the package named in the dynamic imports of a module.

    The first argument of ``__import__`` / ``import_module``: a string
    (``"pyleecan.GUI.x"``) or a concatenation ending with one
    (``PACKAGE_NAME + ".GUI.x"``); ``old`` -> ``new`` (``GUI`` -> ``GUI_new``).
    """
    if "__import__" not in source and "import_module" not in source:
        return source
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    names = ("__import__", "import_module")
    replacements = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and node.args):
            continue
        func = node.func
        if not (
            (isinstance(func, ast.Name) and func.id in names)
            or (isinstance(func, ast.Attribute) and func.attr == "import_module")
        ):
            continue
        argument = node.args[0]
        if isinstance(argument, ast.BinOp) and isinstance(argument.op, ast.Add):
            argument = argument.right
        if not (isinstance(argument, ast.Constant) and isinstance(argument.value, str)):
            continue
        value = argument.value
        for prefix in (f"{soft_name}.{old}", f".{old}"):
            if value == prefix or value.startswith(prefix + "."):
                value = prefix[: -len(old)] + new + value[len(prefix) :]
                break
        if value != argument.value:
            start = offsets[argument.lineno - 1] + argument.col_offset
            end = offsets[argument.end_lineno - 1] + argument.end_col_offset
            replacements.append((start, end, '"' + value + '"'))
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return source


LEGACY_CLASS_LOADER = "pyleecan.Functions.Load.import_class"
"""Module of the legacy class loader ``import_class(package, name, prop_name)``"""

BACKEND_CLASS_LOADER = "pyleecan.Classes_new._import"
"""Module of the class lookup of the backend ``import_class(name, prop_name)``
(``Classes_pydantic._import`` in GUI_pydantic, by the import rewriting)"""


def redirect_class_loader(source, package, soft_name="pyleecan"):
    """Legacy class loader -> class lookup of the backend.

    ``import_class("pyleecan.Classes", name, prop_name)`` (or ``PACKAGE_NAME +
    ".Classes"``) becomes ``import_class(name, prop_name)`` imported from
    ``Classes_new._import``: the class of the backend, not the legacy one.
    The module is left unchanged when a call names another package.
    """
    if "import_class" not in source:
        return source
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    loader_imports = [
        node
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        and (node.module or node.level)
        and _absolute(node, package) == LEGACY_CLASS_LOADER
        and [(alias.name, alias.asname) for alias in node.names]
        == [("import_class", None)]
    ]
    if not loader_imports:
        return source

    def is_classes(argument):
        return (
            isinstance(argument, ast.Constant)
            and argument.value == f"{soft_name}.Classes"
            or isinstance(argument, ast.BinOp)
            and isinstance(argument.op, ast.Add)
            and isinstance(argument.left, ast.Name)
            and argument.left.id == "PACKAGE_NAME"
            and isinstance(argument.right, ast.Constant)
            and argument.right.value == ".Classes"
        )

    replacements = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Name)
            and node.id == "import_class"
            and isinstance(node.ctx, ast.Load)
        ):
            continue
        call = next(
            (
                parent
                for parent in ast.walk(tree)
                if isinstance(parent, ast.Call) and parent.func is node
            ),
            None,
        )
        if (
            call is None
            or not 2 <= len(call.args) <= 3
            or call.keywords
            or not is_classes(call.args[0])
        ):
            return source  # Another use of the legacy loader: kept
        start = offsets[call.args[0].lineno - 1] + call.args[0].col_offset
        end = offsets[call.args[1].lineno - 1] + call.args[1].col_offset
        replacements.append((start, end, ""))
    redirect = {LEGACY_CLASS_LOADER: BACKEND_CLASS_LOADER}.get
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return redirect_imports(source, package, redirect)


def _parenthesized(text, column):
    """Multi-line ``from x import (a, b)`` of an unparsed import."""
    head, _, names = text.partition(" import ")
    indent = " " * (column + 4)
    items = "".join(f"{indent}{name.strip()},\n" for name in names.split(","))
    return f"{head} import (\n{items}{' ' * column})"


def package_redirect(old, new, soft_name="pyleecan"):
    """Redirect of the modules of a package (``pyleecan.GUI.x`` -> ``pyleecan.GUI_new.x``)."""
    old_prefix = f"{soft_name}.{old}"

    def redirect(module):
        if module == old_prefix or module.startswith(old_prefix + "."):
            return f"{soft_name}.{new}" + module[len(old_prefix) :]
        return None

    return redirect


def legacy_module_redirect(root):
    """Redirect of the legacy modules left by the pipeline (MODULE_REDIRECTS,
    ``Functions.x`` -> ``Functions_new.x`` when the new module exists)."""
    root = Path(root)

    def redirect(module):
        if module in MODULE_REDIRECTS:
            return MODULE_REDIRECTS[module]
        parts = module.split(".")
        if len(parts) > 2 and parts[:2] == ["pyleecan", "Functions"]:
            new = root.joinpath("Functions_new", *parts[2:])
            if new.with_suffix(".py").is_file() or (new / "__init__.py").is_file():
                return ".".join(["pyleecan", "Functions_new", *parts[2:]])
        return None

    return redirect


def modernize_gui_source(source, package, root, gen_dict):
    """Legacy GUI module -> GUI_new module.

    Parameters
    ----------
    source : str
        Source of the legacy module
    package : str
        Package of the GUI_new module (e.g. "pyleecan.GUI_new.Dialog")
    root : Path
        Folder of the pyleecan package
    gen_dict : dict
        Generation dictionary

    Returns
    -------
    source : str
        Source of the GUI_new module
    """
    from .femm_object import INTERFACE_OBJECTS, legacy_signatures, redirect_femm_calls
    from .generate_methods_new import _redirect_methods_imports
    from .modernize import (
        modernize_names,
        redirect_get_logger,
        remove_coding_declaration,
        remove_python2_branches,
    )
    from .moved_functions import redirect_moved_calls

    source = remove_coding_declaration(source)
    source = remove_python2_branches(source)
    for spec in INTERFACE_OBJECTS:
        source = redirect_femm_calls(source, package, legacy_signatures(spec), spec)
    source = redirect_moved_calls(source, package, None, gen_dict=gen_dict)
    source = redirect_get_logger(source, package)
    # The errors of the methods and functions: the shared ones (the GUI
    # catches the errors raised by the classes)
    from .modernize import _redirect_shared_error_imports, shared_error_names

    source = _redirect_shared_error_imports(
        source, package, method_error_names=shared_error_names()
    )
    source = _redirect_methods_imports(source, package, str(Path(root) / "Classes_new"))
    source = modernize_names(source, package, gen_dict, None)
    from .moved_functions import redirect_moved_modules

    source = redirect_moved_modules(source, package)
    source = redirect_class_loader(source, package)
    source = redirect_imports(source, package, legacy_module_redirect(root))
    source = redirect_dynamic_imports(
        source, LEGACY_GUI_PACKAGE, GUI_PACKAGES["dataclass"]
    )
    source = retire_replaced_widgets(source)
    return redirect_imports(
        source, package, package_redirect(LEGACY_GUI_PACKAGE, GUI_PACKAGES["dataclass"])
    )


def pydantic_gui_source(source, package):
    """GUI_new module -> GUI_pydantic module (imports only)."""
    from .class_generator import BACKENDS, FUNCTION_PACKAGES

    redirects = [
        package_redirect(BACKENDS["dataclass"], BACKENDS["pydantic"]),
        package_redirect(FUNCTION_PACKAGES["dataclass"], FUNCTION_PACKAGES["pydantic"]),
        package_redirect(GUI_PACKAGES["dataclass"], GUI_PACKAGES["pydantic"]),
    ]

    def redirect(module):
        for rule in redirects:
            new = rule(module)
            if new is not None:
                return new
        return None

    source = redirect_dynamic_imports(
        source, GUI_PACKAGES["dataclass"], GUI_PACKAGES["pydantic"]
    )
    return redirect_imports(source, package, redirect)


RESOURCES = "Resources"
"""Sub-package of the Qt resources: images and compiled resources (28 MB) are
not copied, the GUI_new modules use the legacy ones (RESOURCES_SHIM)"""

RESOURCES_KEPT = {"__init__.py"}
"""Files of RESOURCES copied (pixmap_dict: names of the resources)"""

RESOURCES_SHIM = '''"""Qt resources of the GUI (generated, see generate_gui_new.py).

The compiled resources of the legacy GUI are loaded from their file, without
importing the legacy GUI package (and its classes); GUI_new and GUI_pydantic
register them once.
"""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_NAME = "pyleecan._gui_resources_rc"
if _NAME not in sys.modules:
    _spec = spec_from_file_location(
        _NAME, Path(__file__).resolve().parents[2] / "GUI" / "Resources" / "pyleecan_rc.py"
    )
    sys.modules[_NAME] = module_from_spec(_spec)
    _spec.loader.exec_module(sys.modules[_NAME])
'''


def _write_tree(source_dir, target_dir, convert, fixes=None):
    """Copy a tree, converting the Python modules: convert(source, package).

    ``fixes`` ({module path (posix): LegacyFix tuple}) are applied to the
    sources before the conversion; each module listed must exist.
    """
    from .legacy_fixes import apply_fixes

    fixes = fixes or {}
    missing = [name for name in fixes if not (source_dir / name).is_file()]
    if missing:
        raise FileNotFoundError(f"Fixed GUI modules not found: {missing}")
    if target_dir.exists():
        shutil.rmtree(target_dir)
    written = 0
    for path in sorted(source_dir.rglob("*")):
        if "__pycache__" in path.parts or path.is_dir() or path.suffix == ".pyc":
            continue
        relative = path.relative_to(source_dir)
        if relative.parts[0] == RESOURCES and source_dir.name == LEGACY_GUI_PACKAGE:
            if relative.name == "pyleecan_rc.py":
                target = target_dir / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(RESOURCES_SHIM, encoding="utf-8")
                written += 1
                continue
            if relative.as_posix() not in {
                f"{RESOURCES}/{name}" for name in RESOURCES_KEPT
            }:
                continue
        target = target_dir / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix != ".py":
            shutil.copy2(path, target)
            continue
        with tokenize.open(path) as source_file:
            source = source_file.read()
        if relative.as_posix() in fixes:
            source = apply_fixes(
                source, fixes[relative.as_posix()], f"GUI/{relative.as_posix()}"
            )
        package = ".".join(["pyleecan", target_dir.name, *relative.parts[:-1]])
        target.write_text(convert(source, package), encoding="utf-8")
        written += 1
    return written


def generate_gui(root=None, gen_dict=None):
    """Write GUI_new from GUI, then GUI_pydantic from GUI_new.

    Parameters
    ----------
    root : str or Path, optional
        Folder of the pyleecan package (default: MAIN_DIR)
    gen_dict : dict, optional
        Generation dictionary (default: the one of the CSV files)

    Returns
    -------
    written : dict
        {GUI package: number of Python modules written}
    """
    from pyleecan.definitions import MAIN_DIR

    from .source_names import name_maps

    root = Path(root) if root is not None else Path(MAIN_DIR)
    gen_dict = gen_dict if gen_dict is not None else name_maps().gen_dict
    from .legacy_fixes import GUI_LEGACY_FIXES
    from .moved_functions import GUI_TARGET, MOVED_MODULES

    dataclass_dir = root / GUI_PACKAGES["dataclass"]
    pydantic_dir = root / GUI_PACKAGES["pydantic"]
    written = {
        dataclass_dir.name: _write_tree(
            root / LEGACY_GUI_PACKAGE,
            dataclass_dir,
            lambda source, package: modernize_gui_source(
                source, package, root, gen_dict
            ),
            fixes=GUI_LEGACY_FIXES,
        )
    }
    # The Gen_ modules (widget limits and help) from ClassInfo, not from the
    # CSV files of the legacy GUI generator (removed in Phase 2)
    write_gen_classes(root / LEGACY_GUI_PACKAGE, dataclass_dir)
    # Functions moved to the GUI (moved_functions.MOVED_MODULES)
    for legacy, new in sorted(MOVED_MODULES.items()):
        if not new.startswith(GUI_TARGET):
            continue
        parts = new.split(".")
        target = root.joinpath(*parts).with_suffix(".py")
        target.parent.mkdir(parents=True, exist_ok=True)
        legacy_path = root.joinpath("Functions", *legacy.split(".")).with_suffix(".py")
        with tokenize.open(legacy_path) as file:
            source = file.read()
        package = ".".join(["pyleecan", *parts[:-1]])
        target.write_text(
            modernize_gui_source(source, package, root, gen_dict), encoding="utf-8"
        )
        written[dataclass_dir.name] += 1
    written[pydantic_dir.name] = _write_tree(
        dataclass_dir, pydantic_dir, pydantic_gui_source
    )
    return written


GEN_LIST = "gen_list.json"
"""Widgets of a Qt Designer module set up from the class properties
(legacy GUI generator: ``Generator/gui_generator.py``)"""

MIN_SPIN = -999999
MAX_SPIN = 999999
"""Limits of a spinbox whose property has none (as the legacy GUI generator)"""

_WIDGET_METADATA_SCRIPT = """
import json, sys
from pyleecan.Classes_new._class_info import ClassInfo
class_dict = ClassInfo().get_dict()
wanted = json.loads(sys.stdin.read())
result = {}
for class_name, name in wanted:
    prop = next(p for p in class_dict[class_name]["properties"] if p["name"] == name)
    result[class_name + "." + name] = {
        "min": prop["min"], "max": prop["max"], "desc": prop["desc"]
    }
print(json.dumps(result))
"""


def widget_metadata(properties):
    """Min, max and description of class properties, from ClassInfo.

    Read in a new process: the class modules are the ones just generated,
    not the ones imported before by the generator.

    Parameters
    ----------
    properties : iterable
        (class name, property name)

    Returns
    -------
    metadata : dict
        {(class name, property name): {"min", "max", "desc"}}
    """
    import json
    import subprocess
    import sys

    wanted = sorted(set(properties))
    completed = subprocess.run(
        [sys.executable, "-c", _WIDGET_METADATA_SCRIPT],
        input=json.dumps(wanted),
        capture_output=True,
        text=True,
        check=True,
    )
    result = json.loads(completed.stdout.strip().splitlines()[-1])
    return {tuple(key.split(".", 1)): value for key, value in result.items()}


def _number(value):
    """Limit as written in the setup code (an integral float as an int)."""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return repr(value)


def gen_class_source(ui_name, ui_module, gen_list, metadata):
    """Source of a ``Gen_`` class: widget limits and help texts.

    Same code as the legacy GUI generator (``gen_gui_edit_file``), from the
    class information (``ClassInfo``) instead of the CSV files.

    Parameters
    ----------
    ui_name : str
        Name of the Qt Designer module, without "Ui_" (e.g. "PVentCirc")
    ui_module : str
        Module of the Ui_ class, relative import (e.g. ".Ui_PVentCirc")
    gen_list : list
        Content of gen_list.json: {"cls", "name", "widget"}
    metadata : dict
        {(class name, property name): {"min", "max", "desc"}}

    Returns
    -------
    source : str
        Source of the Gen_ module
    """
    lines = [
        f'"""File generated according to {ui_name}/gen_list.json and the class',
        "information (ClassInfo): limits and help of the widgets.",
        'WARNING! All changes made in this file will be lost!\n"""',
        f"from {ui_module} import Ui_{ui_name}",
        "",
        "",
        f"class Gen_{ui_name}(Ui_{ui_name}):",
        f"    def setupUi(self, {ui_name}):",
        '        """Set the widget limits and help texts (class information)"""',
        f"        Ui_{ui_name}.setupUi(self, {ui_name})",
    ]
    for edit in gen_list:
        data = metadata[(edit["cls"], edit["name"])]
        widgets = edit["widget"] if isinstance(edit["widget"], list) else [edit["widget"]]
        for widget in widgets:
            lines.append(f"        # Setup of {widget}")
            kind = widget.split("_")[0]
            if kind == "si":  # SpinBox
                vmin = MIN_SPIN if data["min"] is None else data["min"]
                vmax = MAX_SPIN if data["max"] is None else data["max"]
                lines.append(f"        self.{widget}.setMinimum({_number(vmin)})")
                lines.append(f"        self.{widget}.setMaximum({_number(vmax)})")
            elif kind == "lf":  # FloatEdit
                if data["min"] is not None:
                    lines.append(
                        f"        self.{widget}.validator().setBottom({_number(data['min'])})"
                    )
                if data["max"] is not None:
                    lines.append(
                        f"        self.{widget}.validator().setTop({_number(data['max'])})"
                    )
            lines.append(f"        txt = self.tr({data['desc']!r})")
            lines.append(f"        self.{widget}.setWhatsThis(txt)")
            lines.append(f"        self.{widget}.setToolTip(txt)")
            lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def write_gen_classes(legacy_dir, target_dir, metadata=None):
    """Write the Gen_ modules of GUI_new from the gen_list.json files.

    Parameters
    ----------
    legacy_dir : Path
        Legacy GUI folder (gen_list.json files, next to the .ui modules)
    target_dir : Path
        GUI_new folder
    metadata : dict, optional
        Property metadata (default: widget_metadata of the listed properties)

    Returns
    -------
    written : list
        Paths of the written modules
    """
    import json

    gen_lists = {
        path: json.loads(path.read_text(encoding="utf-8"))
        for path in sorted(Path(legacy_dir).rglob(GEN_LIST))
    }
    if metadata is None:
        metadata = widget_metadata(
            (edit["cls"], edit["name"])
            for gen_list in gen_lists.values()
            for edit in gen_list
        )
    written = []
    for path, gen_list in gen_lists.items():
        ui_names = [ui.stem[3:] for ui in path.parent.glob("Ui_*.py")]
        if len(ui_names) != 1:
            raise ValueError(f"{path}: one Ui_ module expected, {ui_names} found")
        ui_name = ui_names[0]
        target = Path(target_dir) / path.parent.relative_to(legacy_dir) / f"Gen_{ui_name}.py"
        target.write_text(
            gen_class_source(ui_name, f".Ui_{ui_name}", gen_list, metadata),
            encoding="utf-8",
        )
        written.append(target)
    return written


def retire_replaced_widgets(source):
    """Replace ``widget.setParent(None)`` by ``widget.hide(); widget.deleteLater()``.

    The dialogs replace a page by a new one after ``setParent(None)``: the old
    page, owned by Python without parent, is freed by the garbage collector at
    any later time (inside another Qt call), which crashes PySide6 (access
    violation during garbage collection, the legacy GUI as well; issue #750).
    Hidden and kept with its parent, Qt deletes it in the event loop.
    """
    if "setParent(None)" not in source:
        return source
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    offsets = [0]
    for line in lines:
        offsets.append(offsets[-1] + len(line))
    replacements = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Call)
            and isinstance(node.value.func, ast.Attribute)
            and node.value.func.attr == "setParent"
            and len(node.value.args) == 1
            and isinstance(node.value.args[0], ast.Constant)
            and node.value.args[0].value is None
            and not node.value.keywords
        ):
            continue
        widget = node.value.func.value
        start = offsets[widget.lineno - 1] + widget.col_offset
        end = offsets[widget.end_lineno - 1] + widget.end_col_offset
        name = source[start:end]
        indent = " " * node.col_offset
        statement_start = offsets[node.lineno - 1] + node.col_offset
        statement_end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append(
            (
                statement_start,
                statement_end,
                f"{name}.hide()  # Deleted by Qt (no garbage collection crash)\n"
                f"{indent}{name}.deleteLater()",
            )
        )
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return source


if __name__ == "__main__":
    print(generate_gui())
