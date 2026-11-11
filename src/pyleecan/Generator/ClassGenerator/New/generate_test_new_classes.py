"""Copy the test suite with class and function imports targeting new packages.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_test_new_classes``
to overwrite the copied tests in Tests/New. Data remains in
Tests/Data, and copied tests use Tests/New/Results for the usual result paths.
Unaliased ``import pyleecan.Functions...`` imports require manual review,
as do legacy-only imports and dynamic loading.
Running copied tests still imports Tests/__init__.py, which clears Tests/Results.
"""

import ast
import re
import shutil
import tokenize
from pathlib import Path

from pyleecan.definitions import TEST_DIR
from pyleecan.Functions.Load.retrocompatibility import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import class_module_name

TEST_FOLDERS = (
    "Classes",
    "Functions",
    "GUI",
    "Methods",
    "Plot",
    "Simulation",
    "Tutorials",
    "Validation",
)
RESULT_NAMES = {
    "save_path",
    "save_plot_path",
    "save_validation_path",
    "save_load_path",
    "save_gui_path",
    "SCHEMATICS_PATH",
    "SCHEMATICS_POINT_PATH",
}


def _rewrite_source(source, path, class_dir):
    """Rewrite imports without modifying unrelated code, comments or strings."""
    tree = ast.parse(source, filename=str(path))
    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == 10:
            offsets.append(index + 1)

    def offset(line, column):
        return offsets[line - 1] + column

    replacements = []
    unsupported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name == "pyleecan.Functions" or alias.name.startswith(
                    "pyleecan.Functions."
                ):
                    if alias.asname is None:
                        unsupported.append((node.lineno, alias.name))
                        continue
                    start = offset(alias.lineno, alias.col_offset)
                    end = start + len(alias.name.encode("utf-8"))
                    replacement = alias.name.replace(
                        "pyleecan.Functions", "pyleecan.Functions_new", 1
                    )
                    replacements.append((start, end, replacement.encode("utf-8")))
            continue
        if not isinstance(node, ast.ImportFrom) or node.level or not node.module:
            continue
        start = offset(node.lineno, node.col_offset)
        end = offset(node.end_lineno, node.end_col_offset)
        if node.module.startswith("pyleecan.Classes."):
            class_name = node.module.removeprefix("pyleecan.Classes.")
            if "." in class_name:
                unsupported.append((node.lineno, node.module))
                continue
            module_name = (
                class_name
                if class_name.startswith("_")
                else class_module_name(class_name)
            )
            if not (class_dir / (module_name + ".py")).is_file():
                unsupported.append((node.lineno, node.module))
                continue
            module_bytes = node.module.encode("utf-8")
            segment = encoded[start:end]
            match = re.search(
                rb"\bfrom\s+" + re.escape(module_bytes) + rb"\s+import\b", segment
            )
            if match is None:
                raise ValueError(f"{path}:{node.lineno}: cannot locate import module")
            module_start = start + match.start() + match.group().find(module_bytes)
            replacements.append(
                (
                    module_start,
                    module_start + len(module_bytes),
                    f"pyleecan.Classes_new.{module_name}".encode(),
                )
            )
            for alias in node.names:
                renamed = NORMALIZATION_CLASS_NAMES.get(alias.name)
                if renamed:
                    alias_start = offset(alias.lineno, alias.col_offset)
                    alias_end = offset(alias.end_lineno, alias.end_col_offset)
                    replacement = renamed + " as " + (alias.asname or alias.name)
                    replacements.append(
                        (alias_start, alias_end, replacement.encode("utf-8"))
                    )
        elif node.module == "pyleecan":
            for alias in node.names:
                if alias.name == "Functions":
                    alias_start = offset(alias.lineno, alias.col_offset)
                    alias_end = offset(alias.end_lineno, alias.end_col_offset)
                    replacement = "Functions_new as " + (alias.asname or "Functions")
                    replacements.append(
                        (alias_start, alias_end, replacement.encode("utf-8"))
                    )
        elif node.module == "pyleecan.Functions" or node.module.startswith(
            "pyleecan.Functions."
        ):
            module_bytes = node.module.encode("utf-8")
            segment = encoded[start:end]
            match = re.search(
                rb"\bfrom\s+" + re.escape(module_bytes) + rb"\s+import\b", segment
            )
            if match is None:
                raise ValueError(f"{path}:{node.lineno}: cannot locate import module")
            module_start = start + match.start() + match.group().find(module_bytes)
            new_module = node.module.replace(
                "pyleecan.Functions", "pyleecan.Functions_new", 1
            )
            replacements.append(
                (
                    module_start,
                    module_start + len(module_bytes),
                    new_module.encode("utf-8"),
                )
            )
        elif node.module == "Tests":
            result_aliases = [
                alias for alias in node.names if alias.name in RESULT_NAMES
            ]
            if not result_aliases:
                continue
            other_aliases = [
                alias for alias in node.names if alias.name not in RESULT_NAMES
            ]
            imports = []
            if other_aliases:
                imports.append(
                    ast.unparse(
                        ast.ImportFrom(module="Tests", names=other_aliases, level=0)
                    )
                )
            imports.append(
                ast.unparse(
                    ast.ImportFrom(
                        module="Tests.New._test_paths", names=result_aliases, level=0
                    )
                )
            )
            replacement = ("\n" + " " * node.col_offset).join(imports)
            replacements.append((start, end, replacement.encode("utf-8")))
        elif node.module.split(".")[:2] in [
            ["Tests", folder] for folder in TEST_FOLDERS
        ]:
            segment = encoded[start:end]
            old = node.module.encode("utf-8")
            match = re.search(rb"\bfrom\s+" + re.escape(old) + rb"\s+import\b", segment)
            if match is None:
                raise ValueError(f"{path}:{node.lineno}: cannot locate test import")
            module_start = start + match.start() + match.group().find(old)
            new = "Tests.New." + node.module[len("Tests.") :]
            replacements.append(
                (module_start, module_start + len(old), new.encode("utf-8"))
            )

    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    rewritten = encoded.decode("utf-8")
    ast.parse(rewritten, filename=str(path))
    return rewritten, unsupported


def generate_tests(tests_dir=None, class_dir=None):
    """Copy the selected test trees and return unresolved legacy imports."""
    tests_dir = (
        Path(tests_dir)
        if tests_dir is not None
        else Path(TEST_DIR)
    )
    class_dir = (
        Path(class_dir)
        if class_dir is not None
        else tests_dir.parent / "src" / "pyleecan" / "Classes_new"
    )
    if not class_dir.is_dir():
        raise FileNotFoundError(f"Classes_new directory does not exist: {class_dir}")
    output = tests_dir / "New"
    unsupported = []
    for folder in TEST_FOLDERS:
        source_dir = tests_dir / folder
        if not source_dir.is_dir():
            raise FileNotFoundError(f"Test directory does not exist: {source_dir}")
        for path in sorted(source_dir.rglob("*")):
            if (
                not path.is_file()
                or "__pycache__" in path.parts
                or path.suffix == ".pyc"
            ):
                continue
            destination = output / path.relative_to(tests_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == ".py":
                with tokenize.open(path) as source_file:
                    source = source_file.read()
                    encoding = source_file.encoding
                rewritten, issues = _rewrite_source(source, path, class_dir)
                destination.write_text(rewritten, encoding=encoding, newline="")
                unsupported.extend(
                    (path.relative_to(tests_dir), line, module)
                    for line, module in issues
                )
            else:
                shutil.copy2(path, destination)
    return unsupported


def main():
    issues = generate_tests()
    print("Copied test trees to Tests/New; existing copies were overwritten.")
    if issues:
        print("Legacy imports requiring manual review:")
        for path, line, module in issues:
            print(f"  {path}:{line}: {module}")
    print("Dynamic class loading and legacy-generator tests require manual review.")
    print("Warning: importing Tests still clears the original Tests/Results folder.")


if __name__ == "__main__":
    main()
