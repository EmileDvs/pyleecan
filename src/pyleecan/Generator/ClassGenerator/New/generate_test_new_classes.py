"""Copy the test suite with class and function imports targeting new packages.

Run ``python -m pyleecan.Generator.ClassGenerator.New.generate_test_new_classes``
to overwrite the copied tests in Tests/New, except the independently maintained
Classes/test_classes.py and Classes/test_loggers.py. Data remains in
Tests/Data, and copied tests use Tests/New/Results for the usual result paths.
Unaliased ``import pyleecan.Functions...`` imports require manual review,
as do legacy-only imports and dynamic loading.
Running copied tests still imports Tests/__init__.py, which clears Tests/Results.

The copied tests import the classes and functions from the alias packages
``backend_classes`` and ``backend_functions``, mapped by ``pytest --backend``
to Classes_new/Functions_new (dataclass) or Classes_pydantic/Functions_pydantic
(pydantic), see Tests/New/_backend.py.
"""

import ast
import re
import shutil
import tokenize
from pathlib import Path

from pyleecan.definitions import TEST_DIR
from pyleecan.classes_common.class_lookup import NORMALIZATION_CLASS_NAMES
from pyleecan.Generator.ClassGenerator.New.class_generator import (
    SHARED_SUPPORT_MODULES,
    VENDORED_CLASS_PACKAGES,
    _keyword_geometry_calls,
    class_module_name,
    generated_module_paths,
    relocate_class_imports,
)
from pyleecan.Generator.ClassGenerator.New.function_module_names import (
    function_module_mapping,
    redirect_function_module_imports,
)
from pyleecan.Generator.ClassGenerator.New.generate_function_new_classes import (
    _class_gen_dict,
    _redirect_shared_error_imports,
)

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
PRESERVED_TESTS = {
    Path("Classes") / "test_classes.py",
    Path("Classes") / "test_loggers.py",
}
RESULT_NAMES = {
    "save_path",
    "save_plot_path",
    "save_validation_path",
    "save_load_path",
    "save_gui_path",
    "SCHEMATICS_PATH",
    "SCHEMATICS_POINT_PATH",
}


BACKEND_ALIASES = {
    "pyleecan.Classes_new": "backend_classes",
    "pyleecan.Functions_new": "backend_functions",
}
"""Package of the dataclass implementation -> alias package of the tested one"""


def alias_backend_imports(source):
    """Import the classes and functions of the tested implementation (aliases).

    ``pyleecan.Classes_new.x`` becomes ``backend_classes.x`` and
    ``pyleecan.Functions_new.x`` becomes ``backend_functions.x``, in imports and
    in string constants (e.g. ``mock.patch`` targets). The vendored code and
    the shared support (classes_common) are not aliased.
    """

    def alias(module):
        for package, alias_package in BACKEND_ALIASES.items():
            if module == package or module.startswith(package + "."):
                rest = module[len(package) :]
                if rest.lstrip(".").partition(".")[0] in VENDORED_CLASS_PACKAGES:
                    return None
                return alias_package + rest
        return None

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == 10:  # "\n"
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.ImportFrom) and not node.level and node.module:
            new_module = alias(node.module)
            if new_module is None:
                continue
            replacement = ast.unparse(
                ast.ImportFrom(module=new_module, names=node.names, level=0)
            )
        elif isinstance(node, ast.Import):
            if not any(alias(name.name) for name in node.names if name.asname):
                continue
            replacement = ast.unparse(
                ast.Import(
                    names=[
                        ast.alias(
                            (alias(name.name) if name.asname else None) or name.name,
                            name.asname,
                        )
                        for name in node.names
                    ]
                )
            )
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            new_value = alias(node.value)
            if new_value is None:
                continue
            replacement = repr(new_value)
        else:
            continue
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, replacement.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _rewrite_source(source, path, class_dir):
    """Rewrite imports without modifying unrelated code, comments or strings."""
    source = _redirect_shared_error_imports(source, "Tests")
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
            is_vendored = class_name.split(".")[0] in VENDORED_CLASS_PACKAGES
            if "." in class_name and not is_vendored:
                unsupported.append((node.lineno, node.module))
                continue
            module_name = (
                class_name
                if is_vendored or class_name.startswith("_")
                else class_module_name(class_name)
            )
            module_path = class_dir.joinpath(*module_name.split("."))
            if (
                module_name not in generated_module_paths(class_dir)
                and module_name not in SHARED_SUPPORT_MODULES
                and not module_path.with_suffix(".py").is_file()
                and not (module_path / "__init__.py").is_file()
            ):
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
    rewritten = redirect_function_module_imports(
        rewritten, "Tests.New", function_module_mapping()
    )
    # The pydantic models (Geometry) only accept keyword arguments
    rewritten = _keyword_geometry_calls(rewritten, "pyleecan", _class_gen_dict())
    ast.parse(rewritten, filename=str(path))
    return rewritten, unsupported


def generate_tests(tests_dir=None, class_dir=None):
    """Copy the selected test trees and return unresolved legacy imports."""
    tests_dir = Path(tests_dir) if tests_dir is not None else Path(TEST_DIR)
    class_dir = (
        Path(class_dir)
        if class_dir is not None
        else tests_dir.parent / "src" / "pyleecan" / "Classes_new"
    )
    if not class_dir.is_dir():
        raise FileNotFoundError(f"Classes_new directory does not exist: {class_dir}")
    generated_module_paths.cache_clear()
    class_module_paths = generated_module_paths(class_dir)
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
                or path.relative_to(tests_dir) in PRESERVED_TESTS
            ):
                continue
            destination = output / path.relative_to(tests_dir)
            destination.parent.mkdir(parents=True, exist_ok=True)
            if path.suffix == ".py":
                with tokenize.open(path) as source_file:
                    source = source_file.read()
                    encoding = source_file.encoding
                rewritten, issues = _rewrite_source(source, path, class_dir)
                # Class modules are in sub-packages of Classes_new
                rewritten = relocate_class_imports(
                    rewritten, "pyleecan", "Classes_new", class_module_paths
                )
                # Classes and functions of the implementation under test
                rewritten = alias_backend_imports(rewritten)
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
    print(
        "Copied test trees to Tests/New; independently maintained tests were preserved."
    )
    if issues:
        print("Legacy imports requiring manual review:")
        for path, line, module in issues:
            print(f"  {path}:{line}: {module}")
    print("Dynamic class loading and legacy-generator tests require manual review.")
    print("Warning: importing Tests still clears the original Tests/Results folder.")


if __name__ == "__main__":
    main()
