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
    source = _redirect_methods_imports(source, package, str(Path(root) / "Classes_new"))
    source = modernize_names(source, package, gen_dict, None)
    source = redirect_imports(source, package, legacy_module_redirect(root))
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


def _write_tree(source_dir, target_dir, convert):
    """Copy a tree, converting the Python modules: convert(source, package)."""
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
    dataclass_dir = root / GUI_PACKAGES["dataclass"]
    pydantic_dir = root / GUI_PACKAGES["pydantic"]
    return {
        dataclass_dir.name: _write_tree(
            root / LEGACY_GUI_PACKAGE,
            dataclass_dir,
            lambda source, package: modernize_gui_source(
                source, package, root, gen_dict
            ),
        ),
        pydantic_dir.name: _write_tree(
            dataclass_dir, pydantic_dir, pydantic_gui_source
        ),
    }


if __name__ == "__main__":
    print(generate_gui())
