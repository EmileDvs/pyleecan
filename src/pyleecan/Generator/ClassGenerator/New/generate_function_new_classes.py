"""Generate Functions_new from Functions without modifying the legacy package.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_function_new_classes``
after generating Classes_new. Existing generated copies are overwritten. Legacy
load/save compatibility and unsupported dynamic imports are reported for review.
"""

import ast
import re
import shutil
import tokenize
from importlib.util import resolve_name
from pathlib import Path

from pyleecan.definitions import MAIN_DIR
from pyleecan.Functions.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import class_module_name


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
                if (
                    module == "pyleecan.Classes"
                    or "." in name
                    or name.startswith("_")
                    or not (class_dir / (class_module_name(name) + ".py")).is_file()
                    or any(alias.name == "*" for alias in node.names)
                ):
                    issues.append((node.lineno, f"legacy import: {module}"))
                    continue
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
            rewritten, found = _rewrite_source(source, path, relative, class_dir)
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
