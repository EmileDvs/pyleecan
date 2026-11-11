"""Generate Functions_new from Functions without modifying the legacy package.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_function_new_classes``
after generating Classes_new. Existing generated copies are overwritten. Legacy
load/save compatibility and unsupported dynamic imports are reported for review.
Selected function exceptions are imported directly from Classes_new._error;
regenerate the classes first when those shared definitions change.

Experimental adaptations are implemented as targeted source transformations
here. Changes made only in Functions_new are overwritten on regeneration.
"""

import ast
import re
import shutil
import tokenize
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.definitions import MAIN_DIR
from pyleecan.Functions_new.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    VENDORED_CLASS_PACKAGES,
    class_module_name,
)

FUNCTION_ERRORS = {
    "Converter.Utils.ConvertionError": {"ConvertionError": "ConvertionError"},
    "Converter.Utils.EquivalentError": {"EquivalentError": "EquivalentError"},
    "FEMM.draw_FEMM": {"FEMMError": "FEMMError"},
    "Geometry.create_surface": {"SurfaceError": "SurfaceError"},
    "Geometry.merge_notch_list": {"NotchError": "NotchError"},
    "GMSH": {"InputError": "GMSHInputError"},
    "Load.load_json": {"LoadMissingFileError": "LoadMissingFileError"},
    "Load.retrocompatibility": {"RetroCompatibilityError": "RetroCompatibilityError"},
    "load": {
        "LoadMissingFolderError": "LoadMissingFolderError",
        "LoadWrongDictClassError": "LoadWrongDictClassError",
        "LoadWrongTypeError": "LoadWrongTypeError",
        "LoadSwitchError": "LoadSwitchError",
    },
    "path_tools": {"FileError": "FileError", "ImportError": "PathImportError"},
    "save": {"FormatError": "FormatError"},
    "SciDataTool": {
        "FTError": "FTError",
        "AxisError": "AxisError",
        "UnitError": "UnitError",
        "NormError": "NormError",
    },
    "Structural.conversions": {"DimError": "DimError"},
}


def _redirect_function_errors(source, path, relative_path, class_dir):
    """Replace selected definitions with shared imports only where used."""
    parts = list(relative_path.with_suffix("").parts)
    if parts[-1] == "__init__":
        parts.pop()
    errors = FUNCTION_ERRORS.get(".".join(parts))
    if not errors:
        return source
    tree = ast.parse(source, filename=str(path))
    definitions = {
        node.name: node for node in tree.body if isinstance(node, ast.ClassDef)
    }
    missing = set(errors) - definitions.keys()
    if missing:
        raise ValueError(
            f"{path}: missing function exceptions: {', '.join(sorted(missing))}"
        )
    error_path = class_dir / "_error.py"
    if not error_path.is_file():
        raise FileNotFoundError(
            f"Shared exceptions not generated: {error_path}; generate classes first"
        )
    with tokenize.open(error_path) as error_file:
        shared = {
            node.name: node
            for node in ast.parse(error_file.read(), filename=str(error_path)).body
            if isinstance(node, ast.ClassDef)
        }
    for name, shared_name in errors.items():
        node = definitions[name]
        shared_node = shared.get(shared_name)
        if shared_node is None:
            raise ValueError(f"{error_path}: missing {shared_name}; regenerate classes")
        expected_bases = [
            errors.get(base.id, base.id) if isinstance(base, ast.Name) else None
            for base in node.bases
        ]
        if expected_bases != [
            base.id if isinstance(base, ast.Name) else None for base in shared_node.bases
        ]:
            raise ValueError(
                f"{error_path}: incompatible {shared_name}; regenerate classes"
            )
        if node.decorator_list:
            raise ValueError(f"{path}:{node.lineno}: decorated exception {name}")
    used = {
        node.id
        for item in tree.body
        if item not in (definitions[name] for name in errors)
        for node in ast.walk(item)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    lines = source.splitlines(keepends=True)
    for name, shared_name in sorted(
        errors.items(), key=lambda item: definitions[item[0]].lineno, reverse=True
    ):
        node = definitions[name]
        alias = f" as {name}" if name != shared_name else ""
        lines[node.lineno - 1 : node.end_lineno] = (
            [f"from pyleecan.Classes_new._error import {shared_name}{alias}\n"]
            if name in used
            else []
        )
    return "".join(lines)


def _redirect_shared_error_imports(source, package, soft_name="pyleecan"):
    """Redirect imports of centralized function errors, preserving bindings."""
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom):
            continue
        module = node.module or ""
        if node.level:
            module = resolve_name("." * node.level + module, package)
        errors = None
        for prefix in (f"{soft_name}.Functions.", f"{soft_name}.Functions_new."):
            if module.startswith(prefix):
                errors = FUNCTION_ERRORS.get(module[len(prefix) :])
                break
        if not errors:
            continue
        if any(alias.name == "*" for alias in node.names):
            raise ValueError(f"{module}:{node.lineno}: wildcard error import requires review")
        selected = [alias for alias in node.names if alias.name in errors]
        if not selected:
            continue
        remaining = [alias for alias in node.names if alias.name not in errors]
        shared = [
            ast.alias(
                name=errors[alias.name],
                asname=alias.asname or (
                    alias.name if errors[alias.name] != alias.name else None
                ),
            )
            for alias in selected
        ]
        imports = []
        if remaining:
            imports.append(ast.ImportFrom(module=node.module, names=remaining, level=node.level))
        imports.append(
            ast.ImportFrom(module=f"{soft_name}.Classes_new._error", names=shared, level=0)
        )
        replacement = ("; ".join(ast.unparse(item) for item in imports)).encode("utf-8")
        replacements.append(
            (offsets[node.lineno - 1] + node.col_offset,
             offsets[node.end_lineno - 1] + node.end_col_offset, replacement)
        )
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    return data.decode("utf-8")


def _adapt_retrocompatibility(source, path):
    """Apply the versioned normalization migration to the legacy source."""
    tree = ast.parse(source, filename=str(path))
    lines = source.splitlines(keepends=True)

    def unique_node(predicate, description):
        matches = [node for node in tree.body if predicate(node)]
        if len(matches) != 1:
            raise ValueError(f"{path}: expected exactly one {description}")
        return matches[0]

    def function(name):
        return unique_node(
            lambda node: isinstance(node, ast.FunctionDef) and node.name == name,
            f"function {name}",
        )

    existing_names = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store)
    }
    if "NORMALIZATION_CLASS_NAMES" in existing_names:
        raise ValueError(f"{path}: normalization name mapping already exists")
    search = function("_search_and_update")
    if (
        len(search.body) < 2
        or not isinstance(search.body[0], ast.Expr)
        or not isinstance(search.body[0].value, ast.Constant)
        or not isinstance(search.body[0].value.value, str)
        or not isinstance(search.body[1], ast.If)
    ):
        raise ValueError(f"{path}: unexpected _search_and_update structure")
    versions = unique_node(
        lambda node: isinstance(node, ast.Assign)
        and len(node.targets) == 1
        and isinstance(node.targets[0], ast.Name)
        and node.targets[0].id == "OBJECT_VERSION_DICT"
        and isinstance(node.value, ast.Dict),
        "OBJECT_VERSION_DICT",
    )
    if any(
        isinstance(key, ast.Constant) and key.value == "Normalization"
        for key in versions.value.keys
    ):
        raise ValueError(f"{path}: Normalization version already exists")
    if lines[versions.end_lineno - 1].strip() != "}":
        raise ValueError(f"{path}: unexpected OBJECT_VERSION_DICT layout")
    mapping_source = repr(NORMALIZATION_CLASS_NAMES)
    conversion = (
        f"NORMALIZATION_CLASS_NAMES = {mapping_source}\n\n\n"
        'Normalization_VERSION = "1.5.2"\n\n\n'
        "def convert_normalization(init_dict):\n"
        '    """Update an old normalization class name in place."""\n'
        '    class_name = init_dict.get("__class__")\n'
        "    if class_name in NORMALIZATION_CLASS_NAMES:\n"
        '        init_dict["__class__"] = NORMALIZATION_CLASS_NAMES[class_name]\n'
    )
    convert_init = function("convert_init_dict")
    edits = [
        (convert_init.lineno - 1, convert_init.lineno - 1, conversion + "\n\n"),
        (
            search.body[1].lineno - 1,
            search.body[1].lineno - 1,
            '    if update_dict["Normalization"]:\n        convert_normalization(obj_dict)\n',
        ),
        (
            versions.end_lineno - 1,
            versions.end_lineno - 1,
            '    "Normalization": Normalization_VERSION,\n',
        ),
    ]
    for start, end, replacement in sorted(edits, reverse=True):
        lines[start:end] = [replacement]
    return "".join(lines)


def _rewrite_source(source, path, relative_path, class_dir):
    """Redirect supported imports and report legacy references needing review."""
    tree = ast.parse(source, filename=str(path))
    data = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(data):
        if value == 10:
            offsets.append(index + 1)

    def offset(line, column):
        return offsets[line - 1] + column

    package_parts = ["pyleecan", "Functions"] + list(relative_path.parts[:-1])
    package = ".".join(package_parts)
    replacements = []
    issues = []
    deferred = relative_path.parts[0] in {"Load", "Save"} or relative_path.name in {
        "load.py",
        "save.py",
        "copy.py",
        "load_switch.py",
    }
    dynamic_assignments = {}
    if not deferred:
        for node in ast.walk(tree):
            if not (
                isinstance(node, ast.Assign)
                and len(node.targets) == 1
                and isinstance(node.targets[0], ast.Name)
                and isinstance(node.value, ast.Call)
                and isinstance(node.value.func, ast.Name)
                and node.value.func.id == "import_class"
                and len(node.value.args) == 2
                and all(isinstance(arg, ast.Constant) for arg in node.value.args)
                and node.value.args[0].value == "pyleecan.Classes"
                and isinstance(node.value.args[1].value, str)
            ):
                continue
            name = node.value.args[1].value
            if (class_dir / (class_module_name(name) + ".py")).is_file():
                dynamic_assignments[node] = name
    converted_calls = {id(node.value.func) for node in dynamic_assignments}
    remaining_loader_uses = any(
        isinstance(node, ast.Name)
        and node.id == "import_class"
        and isinstance(node.ctx, ast.Load)
        and id(node) not in converted_calls
        for node in ast.walk(tree)
    )
    for node in ast.walk(tree):
        if node in dynamic_assignments:
            name = dynamic_assignments[node]
            target = node.targets[0].id
            imported_name = NORMALIZATION_CLASS_NAMES.get(name, name)
            replacement = ast.ImportFrom(
                module="pyleecan.Classes_new." + class_module_name(name),
                names=[
                    ast.alias(
                        name=imported_name,
                        asname=target if target != imported_name else None,
                    )
                ],
                level=0,
            )
            start = offset(node.lineno, node.col_offset)
            end = offset(node.end_lineno, node.end_col_offset)
            replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                module = resolve_name("." * node.level + module, package)
            if (
                dynamic_assignments
                and not remaining_loader_uses
                and module == "pyleecan.Functions.Load.import_class"
                and len(node.names) == 1
                and node.names[0].name == "import_class"
                and node.names[0].asname is None
            ):
                start = offset(node.lineno, node.col_offset)
                end = offset(node.end_lineno, node.end_col_offset)
                replacements.append((start, end, b""))
                continue
            if module == "pyleecan.Classes" or module.startswith("pyleecan.Classes."):
                name = module.removeprefix("pyleecan.Classes.")
                if name.split(".")[0] in VENDORED_CLASS_PACKAGES:
                    module_path = class_dir.joinpath(*name.split("."))
                    if not module_path.with_suffix(".py").is_file() and not (
                        module_path / "__init__.py"
                    ).is_file():
                        issues.append((node.lineno, f"legacy import: {module}"))
                        continue
                    replacement = ast.ImportFrom(
                        module="pyleecan.Classes_new." + name,
                        names=node.names,
                        level=0,
                    )
                elif (
                    module == "pyleecan.Classes"
                    or "." in name
                    or name.startswith("_")
                    or not (class_dir / (class_module_name(name) + ".py")).is_file()
                    or any(alias.name == "*" for alias in node.names)
                ):
                    issues.append((node.lineno, f"legacy import: {module}"))
                    continue
                else:
                    aliases = []
                    for alias in node.names:
                        renamed = NORMALIZATION_CLASS_NAMES.get(alias.name, alias.name)
                        binding = alias.asname or (
                            alias.name if renamed != alias.name else None
                        )
                        aliases.append(ast.alias(name=renamed, asname=binding))
                    replacement = ast.ImportFrom(
                        module="pyleecan.Classes_new." + class_module_name(name),
                        names=aliases,
                        level=0,
                    )
            elif not node.level and (
                module == "pyleecan.Functions"
                or module.startswith("pyleecan.Functions.")
            ):
                replacement = ast.ImportFrom(
                    module=module.replace(
                        "pyleecan.Functions", "pyleecan.Functions_new", 1
                    ),
                    names=node.names,
                    level=0,
                )
            elif (
                node.level
                and (
                    module == "pyleecan.Functions"
                    or module.startswith("pyleecan.Functions.")
                )
                and (node.module or "").startswith("Functions")
            ):
                replacement = ast.ImportFrom(
                    module=node.module.replace("Functions", "Functions_new", 1),
                    names=node.names,
                    level=node.level,
                )
            else:
                continue
            start = offset(node.lineno, node.col_offset)
            end = offset(node.end_lineno, node.end_col_offset)
            replacements.append((start, end, ast.unparse(replacement).encode("utf-8")))
        elif isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.startswith(("pyleecan.Classes", "pyleecan.Functions")):
                    issues.append(
                        (node.lineno, f"import requires review: {alias.name}")
                    )
        elif isinstance(node, ast.Call):
            if any(node is assignment.value for assignment in dynamic_assignments):
                continue
            if isinstance(node.func, ast.Name) and node.func.id in {
                "import_class",
                "import_experimental_class",
            }:
                issues.append((node.lineno, "dynamic class loader requires review"))
            elif any(
                isinstance(arg, ast.Constant)
                and isinstance(arg.value, str)
                and re.search(r"\bpyleecan\.(Classes|Functions)\b", arg.value)
                for arg in node.args
            ):
                issues.append((node.lineno, "dynamic legacy package reference"))
    for start, end, replacement in sorted(replacements, reverse=True):
        data = data[:start] + replacement + data[end:]
    rewritten = data.decode("utf-8")
    ast.parse(rewritten, filename=str(path))
    return rewritten, sorted(issues)


def generate_functions(source_dir=None, output_dir=None, class_dir=None):
    """Copy the complete function tree and return unresolved legacy references."""
    root = Path(MAIN_DIR)
    source_dir = Path(source_dir) if source_dir is not None else root / "Functions"
    output_dir = Path(output_dir) if output_dir is not None else root / "Functions_new"
    class_dir = Path(class_dir) if class_dir is not None else root / "Classes_new"
    for directory in (source_dir, class_dir):
        if not directory.is_dir():
            raise FileNotFoundError(f"Required directory does not exist: {directory}")
    if (
        source_dir.resolve() == output_dir.resolve()
        or source_dir.resolve() in output_dir.resolve().parents
        or output_dir.resolve() in source_dir.resolve().parents
    ):
        raise ValueError("Source and output function trees must be separate")

    issues = []
    for path in sorted(source_dir.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        relative = path.relative_to(source_dir)
        destination = output_dir / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        if path.suffix == ".py":
            with tokenize.open(path) as source_file:
                source = source_file.read()
                encoding = source_file.encoding
            if relative == Path("Load") / "retrocompatibility.py":
                source = _adapt_retrocompatibility(source, path)
            source = _redirect_function_errors(source, path, relative, class_dir)
            package = ".".join(["pyleecan", "Functions", *relative.parts[:-1]])
            source = _redirect_shared_error_imports(source, package)
            rewritten, found = _rewrite_source(source, path, relative, class_dir)
            if relative in (
                Path("Converter") / "Utils" / "ConvertionError.py",
                Path("Converter") / "Utils" / "EquivalentError.py",
            ):
                body = ast.parse(rewritten).body
                if body:
                    raise ValueError(f"{path}: error-only module contains other code")
                if destination.exists():
                    with tokenize.open(destination) as existing:
                        existing_tree = ast.parse(existing.read(), filename=str(destination))
                    if any(
                        not isinstance(node, ast.ImportFrom)
                        or node.module != "pyleecan.Classes_new._error"
                        for node in existing_tree.body
                    ):
                        raise ValueError(f"{destination}: refusing to remove modified module")
                    destination.unlink()
                continue
            destination.write_text(rewritten, encoding=encoding, newline="")
            issues.extend((relative, line, message) for line, message in found)
        else:
            shutil.copy2(path, destination)
    return issues


def main():
    issues = generate_functions()
    print("Copied Functions to Functions_new; existing copies were overwritten.")
    if issues:
        print("Legacy references requiring manual review:")
        for path, line, message in issues:
            print(f"  {path}:{line}: {message}")


if __name__ == "__main__":
    main()
