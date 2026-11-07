import ast
import builtins
import re
import subprocess
import tempfile
import warnings
from keyword import iskeyword
from os.path import basename, dirname, isfile, join
from textwrap import indent

from ...Generator import PYTHON_TYPE, TAB
from ...Generator.ClassGenerator.as_dict_method_generator import generate_as_dict
from ...Generator.ClassGenerator.compare_method_generator import generate_compare
from ...Generator.ClassGenerator.copy_method_generator import generate_copy
from ...Generator.ClassGenerator.eq_method_generator import generate_eq
from ...Generator.ClassGenerator.import_method_generator import import_method
from ...Generator.ClassGenerator.init_method_generator import generate_init
from ...Generator.ClassGenerator.init_void_method_generator import generate_init_void
from ...Generator.ClassGenerator.properties_generator import generate_properties
from ...Generator.ClassGenerator.set_None_method_generator import generate_set_None
from ...Generator.ClassGenerator.size_of_method_generator import generate_size_of
from ...Generator.ClassGenerator.str_method_generator import generate_str
from ...Generator.read_fct import (
    find_import_type,
    get_value_str,
    is_dict_list_pyleecan_type,
    is_dict_pyleecan_type,
    is_list_pyleecan_type,
)

CLASS_ERROR_NAMES = {"NotImplementedYetError", "ParentMissingError"}


def class_module_name(class_name):
    """Convert a class name to a Python module name, keeping acronyms together."""
    name = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", class_name)
    name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
    name = re.sub(r"([A-Za-z])([0-9])", r"\1_\2", name).lower()
    if iskeyword(name):
        name += "_"
    if not name.isidentifier():
        raise ValueError(f"Cannot derive a Python module name from {class_name!r}")
    return name


def validate_class_module_names(gen_dict):
    """Reject ambiguous experimental output names before writing any classes."""
    modules = {}
    for class_name in gen_dict:
        module = class_module_name(class_name)
        if module in modules:
            raise ValueError(
                f"Classes {modules[module]!r} and {class_name!r} "
                f"both map to module {module!r}"
            )
        modules[module] = class_name


METHOD_IMPORT_REDIRECTS = {
    ("Methods.Machine", "ARC_NPOINT_D"): "Machine",
    ("Methods.Machine", "LINE_NPOINT_D"): "Machine",
    ("Methods.Machine.Skew", "TYPE_SKEW_LIST"): "Skew",
    ("Methods.Elmer.Section", "File"): "Section",
    ("Methods.Elmer.Section", "Variable"): "Section",
    ("Methods.Elmer.Section", "MATC"): "Section",
    ("Methods.Elmer.Section.write", "INDENT"): "SolverInputFile",
    ("Methods.Elmer.SolverInputFile.write", "INDENT"): "SolverInputFile",
    ("Methods.Simulation.Input", "CURRENT_DIR_REF"): "Input",
    ("Methods.Simulation.Input", "ROT_DIR_REF"): "Input",
    ("Methods.Simulation.Input", "PHASE_DIR_REF"): "Input",
}
CLASS_MODULE_CONSTANTS = {
    "Machine": {"ARC_NPOINT_D": 99, "LINE_NPOINT_D": 1},
    "Skew": {
        "TYPE_SKEW_LIST": ["linear", "vshape", "zig-zag", "user-defined", "function"]
    },
    "Input": {
        "ROT_DIR_REF": -1,
        "CURRENT_DIR_REF": -1,
        "PHASE_DIR_REF": -1,
    },
}
CLASS_MODULE_CONSTANT_EXPRESSIONS = {
    "SolverInputFile": {
        "WHITESPACE": repr(" "),
        "INDENT": "2 * WHITESPACE",
    }
}
CLASS_BODY_CONSTANTS = {
    "SolverInputFile": {
        "WHITESPACE": repr(" "),
        "COMMENT": repr("! "),
        "NEWLINE": repr("\n"),
        "END": repr("End"),
        "MESH_FILE": repr("Mesh"),
    }
}
CLASS_METHOD_HELPERS = {
    "XOutput": {
        "_get_symbol_data_": ("Output.XOutput", "_get_symbol_data_"),
    },
    "DataDual": {
        "is_freq": ("SciDataTool.DataDual", "is_freq"),
    },
    "MagElmer": {
        "_get_BP_dict": ("Simulation.MagElmer", "_get_BP_dict"),
    },
    "StructElmer": {
        "_get_BP_dict": ("Simulation.StructElmer", "_get_BP_dict"),
        "_execute": ("Simulation.StructElmer", "_execute"),
    },
}
CLASS_STATIC_METHOD_HELPERS = {
    "DataDual": {"is_freq"},
    "MagElmer": {"_get_BP_dict"},
    "StructElmer": {"_get_BP_dict", "_execute"},
}
CLASS_MODULE_CLASS_DEFINITIONS = {
    "Section": ("Elmer.Section", ("File", "Variable", "MATC")),
    "StructElmer": ("Simulation.StructElmer", ("ElmerProcessError",)),
}
METHOD_CALL_REDIRECTS = {
    ("OptiGenAlgNsga2Deap", "Methods.Output.XOutput", "_get_symbol_data_"): (
        "self.xoutput",
        "_get_symbol_data_",
    ),
    ("MeshMat", "Methods.Mesh.MeshMat.get_element", "_check_element_name"): (
        None,
        "_check_element_name",
    ),
}
CONFIGURED_PLOT_CONSTANT_NAMES = {
    "PATCH_COLOR_ALPHA",
    "PATCH_EDGE",
    "PATCH_EDGE_ALPHA",
    "PHASE_COLORS",
    "COLORS",
    "COLORMAP",
    "COLOR_MAP",
    "FONT_NAME",
    "FONT_SIZE_TITLE",
    "FONT_SIZE_LABEL",
    "FONT_SIZE_LEGEND",
    "FONT_FAMILY_PYVISTA",
}


def _load_method_error_module(path_to_gen, module_name):
    """Load a Methods module or package initializer for error-class lookup."""
    module_parts = module_name.split(".")
    if len(module_parts) < 2 or module_parts[1] != "Methods":
        return None, None
    methods_path = join(dirname(path_to_gen), *module_parts[1:])
    module_path = methods_path + ".py"
    package_parts = module_parts[:-1]
    if not isfile(module_path):
        module_path = join(methods_path, "__init__.py")
        package_parts = module_parts
    try:
        with open(module_path, encoding="utf-8") as source_file:
            return ast.parse(source_file.read(), filename=module_path), package_parts
    except FileNotFoundError:
        return None, None


def _get_exception_classes(module):
    """Return exception classes declared directly in a module."""
    classes = {
        node.name: node for node in module.body if isinstance(node, ast.ClassDef)
    }

    def is_exception_class(node, visited=()):
        if node.name in visited:
            return False
        for base in node.bases:
            base_name = (
                base.id
                if isinstance(base, ast.Name)
                else base.attr
                if isinstance(base, ast.Attribute)
                else None
            )
            if base_name in {"Exception", "BaseException"} or (
                base_name is not None and "Error" in base_name
            ):
                return True
            if base_name in classes and is_exception_class(
                classes[base_name], visited + (node.name,)
            ):
                return True
        return False

    return {name: node for name, node in classes.items() if is_exception_class(node)}


def _get_error_class_fingerprint(path_to_gen, module_name, class_name, visited=()):
    """Return the definition of an exported exception class, if available."""
    if module_name in visited:
        return None
    module, package_parts = _load_method_error_module(path_to_gen, module_name)
    if module is None:
        return None
    class_node = _get_exception_classes(module).get(class_name)
    if class_node is not None:
        return ast.dump(class_node, include_attributes=False)

    for node in module.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        for alias in node.names:
            if (alias.asname or alias.name) != class_name or alias.name == "*":
                continue
            imported_module = ".".join(_get_absolute_import_module(node, package_parts))
            return _get_error_class_fingerprint(
                path_to_gen,
                imported_module,
                alias.name,
                visited + (module_name,),
            )
    return None


def _get_error_class_definitions(path_to_gen, module_name, class_name, visited=()):
    """Return exception definitions and their exception bases in dependency order."""
    if module_name in visited:
        return []
    module, package_parts = _load_method_error_module(path_to_gen, module_name)
    if module is None:
        return []

    classes = {
        node.name: node for node in module.body if isinstance(node, ast.ClassDef)
    }
    imports = {}
    for node in module.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        imported_module = ".".join(_get_absolute_import_module(node, package_parts))
        for alias in node.names:
            if alias.name != "*":
                imports[alias.asname or alias.name] = (imported_module, alias.name)

    class_node = classes.get(class_name)
    if class_node is None:
        imported = imports.get(class_name)
        if imported is None:
            return []
        return _get_error_class_definitions(
            path_to_gen, imported[0], imported[1], visited + (module_name,)
        )
    if class_name not in _get_exception_classes(module):
        return []

    dependencies = []
    for base in class_node.bases:
        if not isinstance(base, ast.Name):
            continue
        if base.id in classes:
            dependencies.extend(
                _get_error_class_definitions(path_to_gen, module_name, base.id, visited)
            )
        elif base.id in imports:
            imported_module, imported_name = imports[base.id]
            dependencies.extend(
                _get_error_class_definitions(
                    path_to_gen,
                    imported_module,
                    imported_name,
                    visited + (module_name,),
                )
            )

    definition = ast.parse(ast.unparse(class_node)).body[0]
    definitions = []
    seen = set()
    for dependency in dependencies + [definition]:
        existing = next(
            (node for node in definitions if node.name == dependency.name),
            None,
        )
        if existing is not None:
            if ast.dump(existing, include_attributes=False) != ast.dump(
                dependency, include_attributes=False
            ):
                return []
            continue
        if dependency.name not in seen:
            definitions.append(dependency)
            seen.add(dependency.name)
    return definitions


def _same_error_class_import(path_to_gen, first_identity, second_identity):
    """Check whether two imports refer to identically defined exception classes."""
    if (
        first_identity[0] != "ImportFrom"
        or second_identity[0] != "ImportFrom"
        or first_identity[3] != second_identity[3]
        or first_identity[4] != second_identity[4]
    ):
        return False
    first_fingerprint = _get_error_class_fingerprint(
        path_to_gen, first_identity[2], first_identity[3]
    )
    return first_fingerprint is not None and first_fingerprint == (
        _get_error_class_fingerprint(
            path_to_gen, second_identity[2], second_identity[3]
        )
    )


def _rename_method_references(source, renamed_names):
    """Rename Python name references without changing comments or string literals."""
    if not renamed_names:
        return source
    tree = ast.parse(source)
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Name) or node.id not in renamed_names:
            continue
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = start + len(node.id.encode("utf-8"))
        replacements.append((start, end, renamed_names[node.id].encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _replace_empty_containers(source, blocked_names=()):
    """Replace unshadowed empty built-in container calls in an inlined method."""
    tree = ast.parse(source)
    blocked = set(blocked_names)
    candidates = {"dict", "list"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            blocked.add(node.id)
        elif isinstance(node, ast.arg):
            blocked.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            blocked.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            blocked.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            blocked.update(node.names)
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for alias in node.names:
                if alias.name == "*":
                    blocked.update(candidates)
                else:
                    blocked.add(
                        alias.asname
                        or (
                            alias.name.split(".")[0]
                            if isinstance(node, ast.Import)
                            else alias.name
                        )
                    )
        elif isinstance(node, ast.MatchAs) and node.name:
            blocked.add(node.name)
        elif isinstance(node, ast.MatchStar) and node.name:
            blocked.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            blocked.add(node.rest)

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)
    replacements = []
    for node in ast.walk(tree):
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in candidates - blocked
            and not node.args
            and not node.keywords
        ):
            start = offsets[node.lineno - 1] + node.col_offset
            end = offsets[node.end_lineno - 1] + node.end_col_offset
            # Preserve comments inside multiline calls.
            if b"#" not in encoded[start:end]:
                replacements.append(
                    (start, end, b"{}" if node.func.id == "dict" else b"[]")
                )
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8")


def _replace_dynamic_class_imports(source, soft_name, blocked_names=()):
    """Replace recognized module-and-class import pairs in inlined methods."""
    if set(blocked_names).intersection(
        {"__import__", "getattr", "_pyleecan_import_class", "*"}
    ):
        return source, False
    tree = ast.parse(source)
    if any(
        (isinstance(node, ast.Name) and node.id in {"__import__", "getattr"}
         and isinstance(node.ctx, (ast.Store, ast.Del)))
        or (isinstance(node, ast.arg) and node.arg in {"__import__", "getattr"})
        for node in ast.walk(tree)
    ):
        return source, False
    names = {node.id for node in ast.walk(tree) if isinstance(node, ast.Name)}
    names.update(node.arg for node in ast.walk(tree) if isinstance(node, ast.arg))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            bindings = {
                alias.asname
                or (
                    alias.name.split(".")[0]
                    if isinstance(node, ast.Import)
                    else alias.name
                )
                for alias in node.names
            }
            if bindings.intersection({"__import__", "getattr", "*"}):
                return source, False
            names.update(bindings)
    if "_pyleecan_import_class" in names:
        return source, False

    encoded = source.encode("utf-8")
    offsets = [0]
    for index, value in enumerate(encoded):
        if value == ord("\n"):
            offsets.append(index + 1)

    matches = []
    for parent in ast.walk(tree):
        for _, statements in ast.iter_fields(parent):
            if not isinstance(statements, list):
                continue
            for first, second in zip(statements, statements[1:]):
                if not (
                    isinstance(first, ast.Assign)
                    and len(first.targets) == 1
                    and isinstance(first.targets[0], ast.Name)
                    and isinstance(first.value, ast.Call)
                    and isinstance(first.value.func, ast.Name)
                    and first.value.func.id == "__import__"
                    and len(first.value.args) == 1
                    and len(first.value.keywords) == 1
                    and first.value.keywords[0].arg == "fromlist"
                    and isinstance(first.value.keywords[0].value, (ast.List, ast.Tuple))
                    and len(first.value.keywords[0].value.elts) == 1
                    and isinstance(second, ast.Assign)
                    and len(second.targets) == 1
                    and isinstance(second.targets[0], ast.Name)
                    and first.end_lineno + 1 == second.lineno
                ):
                    continue
                class_expr = first.value.keywords[0].value.elts[0]
                module_expr = first.value.args[0]
                module_name = first.targets[0].id
                value = second.value
                if isinstance(value, ast.Attribute) and (
                    isinstance(value.value, ast.Name)
                    and value.value.id == module_name
                    and isinstance(class_expr, ast.Constant)
                    and value.attr == class_expr.value
                ):
                    module_ref = value.value
                elif (
                    isinstance(value, ast.Call)
                    and isinstance(value.func, ast.Name)
                    and value.func.id == "getattr"
                    and len(value.args) == 2
                    and not value.keywords
                    and isinstance(value.args[0], ast.Name)
                    and value.args[0].id == module_name
                    and ast.dump(value.args[1]) == ast.dump(class_expr)
                ):
                    module_ref = value.args[0]
                else:
                    continue

                package_expr = None
                if isinstance(class_expr, ast.Constant) and isinstance(
                    class_expr.value, str
                ):
                    suffix = ".Classes." + class_expr.value
                    if isinstance(module_expr, ast.Constant) and isinstance(
                        module_expr.value, str
                    ) and module_expr.value == soft_name + suffix:
                        package_expr = repr(soft_name + ".Classes")
                    elif (
                        isinstance(module_expr, ast.BinOp)
                        and isinstance(module_expr.op, ast.Add)
                        and isinstance(module_expr.left, ast.Name)
                        and module_expr.left.id == "PACKAGE_NAME"
                        and isinstance(module_expr.right, ast.Constant)
                        and module_expr.right.value == suffix
                    ):
                        package_expr = 'PACKAGE_NAME + ".Classes"'
                elif (
                    isinstance(class_expr, ast.Name)
                    and isinstance(module_expr, ast.BinOp)
                    and isinstance(module_expr.op, ast.Add)
                    and isinstance(module_expr.left, ast.Constant)
                    and module_expr.left.value == soft_name + ".Classes."
                    and ast.dump(module_expr.right) == ast.dump(class_expr)
                ):
                    package_expr = repr(soft_name + ".Classes")
                if package_expr is None:
                    continue
                first_end = offsets[first.end_lineno - 1] + first.end_col_offset
                first_start = offsets[first.lineno - 1] + first.col_offset
                line_end = encoded.find(b"\n", first_end)
                if (
                    line_end < 0
                    or encoded[first_end:line_end].strip()
                    or b"#" in encoded[first_start:first_end]
                ):
                    continue
                matches.append((first, second, module_ref, package_expr, class_expr))

    safe_refs = {id(item[2]) for item in matches}
    unsafe_modules = {
        node.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Name)
        and isinstance(node.ctx, ast.Load)
        and node.id in {item[0].targets[0].id for item in matches}
        and id(node) not in safe_refs
    }
    replacements = []
    for first, second, _, package_expr, class_expr in matches:
        if first.targets[0].id in unsafe_modules:
            continue
        start = offsets[first.lineno - 1] + first.col_offset
        end = offsets[second.end_lineno - 1] + second.end_col_offset
        replacement = (
            f"{second.targets[0].id} = _pyleecan_import_class("
            f"{package_expr}, {ast.unparse(class_expr)})"
        )
        replacements.append((start, end, replacement.encode("utf-8")))
    for start, end, replacement in sorted(replacements, reverse=True):
        encoded = encoded[:start] + replacement + encoded[end:]
    return encoded.decode("utf-8"), bool(replacements)


def _rewrite_method_call_targets(source, call_redirects):
    """Redirect imported helper calls to methods on an existing object."""
    if not call_redirects:
        return source
    tree = ast.parse(source)
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in call_redirects
        ):
            continue
        receiver, method_name = call_redirects[node.func.id]
        function_start = line_offsets[node.func.lineno - 1] + node.func.col_offset
        function_end = function_start + len(node.func.id.encode("utf-8"))
        target = (
            "self." + method_name if receiver is None else receiver + "." + method_name
        )
        replacements.append((function_start, function_end, target.encode("utf-8")))
        if receiver is not None:
            if not node.args or ast.unparse(node.args[0]) != receiver:
                raise ValueError(
                    "Cannot redirect "
                    + node.func.id
                    + " call without its expected receiver "
                    + receiver
                )
            if len(node.args) < 2:
                raise ValueError(
                    "Cannot redirect "
                    + node.func.id
                    + " call without additional positional arguments"
                )
            first_argument_start = (
                line_offsets[node.args[0].lineno - 1] + node.args[0].col_offset
            )
            second_argument_start = (
                line_offsets[node.args[1].lineno - 1] + node.args[1].col_offset
            )
            replacements.append((first_argument_start, second_argument_start, b""))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _get_method_body_imports(method_node):
    """Collect static imports in a method body without entering nested scopes."""
    imports = []

    class ImportVisitor(ast.NodeVisitor):
        def visit_Import(self, node):
            imports.append(node)

        def visit_ImportFrom(self, node):
            imports.append(node)

        def visit_FunctionDef(self, node):
            return

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            return

    visitor = ImportVisitor()
    for statement in method_node.body:
        visitor.visit(statement)
    return imports


def _get_imported_class_modules(
    import_node, source_package, path_to_gen, soft_name, class_import_graph=None
):
    """Return generated class modules referenced by a static import."""
    imported_modules = []
    if isinstance(import_node, ast.Import):
        module_names = [alias.name.split(".") for alias in import_node.names]
    else:
        module_parts = _get_absolute_import_module(import_node, source_package)
        if module_parts[:2] != [soft_name, "Classes"]:
            return []
        if len(module_parts) > 2:
            module_names = [module_parts]
        else:
            module_names = [
                module_parts + alias.name.split(".")
                for alias in import_node.names
                if alias.name != "*"
            ]

    for module_parts in module_names:
        if module_parts[:2] != [soft_name, "Classes"] or len(module_parts) < 3:
            continue
        class_module = module_parts[2]
        if (
            class_module in class_import_graph
            if class_import_graph is not None
            else isfile(join(path_to_gen, class_module + ".py"))
        ):
            imported_modules.append(class_module)
    return imported_modules


def _class_module_imports(path_to_gen, class_module, soft_name):
    """Return top-level generated class imports for one class module."""
    class_path = join(path_to_gen, class_module + ".py")
    if not isfile(class_path):
        return []
    with open(class_path, encoding="utf-8") as class_file:
        class_tree = ast.parse(class_file.read())

    imports = []
    class_package = [soft_name, "Classes"]
    for node in class_tree.body:
        if isinstance(node, ast.Import) or isinstance(node, ast.ImportFrom):
            import_nodes = [node]
        else:
            continue
        for import_node in import_nodes:
            imports.extend(
                _get_imported_class_modules(
                    import_node, class_package, path_to_gen, soft_name
                )
            )
    return imports


def get_class_import_graph(path_to_gen, gen_dict, soft_name):
    """Snapshot generated class imports before class files are rewritten."""
    return {
        class_name: tuple(_class_module_imports(path_to_gen, class_name, soft_name))
        for class_name in gen_dict
        if isfile(join(path_to_gen, class_name + ".py"))
    }


def _would_create_class_import_cycle(
    import_node,
    source_package,
    path_to_gen,
    class_name,
    soft_name,
    class_import_graph=None,
):
    """Check whether hoisting an import would create a generated-class cycle."""
    pending = _get_imported_class_modules(
        import_node,
        source_package,
        path_to_gen,
        soft_name,
        class_import_graph=class_import_graph,
    )
    visited = set()
    while pending:
        class_module = pending.pop()
        if class_module == class_name:
            return True
        if class_module in visited:
            continue
        visited.add(class_module)
        if class_import_graph is None:
            pending.extend(_class_module_imports(path_to_gen, class_module, soft_name))
        else:
            pending.extend(class_import_graph.get(class_module, ()))
    return False


def _has_method_body_import_guard(source, import_node):
    """Keep imports explicitly marked as local circular-import guards."""
    source_lines = source.splitlines()
    line_index = import_node.lineno - 2
    while line_index >= 0:
        line = source_lines[line_index].strip().lower()
        if not line:
            return False
        if line.startswith("#"):
            return "circular" in line or "importerror" in line
        if (
            line.startswith("import ")
            or line.startswith("from ")
            or line in ("(", ")")
            or line.endswith(("(", ","))
        ):
            line_index -= 1
            continue
        return False
    return False


def _remove_method_body_imports(
    source, method_body_imports, method_start_line, method_node
):
    """Remove extracted static imports while retaining the surrounding source."""
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    extracted_imports = set(method_body_imports)
    imports_requiring_pass = set()
    for parent in ast.walk(method_node):
        for _, statements in ast.iter_fields(parent):
            if not isinstance(statements, list) or not all(
                isinstance(statement, ast.stmt) for statement in statements
            ):
                continue
            suite_imports = [
                statement for statement in statements if statement in extracted_imports
            ]
            if suite_imports and len(suite_imports) == len(statements):
                imports_requiring_pass.add(
                    min(suite_imports, key=lambda node: node.lineno)
                )

    replacements = []
    for node in method_body_imports:
        start_line = node.lineno - method_start_line
        end_line = node.end_lineno - method_start_line
        start = line_offsets[start_line] + node.col_offset
        end = line_offsets[end_line] + node.end_col_offset
        replacement = b"pass" if node in imports_requiring_pass else b""
        replacements.append((start, end, replacement))
    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _resolve_method_relative_imports(source, source_package):
    """Resolve relative imports retained inside a generated class method."""
    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        absolute_module = ".".join(_get_absolute_import_module(node, source_package))
        replacement = ast.unparse(
            ast.ImportFrom(
                module=absolute_module,
                names=node.names,
                level=0,
            )
        ).encode("utf-8")
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = line_offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, replacement))

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _expand_error_wildcard_imports(
    module, method_node, used_names, path_to_gen, source_package
):
    """Resolve wildcard imports whose used names are package exception classes."""
    method_local_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    method_local_names.update(
        argument.arg
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
    )
    module_bindings = set()
    wildcard_nodes = []
    for node in module.body:
        if isinstance(node, ast.Import):
            module_bindings.update(
                alias.asname or alias.name.split(".")[0] for alias in node.names
            )
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                wildcard_nodes.append(node)
            else:
                module_bindings.update(
                    alias.asname or alias.name for alias in node.names
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            module_bindings.add(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            module_bindings.update(
                child.id
                for target in targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
            )

    unresolved_names = (
        used_names - method_local_names - module_bindings - set(dir(builtins))
    )
    if not wildcard_nodes:
        return module.body, None

    providers = {}
    package_exports = {}
    for node in wildcard_nodes:
        module_parts = _get_absolute_import_module(node, source_package)
        if len(module_parts) < 3 or module_parts[1] != "Methods":
            return (
                None,
                "module uses a wildcard import whose names cannot be resolved safely",
            )
        init_path = join(dirname(path_to_gen), *module_parts[1:], "__init__.py")
        try:
            with open(init_path, encoding="utf-8") as init_file:
                package_module = ast.parse(init_file.read(), filename=init_path)
        except FileNotFoundError:
            return None, "wildcard import package initializer is missing"

        exception_classes = _get_exception_classes(package_module)
        error_fingerprints = {
            name: ast.dump(node, include_attributes=False)
            for name, node in exception_classes.items()
        }
        for statement in package_module.body:
            if isinstance(statement, ast.ImportFrom):
                for alias in statement.names:
                    name = alias.asname or alias.name
                    if alias.name != "*" and "Error" in name:
                        error_fingerprints[name] = _get_error_class_fingerprint(
                            path_to_gen, ".".join(module_parts), name
                        )
            elif isinstance(statement, ast.Import):
                for alias in statement.names:
                    name = alias.asname or alias.name.split(".")[0]
                    if "Error" in name:
                        error_fingerprints[name] = None
        package_name = ".".join(module_parts)
        package_exports[package_name] = error_fingerprints
        for name in unresolved_names.intersection(error_fingerprints):
            providers.setdefault(name, []).append(package_name)

    unresolved_names.difference_update(providers)
    if unresolved_names:
        return (
            None,
            "module uses a wildcard import whose names cannot be resolved safely",
        )

    imports_by_package = {}
    for name, package_names in providers.items():
        package_names = list(dict.fromkeys(package_names))
        canonical_package = package_names[0]
        canonical_fingerprint = package_exports[canonical_package].get(name)
        for package_name in package_names[1:]:
            candidate_fingerprint = package_exports[package_name].get(name)
            if (
                canonical_fingerprint is None
                or candidate_fingerprint is None
                or canonical_fingerprint != candidate_fingerprint
            ):
                return (
                    None,
                    "wildcard import name '"
                    + name
                    + "' refers to different class errors",
                )
        imports_by_package.setdefault(canonical_package, []).append(
            ast.alias(name=name)
        )

    replacement_nodes = []
    for package_name, aliases in imports_by_package.items():
        replacement_nodes.append(
            ast.ImportFrom(
                module=package_name,
                names=aliases,
                level=0,
            )
        )
    body = []
    inserted_imports = False
    for node in module.body:
        if node in wildcard_nodes:
            if not inserted_imports:
                body.extend(replacement_nodes)
                inserted_imports = True
        else:
            body.append(node)
    return body, None


def _get_method_source(
    path_to_gen,
    class_pack,
    class_name,
    meth,
    soft_name,
    hoist_names=(),
    class_import_graph=None,
):
    """Return a method definition and the imports it needs."""
    method_parts = [part for part in (class_pack or "").split(".") if part]
    method_parts.extend([class_name, *meth.split(".")])
    method_path = join(dirname(path_to_gen), "Methods", *method_parts) + ".py"

    try:
        with open(method_path, encoding="utf-8") as method_file:
            source = method_file.read()
    except FileNotFoundError:
        return None, [], [], [], "method source file is missing"

    module = ast.parse(source, filename=method_path)
    method_name = meth.split(".")[-1]
    method_node = next(
        (
            node
            for node in module.body
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
            and node.name == method_name
        ),
        None,
    )
    if method_node is None:
        return None, [], [], [], "method function is missing"
    if any(
        isinstance(node, ast.ImportFrom) and node.module == "__future__"
        for node in module.body
    ):
        return None, [], [], [], "module has a __future__ import"

    source_package = [
        soft_name,
        "Methods",
        *[part for part in (class_pack or "").split(".") if part],
        class_name,
        *meth.split(".")[:-1],
    ]
    used_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    helper_function_nodes = {
        node.name: node
        for node in module.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node is not method_node
        and not node.decorator_list
    }
    inline_helper_names = set()
    pending_helpers = list(used_names.intersection(helper_function_nodes))
    while pending_helpers:
        helper_name = pending_helpers.pop()
        if helper_name in inline_helper_names:
            continue
        inline_helper_names.add(helper_name)
        helper_used_names = {
            node.id
            for node in ast.walk(helper_function_nodes[helper_name])
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        used_names.update(helper_used_names)
        pending_helpers.extend(
            name
            for name in helper_used_names
            if name in helper_function_nodes and name not in inline_helper_names
        )
    module.body, wildcard_reason = _expand_error_wildcard_imports(
        module, method_node, used_names, path_to_gen, source_package
    )
    if wildcard_reason is not None:
        return None, [], [], [], wildcard_reason
    if any(isinstance(node, ast.Global) for node in ast.walk(method_node)):
        return None, [], [], [], "method declares module globals"

    signature_nodes = (
        method_node.decorator_list
        + method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        + [
            argument.annotation
            for argument in (
                method_node.args.posonlyargs
                + method_node.args.args
                + method_node.args.kwonlyargs
            )
            if argument.annotation is not None
        ]
    )
    if method_node.returns is not None:
        signature_nodes.append(method_node.returns)
    signature_names = {
        node.id
        for root_node in signature_nodes
        for node in ast.walk(root_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }

    helper_bindings = set()
    literal_defaults = {}
    has_module_helpers = False
    for node in module.body:
        if node is method_node or (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ):
            continue
        if isinstance(node, ast.Import):
            continue
        elif isinstance(node, ast.ImportFrom):
            if any(alias.name == "*" for alias in node.names):
                return (
                    None,
                    [],
                    [],
                    [],
                    "module uses a wildcard import whose names cannot be resolved safely",
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if node is method_node:
                continue
            helper_bindings.add(node.name)
            has_module_helpers = True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names = {
                child.id
                for target in targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
            }
            helper_bindings.update(names)
            if len(names) == 1 and len(targets) == 1:
                try:
                    ast.literal_eval(node.value)
                except ValueError, TypeError, SyntaxError:
                    pass
                else:
                    name = next(iter(names))
                    literal_defaults[name] = ast.unparse(node.value)
            has_module_helpers = True
        else:
            return (
                None,
                [],
                [],
                [],
                "module contains unsupported top-level "
                + type(node).__name__
                + " statements",
            )

    inline_literal_defaults = {
        name: value
        for name, value in literal_defaults.items()
        if name not in signature_names
        and name not in CLASS_BODY_CONSTANTS.get(class_name, {})
        and name not in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {})
    }
    method_local_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    method_local_names.update(
        argument.arg
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
    )
    module_assignments = {}
    for node in module.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        targets = node.targets if isinstance(node, ast.Assign) else [node.target]
        if len(targets) != 1 or not isinstance(targets[0], ast.Name):
            continue
        name = targets[0].id
        if name in literal_defaults:
            continue
        module_assignments[name] = node.value

    signature_non_defaults = method_node.decorator_list + [
        argument.annotation
        for argument in (
            method_node.args.posonlyargs
            + method_node.args.args
            + method_node.args.kwonlyargs
        )
        if argument.annotation is not None
    ]
    if method_node.returns is not None:
        signature_non_defaults.append(method_node.returns)
    signature_default_names = {
        node.id
        for default in method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        for node in ast.walk(default)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    direct_default_names = {
        default.id
        for default in method_node.args.defaults
        + [node for node in method_node.args.kw_defaults if node is not None]
        if isinstance(default, ast.Name)
    }
    signature_non_default_names = {
        node.id
        for root_node in signature_non_defaults
        for node in ast.walk(root_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    configured_assignment_names = {
        name
        for name in hoist_names.intersection(module_assignments)
        if any(
            isinstance(node, ast.Name) and node.id == "config_dict"
            for node in ast.walk(module_assignments[name])
        )
    }
    hoisted_names = {
        name
        for name in used_names.intersection(module_assignments, hoist_names)
        if name not in method_local_names
        and name not in signature_non_default_names
        and (name not in signature_default_names or name in direct_default_names)
    } | configured_assignment_names
    if hoisted_names and not method_node.args.args:
        return (
            None,
            [],
            [],
            [],
            "cannot hoist module assignments for a method without an instance argument",
        )

    class_attributes = [
        ast.fix_missing_locations(
            ast.Assign(
                targets=[ast.Name(id=name, ctx=ast.Store())],
                value=value,
            )
        )
        for name, value in module_assignments.items()
        if name in hoisted_names
    ]
    extra_used_names = {
        node.id
        for assignment in class_attributes
        for node in ast.walk(assignment.value)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    } - hoisted_names
    target_package = [soft_name, "Classes"]
    method_imports = []
    import_used_names = used_names | extra_used_names
    renamed_method_names = {}
    method_call_redirects = {}
    method_body_imports = [
        node
        for node in _get_method_body_imports(method_node)
        if not _has_method_body_import_guard(source, node)
        and not _would_create_class_import_cycle(
            node,
            source_package,
            path_to_gen,
            class_name,
            soft_name,
            class_import_graph=class_import_graph,
        )
    ]

    if has_module_helpers:
        helper_names = sorted(
            import_used_names.intersection(
                helper_bindings
                - inline_literal_defaults.keys()
                - hoisted_names
                - CLASS_BODY_CONSTANTS.get(class_name, {}).keys()
                - CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {}).keys()
            )
        )
        if helper_names:
            helper_module = source_package + [method_name]
            common = 0
            while (
                common < len(target_package)
                and common < len(helper_module)
                and target_package[common] == helper_module[common]
            ):
                common += 1
            imported_helpers = [
                ast.alias(name=name)
                for name in helper_names
                if name not in inline_helper_names
                and METHOD_IMPORT_REDIRECTS.get((".".join(helper_module[1:]), name))
                is None
            ]
            if imported_helpers:
                method_imports.append(
                    ast.ImportFrom(
                        module=".".join(helper_module[common:]),
                        names=imported_helpers,
                        level=len(target_package) - common + 1,
                    )
                )
            for name in helper_names:
                target_class = METHOD_IMPORT_REDIRECTS.get(
                    (".".join(helper_module[1:]), name)
                )
                if target_class is None:
                    continue
                if target_class != class_name:
                    method_imports.append(
                        ast.ImportFrom(
                            module=soft_name + ".Classes." + target_class,
                            names=[ast.alias(name=name)],
                            level=0,
                        )
                    )

    for node in module.body + method_body_imports:
        is_method_body_import = node in method_body_imports
        if isinstance(node, ast.Import):
            aliases = [
                alias
                for alias in node.names
                if is_method_body_import
                or (alias.asname or alias.name.split(".")[0]) in import_used_names
            ]
            if aliases:
                method_imports.append(ast.Import(names=aliases))
        elif isinstance(node, ast.ImportFrom):
            aliases = [
                alias
                for alias in node.names
                if is_method_body_import
                or alias.name == "*"
                or (alias.asname or alias.name) in import_used_names
            ]
            if not aliases:
                continue

            absolute_module_parts = _get_absolute_import_module(node, source_package)
            redirect_module = ".".join(
                absolute_module_parts[1:]
                if absolute_module_parts[:1] == [soft_name]
                else absolute_module_parts
            )
            redirected_aliases = {}
            for alias in aliases:
                method_call_redirect = METHOD_CALL_REDIRECTS.get(
                    (class_name, redirect_module, alias.name)
                )
                if method_call_redirect is not None:
                    method_call_redirects[alias.asname or alias.name] = (
                        method_call_redirect
                    )
                    continue
                target_class = METHOD_IMPORT_REDIRECTS.get(
                    (redirect_module, alias.name)
                )
                if target_class is not None:
                    target_module = soft_name + ".Classes." + target_class
                    redirected_aliases.setdefault(target_module, []).append(alias)
            for target_module, target_aliases in redirected_aliases.items():
                if target_module != soft_name + ".Classes." + class_name:
                    method_imports.append(
                        ast.ImportFrom(
                            module=target_module,
                            names=target_aliases,
                            level=0,
                        )
                    )
            aliases = [
                alias
                for alias in aliases
                if (redirect_module, alias.name) not in METHOD_IMPORT_REDIRECTS
                and (
                    class_name,
                    redirect_module,
                    alias.name,
                )
                not in METHOD_CALL_REDIRECTS
            ]
            if not aliases:
                continue

            if _get_absolute_import_module(node, source_package) == [
                soft_name,
                "Functions",
                "SciDataTool",
            ]:
                updated_aliases = []
                for alias in aliases:
                    if alias.name == "axes_dict":
                        updated_aliases.append(
                            ast.alias(name="axes_dict_transformation")
                        )
                        renamed_method_names["axes_dict"] = "axes_dict_transformation"
                    else:
                        updated_aliases.append(alias)
                aliases = updated_aliases

            if node.level:
                module_parts = source_package[: len(source_package) - node.level + 1]
                if node.module:
                    module_parts.extend(node.module.split("."))

                common = 0
                while (
                    common < len(target_package)
                    and common < len(module_parts)
                    and target_package[common] == module_parts[common]
                ):
                    common += 1
                node = ast.ImportFrom(
                    module=".".join(module_parts[common:]) or None,
                    names=aliases,
                    level=len(target_package) - common + 1,
                )
            else:
                node = ast.ImportFrom(
                    module=node.module,
                    names=aliases,
                    level=0,
                )
            class_error_aliases = [
                alias for alias in aliases if alias.name in CLASS_ERROR_NAMES
            ]
            method_aliases = [
                alias for alias in aliases if alias.name not in CLASS_ERROR_NAMES
            ]
            if method_aliases:
                method_imports.append(
                    ast.ImportFrom(
                        module=node.module,
                        names=method_aliases,
                        level=node.level,
                    )
                )
            if class_error_aliases:
                method_imports.append(
                    ast.ImportFrom(
                        module=soft_name + ".Classes",
                        names=class_error_aliases,
                        level=0,
                    )
                )

    source_lines = source.splitlines()
    start_line = min(
        [method_node.lineno]
        + [decorator.lineno for decorator in method_node.decorator_list]
    )
    while start_line > 1 and source_lines[start_line - 2].lstrip().startswith("#"):
        start_line -= 1
    method_source = "\n".join(source_lines[start_line - 1 : method_node.end_lineno])
    method_source = _remove_method_body_imports(
        method_source, method_body_imports, start_line, method_node
    )
    method_source = _resolve_method_relative_imports(method_source, source_package)
    method_source = _rename_method_references(method_source, renamed_method_names)
    method_source = _rewrite_method_call_targets(method_source, method_call_redirects)
    method_helper_names = inline_helper_names.difference(method_local_names)
    method_source = _rename_method_references(
        method_source,
        {name: "self." + name for name in method_helper_names},
    )
    method_source = _add_literal_keyword_defaults(
        method_source, inline_literal_defaults, used_names
    )
    method_source, default_overrides = _rewrite_hoisted_method_names(
        method_source,
        hoisted_names,
        method_name,
        (
            method_node.args.posonlyargs[0].arg
            if method_node.args.posonlyargs
            else method_node.args.args[0].arg
            if method_node.args.args
            else None
        ),
    )
    source_lines = source.splitlines()
    helper_sources = []
    for helper_name in sorted(inline_helper_names):
        helper_node = helper_function_nodes[helper_name]
        helper_source = "\n".join(
            source_lines[helper_node.lineno - 1 : helper_node.end_lineno]
        )
        helper_local_names = {
            node.id
            for node in ast.walk(helper_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
        }
        helper_local_names.update(
            argument.arg
            for argument in (
                helper_node.args.posonlyargs
                + helper_node.args.args
                + helper_node.args.kwonlyargs
            )
        )
        helper_reference_names = {
            name: class_name + "." + name
            for name in inline_helper_names.difference(helper_local_names)
        }
        helper_reference_names.update(
            {
                name: class_name + "." + name
                for name in hoisted_names.difference(helper_local_names)
            }
        )
        helper_reference_names.update(
            {
                name: class_name + "." + name
                for name in CLASS_BODY_CONSTANTS.get(class_name, {}).keys()
                if name not in helper_local_names
            }
        )
        helper_source = _rename_method_references(
            helper_source,
            helper_reference_names,
        )
        helper_sources.append("@staticmethod\n" + helper_source)
    if helper_sources:
        method_source += "\n\n" + "\n\n".join(helper_sources)
    method_import_bindings = {
        alias.asname
        or (alias.name.split(".")[0] if isinstance(node, ast.Import) else alias.name)
        for node in method_imports
        for alias in node.names
    }
    method_source, replaced_class_import = _replace_dynamic_class_imports(
        method_source, soft_name, method_import_bindings
    )
    if replaced_class_import:
        method_imports.append(
            ast.ImportFrom(
                module=soft_name + ".Functions.Load.import_class",
                names=[ast.alias(name="import_class", asname="_pyleecan_import_class")],
                level=0,
            )
        )
    method_tree = ast.parse(method_source)
    if any(
        _is_numpy_import(node) for node in method_imports + list(ast.walk(method_tree))
    ):
        method_source, method_imports = _normalize_method_numpy_imports(
            method_source, method_imports
        )
    if any(
        _is_package_import(node, "pyvista")
        for node in method_imports + list(ast.walk(ast.parse(method_source)))
    ):
        method_source, method_imports = _normalize_method_package_imports(
            method_source, method_imports, "pyvista", "pv"
        )
    class_attribute_loads = {
        node.id
        for assignment in class_attributes
        for node in ast.walk(assignment.value)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    os_import_bindings = {
        alias.asname
        or (
            alias.name.split(".")[0]
            if isinstance(node, ast.Import)
            else alias.name
        )
        for node in method_imports
        if _is_package_import(node, "os")
        for alias in node.names
        if isinstance(node, ast.ImportFrom)
        or alias.name == "os"
        or alias.name.startswith("os.")
    }
    if not class_attribute_loads.intersection(os_import_bindings) and any(
        _is_package_import(node, "os")
        for node in method_imports + list(ast.walk(ast.parse(method_source)))
    ):
        method_source, method_imports = _normalize_method_package_imports(
            method_source, method_imports, "os", "os"
        )
    return (
        method_source,
        method_imports,
        class_attributes,
        default_overrides,
        None,
    )


def _find_repeated_method_assignments(path_to_gen, class_pack, class_name, methods):
    """Find computed module assignments that are shared or used as defaults."""
    assignment_methods = {}
    method_assignments = {}
    default_assignments = {}
    configured_plot_assignments = set()

    for meth in methods:
        method_parts = [part for part in (class_pack or "").split(".") if part]
        method_parts.extend([class_name, *meth.split(".")])
        method_path = join(dirname(path_to_gen), "Methods", *method_parts) + ".py"
        try:
            with open(method_path, encoding="utf-8") as method_file:
                module = ast.parse(method_file.read(), filename=method_path)
        except FileNotFoundError:
            continue

        method_name = meth.split(".")[-1]
        method_node = next(
            (
                node
                for node in module.body
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
                and node.name == method_name
            ),
            None,
        )
        if method_node is None:
            continue

        used_names = {
            node.id
            for node in ast.walk(method_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
        }
        local_names = {
            node.id
            for node in ast.walk(method_node)
            if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
        }
        local_names.update(
            argument.arg
            for argument in (
                method_node.args.posonlyargs
                + method_node.args.args
                + method_node.args.kwonlyargs
            )
        )
        direct_default_names = {
            default.id
            for default in method_node.args.defaults
            + [node for node in method_node.args.kw_defaults if node is not None]
            if isinstance(default, ast.Name)
        }
        assigned_names = set()
        for node in module.body:
            if isinstance(node, ast.Assign):
                if len(node.targets) != 1 or not isinstance(node.targets[0], ast.Name):
                    continue
                name = node.targets[0].id
                value = node.value
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                name = node.target.id
                value = node.value
            else:
                continue
            is_configured_plot_assignment = (
                value is not None
                and (name.endswith("_COLOR") or name in CONFIGURED_PLOT_CONSTANT_NAMES)
                and any(
                    isinstance(child, ast.Name) and child.id == "config_dict"
                    for child in ast.walk(value)
                )
            )
            if (
                value is None
                or name in local_names
                or (name not in used_names and not is_configured_plot_assignment)
            ):
                continue
            try:
                ast.literal_eval(value)
            except ValueError, TypeError, SyntaxError:
                assigned_names.add(name)
                assignment_methods.setdefault(name, set()).add(meth)
                if name in direct_default_names:
                    default_assignments.setdefault(meth, set()).add(name)
                if is_configured_plot_assignment:
                    configured_plot_assignments.add(name)
        method_assignments[meth] = assigned_names

    hoisted_names = {
        name
        for name, methods_using_name in assignment_methods.items()
        if len(methods_using_name) > 1
    } | configured_plot_assignments
    return {
        meth: names.intersection(hoisted_names).union(
            default_assignments.get(meth, set())
        )
        for meth, names in method_assignments.items()
    }


def _prepare_class_methods(
    path_to_gen,
    class_pack,
    class_name,
    methods,
    soft_name,
    reserved_names=(),
    class_import_graph=None,
):
    """Inline methods and collect their imports without name conflicts."""
    prepared = {}
    fallback_reasons = {}
    imports = []
    import_groups = {}
    import_bindings = {}
    import_keys = set()
    target_package = [soft_name, "Classes"]
    class_attributes = {}
    class_error_definitions = {}
    class_method_definitions = {}
    class_method_imports = []
    method_default_overrides = {}
    repeated_assignments = _find_repeated_method_assignments(
        path_to_gen, class_pack, class_name, methods
    )

    for meth in methods:
        (
            method_source,
            method_imports,
            candidate_class_attributes,
            candidate_default_overrides,
            reason,
        ) = _get_method_source(
            path_to_gen,
            class_pack,
            class_name,
            meth,
            soft_name,
            repeated_assignments.get(meth, set()),
            class_import_graph=class_import_graph,
        )
        if reason is not None:
            warnings.warn(
                "Could not inline "
                + class_name
                + "."
                + meth
                + ": "
                + reason
                + "; keeping its module import",
                stacklevel=2,
            )
            prepared[meth] = None
            fallback_reasons[meth] = reason
            continue

        filtered_method_imports = []
        for import_node in method_imports:
            if not isinstance(import_node, ast.ImportFrom):
                filtered_method_imports.append(import_node)
                continue
            absolute_module = ".".join(
                _get_absolute_import_module(import_node, target_package)
            )
            retained_aliases = []
            for alias in import_node.names:
                configured_module_classes = CLASS_MODULE_CLASS_DEFINITIONS.get(
                    class_name
                )
                if (
                    configured_module_classes is not None
                    and absolute_module
                    == soft_name + ".Methods." + configured_module_classes[0]
                    and alias.name in configured_module_classes[1]
                ):
                    continue
                binding = alias.asname or alias.name
                configured_helper = CLASS_METHOD_HELPERS.get(class_name, {}).get(
                    binding
                )
                if (
                    configured_helper is None
                    or absolute_module != soft_name + ".Methods." + configured_helper[0]
                    or alias.name != configured_helper[1]
                ):
                    retained_aliases.append(alias)
                    continue
                helper_path = join(
                    dirname(path_to_gen),
                    "Methods",
                    *configured_helper[0].split("."),
                    "__init__.py",
                )
                with open(helper_path, encoding="utf-8") as helper_file:
                    helper_module = ast.parse(helper_file.read(), filename=helper_path)
                helper_node = next(
                    (
                        node
                        for node in helper_module.body
                        if isinstance(node, ast.FunctionDef)
                        and node.name == configured_helper[1]
                    ),
                    None,
                )
                if helper_node is None:
                    raise ValueError(
                        "Could not find configured class helper "
                        + configured_helper[1]
                        + " in "
                        + helper_path
                    )
                if configured_helper[1] in CLASS_STATIC_METHOD_HELPERS.get(
                    class_name, set()
                ):
                    helper_node.decorator_list.insert(
                        0, ast.Name(id="staticmethod", ctx=ast.Load())
                    )
                class_method_definitions[helper_node.name] = helper_node
                helper_used_names = {
                    node.id
                    for node in ast.walk(helper_node)
                    if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
                }
                for helper_import in helper_module.body:
                    if not isinstance(helper_import, (ast.Import, ast.ImportFrom)):
                        continue
                    used_aliases = [
                        helper_alias
                        for helper_alias in helper_import.names
                        if (
                            helper_alias.asname
                            or (
                                helper_alias.name.split(".")[0]
                                if isinstance(helper_import, ast.Import)
                                else helper_alias.name
                            )
                        )
                        in helper_used_names
                    ]
                    if used_aliases:
                        if isinstance(helper_import, ast.Import):
                            class_method_imports.append(ast.Import(names=used_aliases))
                            continue
                        helper_package = [
                            soft_name,
                            "Methods",
                            *configured_helper[0].split("."),
                        ]
                        absolute_helper_module = _get_absolute_import_module(
                            helper_import, helper_package
                        )
                        common = 0
                        while (
                            common < len(target_package)
                            and common < len(absolute_helper_module)
                            and target_package[common] == absolute_helper_module[common]
                        ):
                            common += 1
                        class_method_imports.append(
                            ast.ImportFrom(
                                module=".".join(absolute_helper_module[common:]),
                                names=used_aliases,
                                level=len(target_package) - common + 1,
                            )
                        )
            if retained_aliases:
                filtered_method_imports.append(
                    ast.ImportFrom(
                        module=import_node.module,
                        names=retained_aliases,
                        level=import_node.level,
                    )
                )
        method_imports = filtered_method_imports

        candidate_bindings = {}
        conflict = False
        conflict_name = None
        conflict_imports = None
        conflict_reason = None
        for assignment in candidate_class_attributes:
            binding = assignment.targets[0].id
            existing = class_attributes.get(binding)
            identity = ast.dump(assignment.value, include_attributes=False)
            if binding in reserved_names:
                conflict_reason = (
                    "class attribute '"
                    + binding
                    + "' conflicts with an existing class member"
                )
                break
            if (
                existing is not None
                and ast.dump(existing, include_attributes=False) != identity
            ):
                conflict_reason = (
                    "class attribute '"
                    + binding
                    + "' has different definitions in method modules"
                )
                break
        for import_node in method_imports:
            if conflict_reason is not None:
                break
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = _get_import_identity(import_node, alias, target_package)
                existing = import_bindings.get(binding)
                candidate = candidate_bindings.get(binding)
                for previous in (existing, candidate):
                    if previous is None or previous == identity:
                        continue
                    if _same_error_class_import(path_to_gen, previous, identity):
                        identity = previous
                    else:
                        conflict = True
                        conflict_name = binding
                        conflict_imports = (previous, identity)
                        break
                if conflict:
                    break
                candidate_bindings[binding] = identity
            if conflict:
                break

        candidate_error_definitions = {}
        if not conflict and conflict_reason is None:
            for import_node in method_imports:
                if not isinstance(import_node, ast.ImportFrom):
                    continue
                module_name = ".".join(
                    _get_absolute_import_module(import_node, target_package)
                )
                if not module_name.startswith(soft_name + ".Methods."):
                    continue
                for alias in import_node.names:
                    definitions = _get_error_class_definitions(
                        path_to_gen, module_name, alias.name
                    )
                    for definition in definitions:
                        existing = candidate_error_definitions.get(
                            definition.name,
                            class_error_definitions.get(definition.name),
                        )
                        if existing is not None and ast.dump(
                            existing, include_attributes=False
                        ) != ast.dump(definition, include_attributes=False):
                            conflict_reason = (
                                "class error '"
                                + definition.name
                                + "' has different definitions"
                            )
                            break
                        candidate_error_definitions[definition.name] = definition
                    if conflict_reason is not None:
                        break
                if conflict_reason is not None:
                    break

        if conflict or conflict_reason is not None:
            fallback_reason = (
                conflict_reason
                if conflict_reason is not None
                else (
                    "import name '"
                    + conflict_name
                    + "' refers to different sources ("
                    + _format_import_identity(conflict_imports[0])
                    + " and "
                    + _format_import_identity(conflict_imports[1])
                    + ")"
                )
            )
            warnings.warn(
                "Could not inline "
                + class_name
                + "."
                + meth
                + ": "
                + fallback_reason
                + "; "
                + "keeping its module import",
                stacklevel=2,
            )
            prepared[meth] = None
            fallback_reasons[meth] = fallback_reason
            continue

        prepared[meth] = method_source
        method_default_overrides[meth] = candidate_default_overrides
        class_error_definitions.update(candidate_error_definitions)
        for assignment in candidate_class_attributes:
            class_attributes.setdefault(assignment.targets[0].id, assignment.value)
        import_bindings.update(candidate_bindings)
        for import_node in method_imports:
            if isinstance(import_node, ast.ImportFrom):
                module_name = ".".join(
                    _get_absolute_import_module(import_node, target_package)
                )
                if module_name.startswith(soft_name + ".Methods."):
                    retained_aliases = [
                        alias
                        for alias in import_node.names
                        if not _get_error_class_definitions(
                            path_to_gen, module_name, alias.name
                        )
                    ]
                    if not retained_aliases:
                        continue
                    import_node = ast.ImportFrom(
                        module=import_node.module,
                        names=retained_aliases,
                        level=import_node.level,
                    )
            group_key = (
                type(import_node).__name__,
                getattr(import_node, "level", 0),
                getattr(import_node, "module", None),
                any(alias.name == "*" for alias in import_node.names),
            )
            if group_key not in import_groups:
                if isinstance(import_node, ast.Import):
                    grouped_import = ast.Import(names=[])
                else:
                    grouped_import = ast.ImportFrom(
                        module=import_node.module,
                        names=[],
                        level=import_node.level,
                    )
                import_groups[group_key] = grouped_import
                imports.append(grouped_import)
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = candidate_bindings[binding]
                if identity in import_keys:
                    continue
                import_keys.add(identity)
                import_groups[group_key].names.append(alias)

    if class_method_definitions:
        helper_names = set(class_method_definitions)
        for meth, method_source in prepared.items():
            if method_source is not None:
                prepared[meth] = _rename_method_references(
                    method_source,
                    {name: "self." + name for name in helper_names},
                )
        first_method = next(
            (meth for meth, source in prepared.items() if source is not None), None
        )
        if first_method is not None:
            helper_sources = [
                ast.unparse(class_method_definitions[name])
                for name in sorted(class_method_definitions)
            ]
            prepared[first_method] += "\n\n" + "\n\n".join(helper_sources)
        for import_node in class_method_imports:
            group_key = (
                type(import_node).__name__,
                getattr(import_node, "level", 0),
                getattr(import_node, "module", None),
                any(alias.name == "*" for alias in import_node.names),
            )
            if group_key not in import_groups:
                grouped_import = (
                    ast.Import(names=[])
                    if isinstance(import_node, ast.Import)
                    else ast.ImportFrom(
                        module=import_node.module,
                        names=[],
                        level=import_node.level,
                    )
                )
                import_groups[group_key] = grouped_import
                imports.append(grouped_import)
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = _get_import_identity(import_node, alias, target_package)
                previous = import_bindings.get(binding)
                if previous is not None and previous != identity:
                    raise ValueError(
                        "Class helper import name '"
                        + binding
                        + "' conflicts with "
                        + _format_import_identity(previous)
                    )
                import_bindings[binding] = identity
                if identity in import_keys:
                    continue
                import_keys.add(identity)
                import_groups[group_key].names.append(alias)

    assignments = [
        ast.fix_missing_locations(
            ast.Assign(targets=[ast.Name(id=name, ctx=ast.Store())], value=value)
        )
        for name, value in class_attributes.items()
    ]
    blocked_containers = set(import_bindings)
    if any(
        isinstance(node, ast.ImportFrom)
        and any(alias.name == "*" for alias in node.names)
        for node in imports
    ):
        blocked_containers.update(("dict", "list"))
    for name, method_source in prepared.items():
        if method_source is not None:
            prepared[name] = _replace_empty_containers(method_source, blocked_containers)
    return (
        prepared,
        [node for node in imports if node.names],
        fallback_reasons,
        assignments,
        method_default_overrides,
        list(class_error_definitions.values()),
    )


def _format_import_identity(identity):
    """Format the source of an import binding for inline-fallback reports."""
    import_type, level, module, name, alias = identity
    if import_type == "Import":
        source = name
    else:
        source = "." * level + (module + "." if module else "") + name
    if alias:
        source += " as " + alias
    return source


def _get_import_identity(import_node, alias, target_package):
    """Return a binding identity with relative imports resolved to package names."""
    if isinstance(import_node, ast.Import):
        return (
            "Import",
            0,
            None,
            alias.name,
            alias.asname,
        )

    module_parts = _get_absolute_import_module(import_node, target_package)
    return (
        "ImportFrom",
        0,
        ".".join(module_parts),
        alias.name,
        alias.asname,
    )


def _get_absolute_import_module(import_node, target_package):
    """Resolve an ImportFrom node to its absolute module path."""
    module_parts = (import_node.module or "").split(".")
    if import_node.level:
        module_parts = target_package[: len(target_package) - import_node.level + 1]
        if import_node.module:
            module_parts.extend(import_node.module.split("."))
    return module_parts


def _apply_import_style(source, soft_name, import_style, class_package="Classes"):
    """Apply the configured Pyleecan import style without rewriting other code."""
    target_package = [soft_name, class_package]
    lines = source.splitlines()
    replacements = []

    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom):
            continue

        if import_style == "absolute" and node.level:
            module_parts = _get_absolute_import_module(node, target_package)
            replacement = ast.ImportFrom(
                module=".".join(module_parts) or None,
                names=node.names,
                level=0,
            )
        elif (
            import_style == "relative"
            and not node.level
            and node.module
            and (node.module == soft_name or node.module.startswith(soft_name + "."))
        ):
            module_parts = node.module.split(".")
            common = 0
            while (
                common < len(target_package)
                and common < len(module_parts)
                and target_package[common] == module_parts[common]
            ):
                common += 1
            replacement = ast.ImportFrom(
                module=".".join(module_parts[common:]) or None,
                names=node.names,
                level=len(target_package) - common + 1,
            )
        else:
            continue

        start = node.lineno - 1
        end = node.end_lineno - 1
        prefix = lines[start][: node.col_offset]
        suffix = lines[end][node.end_col_offset :]
        replacements.append((start, end, prefix + ast.unparse(replacement) + suffix))

    for start, end, replacement in reversed(replacements):
        lines[start : end + 1] = [replacement]
    return "\n".join(lines) + ("\n" if source.endswith("\n") else "")


def _get_import_scope_info(scope_body, package):
    """Collect names local to a scope and its directly imported package symbols."""
    local_names = set()
    package_names = {}
    global_names = set()
    assigned_names = set()

    class ScopeVisitor(ast.NodeVisitor):
        def visit_FunctionDef(self, node):
            local_names.add(node.name)

        visit_AsyncFunctionDef = visit_FunctionDef

        def visit_ClassDef(self, node):
            local_names.add(node.name)

        def visit_Lambda(self, node):
            return

        def visit_Name(self, node):
            if isinstance(node.ctx, (ast.Store, ast.Del)):
                local_names.add(node.id)
                assigned_names.add(node.id)

        def visit_Global(self, node):
            global_names.update(node.names)

        def visit_Import(self, node):
            for alias in node.names:
                local_names.add(alias.asname or alias.name.split(".")[0])
                if alias.name == package or alias.name.startswith(package + "."):
                    module_name = alias.name[len(package) :].lstrip(".")
                    package_names[alias.asname or alias.name.split(".")[0]] = (
                        (module_name or None) if alias.asname else None
                    )

        def visit_ImportFrom(self, node):
            for alias in node.names:
                local_names.add(alias.asname or alias.name)
                if (
                    node.module
                    and (
                        node.module == package or node.module.startswith(package + ".")
                    )
                    and alias.name != "*"
                ):
                    module_name = node.module[len(package) :].lstrip(".")
                    imported_name = ".".join(
                        part for part in (module_name, alias.name) if part
                    )
                    package_names[alias.asname or alias.name] = imported_name

    visitor = ScopeVisitor()
    for statement in scope_body:
        visitor.visit(statement)

    local_names.difference_update(global_names)
    for name in global_names:
        package_names.pop(name, None)
    shadowed_names = assigned_names.intersection(package_names)
    return local_names, package_names, shadowed_names


def _apply_package_import_style(source, package, package_alias):
    """Normalize package imports and their references to a shared module alias."""
    tree = ast.parse(source)
    if package in ("pyvista", "os"):
        imported_names = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imported_names.update(
                    alias.asname or alias.name.split(".")[0]
                    for alias in node.names
                    if alias.name == package or alias.name.startswith(package + ".")
                )
                if package == "os" and any(
                    alias.name.startswith("os.") for alias in node.names
                ):
                    return source
            elif isinstance(node, ast.ImportFrom) and node.module and (
                node.module == package or node.module.startswith(package + ".")
            ):
                if node.level:
                    return source
                if package == "os" and node.module != "os" and node.module != "os.path":
                    return source
                imported_names.update(alias.asname or alias.name for alias in node.names)
        for node in ast.walk(tree):
            if package == "os" and isinstance(node, (ast.Import, ast.ImportFrom)):
                aliases = node.names
                is_os_import = (
                    isinstance(node, ast.Import)
                    and any(
                        item.name == package or item.name.startswith(package + ".")
                        for item in aliases
                    )
                ) or (
                    isinstance(node, ast.ImportFrom)
                    and node.module is not None
                    and (node.module == package or node.module.startswith(package + "."))
                )
                if is_os_import:
                    if any(
                        isinstance(other, ast.stmt)
                        and other is not node
                        and (
                            other.lineno == node.lineno
                            and other.col_offset < node.col_offset
                            or other.lineno == node.end_lineno
                            and other.col_offset >= node.end_col_offset
                        )
                        for other in ast.walk(tree)
                    ):
                        return source
            if (
                isinstance(node, ast.Name)
                and node.id == package_alias
                and isinstance(node.ctx, (ast.Store, ast.Del))
            ) or (isinstance(node, ast.arg) and node.arg == package_alias):
                return source
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                if node.name == package_alias:
                    return source
            if isinstance(node, ast.ExceptHandler) and node.name == package_alias:
                return source
            if isinstance(node, (ast.Global, ast.Nonlocal)) and (
                set(node.names) & (imported_names | {package_alias})
            ):
                return source
            if isinstance(node, ast.Lambda) and any(
                argument.arg in imported_names
                for argument in (
                    node.args.posonlyargs
                    + node.args.args
                    + node.args.kwonlyargs
                    + ([node.args.vararg] if node.args.vararg else [])
                    + ([node.args.kwarg] if node.args.kwarg else [])
                )
            ):
                return source
            if isinstance(node, ast.comprehension) and any(
                isinstance(target, ast.Name) and target.id in imported_names
                for target in ast.walk(node.target)
            ):
                return source
            if isinstance(node, ast.ClassDef) and any(
                isinstance(child, ast.Name)
                and isinstance(child.ctx, (ast.Store, ast.Del))
                and child.id in imported_names
                for statement in node.body
                if not isinstance(statement, (ast.FunctionDef, ast.AsyncFunctionDef))
                for child in ast.walk(statement)
            ):
                return source
            if isinstance(node, ast.Import):
                if any(
                    (alias.asname or alias.name.split(".")[0]) == package_alias
                    and not (
                        alias.name == package or alias.name.startswith(package + ".")
                    )
                    for alias in node.names
                ):
                    return source
            if isinstance(node, ast.ImportFrom):
                if node.module == package or (
                    node.module and node.module.startswith(package + ".")
                ):
                    if any(alias.name == "*" for alias in node.names):
                        return source
                elif any(
                    (alias.asname or alias.name) == package_alias
                    for alias in node.names
                ):
                    return source
            if isinstance(
                node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                _, _, shadowed_names = _get_import_scope_info(node.body, package)
                if shadowed_names:
                    return source
    _, module_names, module_shadowed_names = _get_import_scope_info(tree.body, package)

    source_bytes = source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    duplicate_module_imports = set()
    has_module_package_import = False
    for node in tree.body:
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and (node.module == package or node.module.startswith(package + "."))
        ):
            if any(alias.name == "*" for alias in node.names):
                continue
            if has_module_package_import:
                duplicate_module_imports.add(id(node))
            has_module_package_import = True
        elif isinstance(node, ast.Import):
            package_aliases = [
                alias
                for alias in node.names
                if alias.name == package or alias.name.startswith(package + ".")
            ]
            if package_aliases:
                if has_module_package_import:
                    duplicate_module_imports.add(id(node))
                has_module_package_import = True

    def add_statement_replacement(node, replacement):
        start = line_offsets[node.lineno - 1]
        statement_start = start + node.col_offset
        end = line_offsets[node.end_lineno - 1] + node.end_col_offset
        line_end = source_bytes.find(b"\n", end)
        if line_end == -1:
            line_end = len(source_bytes)
        indentation = source_bytes[start:statement_start]
        suffix = source_bytes[end:line_end]
        replacements.append((start, line_end, indentation + replacement + suffix))

    class ReferenceVisitor(ast.NodeVisitor):
        def __init__(self):
            self.scopes = []

        def visit_FunctionDef(self, node):
            self._visit_function(node)

        def visit_AsyncFunctionDef(self, node):
            self._visit_function(node)

        def _visit_function(self, node):
            for decorator in node.decorator_list:
                self.visit(decorator)
            for default in node.args.defaults + node.args.kw_defaults:
                if default is not None:
                    self.visit(default)
            for argument in (
                node.args.posonlyargs + node.args.args + node.args.kwonlyargs
            ):
                if argument.annotation is not None:
                    self.visit(argument.annotation)
            if node.args.vararg and node.args.vararg.annotation:
                self.visit(node.args.vararg.annotation)
            if node.args.kwarg and node.args.kwarg.annotation:
                self.visit(node.args.kwarg.annotation)
            if node.returns is not None:
                self.visit(node.returns)
            body = node.body
            local_names, package_names, shadowed_names = _get_import_scope_info(
                body, package
            )
            argument_names = {
                argument.arg
                for argument in (
                    node.args.posonlyargs + node.args.args + node.args.kwonlyargs
                )
            }
            if node.args.vararg:
                argument_names.add(node.args.vararg.arg)
            if node.args.kwarg:
                argument_names.add(node.args.kwarg.arg)
            local_names.update(argument_names)
            self.scopes.append((local_names, package_names, shadowed_names))
            for statement in body:
                self.visit(statement)
            self.scopes.pop()

        def visit_ClassDef(self, node):
            for decorator in node.decorator_list:
                self.visit(decorator)
            for base in node.bases:
                self.visit(base)
            for keyword in node.keywords:
                self.visit(keyword.value)
            for statement in node.body:
                self.visit(statement)

        def visit_Name(self, node):
            if not isinstance(node.ctx, ast.Load):
                return

            imported_name = None
            for local_names, package_names, shadowed_names in reversed(self.scopes):
                if node.id in shadowed_names:
                    return
                if node.id in package_names:
                    imported_name = package_names[node.id]
                    break
                if node.id in local_names:
                    return
            else:
                if node.id not in module_names:
                    return
                if node.id in module_shadowed_names:
                    return
                imported_name = module_names[node.id]

            if imported_name is None:
                replacement = package_alias.encode("utf-8")
            else:
                replacement = (package_alias + "." + imported_name).encode("utf-8")
            start = line_offsets[node.lineno - 1] + node.col_offset
            end = start + len(node.id.encode("utf-8"))
            replacements.append((start, end, replacement))

    ReferenceVisitor().visit(tree)

    for node in ast.walk(tree):
        if (
            isinstance(node, ast.ImportFrom)
            and node.module
            and (node.module == package or node.module.startswith(package + "."))
        ):
            if any(alias.name == "*" for alias in node.names):
                continue
            replacement = (
                b""
                if id(node) in duplicate_module_imports
                else (
                    f"import {package}"
                    if package == package_alias
                    else f"import {package} as {package_alias}"
                ).encode("utf-8")
            )
            add_statement_replacement(node, replacement)
        elif isinstance(node, ast.Import):
            aliases = []
            changed = False
            package_seen = False
            for alias in node.names:
                if alias.name == package or alias.name.startswith(package + "."):
                    if id(node) in duplicate_module_imports or package_seen:
                        changed = True
                        continue
                    aliases.append(
                        ast.alias(
                            name=package,
                            asname=package_alias if package != package_alias else None,
                        )
                    )
                    package_seen = True
                    changed = True
                else:
                    aliases.append(alias)
            if changed:
                add_statement_replacement(
                    node,
                    (
                        ast.unparse(ast.Import(names=aliases)).encode("utf-8")
                        if aliases
                        else b""
                    ),
                )

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8")


def _apply_numpy_import_style(source):
    """Use ``import numpy as np`` for NumPy imports and their references."""
    return _apply_package_import_style(source, "numpy", "np")


def _apply_pyvista_import_style(source):
    """Use ``import pyvista as pv`` for PyVista imports and their references."""
    return _apply_package_import_style(source, "pyvista", "pv")


def _apply_os_import_style(source):
    """Use ``import os`` for os imports and their references."""
    return _apply_package_import_style(source, "os", "os")


def _organize_header_imports(source, class_name, class_path):
    """Run Ruff's import organizer on the generated module header only."""
    module = ast.parse(source, filename=class_path)
    class_node = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if class_node is None:
        raise ValueError(
            "Could not find generated class " + class_name + " in " + class_path
        )
    source_header_end = sum(
        len(line) for line in source.splitlines(keepends=True)[: class_node.lineno - 1]
    )
    with tempfile.TemporaryDirectory(dir=dirname(class_path)) as temp_dir:
        temp_path = join(temp_dir, basename(class_path))
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(source)
        result = subprocess.run(
            [
                "ruff",
                "check",
                "--select",
                "F401,I001",
                "--fix-only",
                temp_path,
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not organize imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        result = subprocess.run(
            ["ruff", "format", temp_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not format imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        with open(temp_path, encoding="utf-8") as temp_file:
            organized_source = temp_file.read()
        organized_module = ast.parse(organized_source, filename=class_path)
        organized_class = next(
            node
            for node in organized_module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
        organized_header_end = sum(
            len(line)
            for line in organized_source.splitlines(keepends=True)[
                : organized_class.lineno - 1
            ]
        )
    return organized_source[:organized_header_end] + source[source_header_end:]


def _regroup_pyleecan_imports(source, class_name, class_path):
    """Regroup generated Pyleecan package imports in the module header."""
    module = ast.parse(source, filename=class_path)
    class_node = next(
        (
            node
            for node in module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        ),
        None,
    )
    if class_node is None:
        raise ValueError(
            "Could not find generated class " + class_name + " in " + class_path
        )
    original_header_end = sum(
        len(line)
        for line in source.splitlines(keepends=True)[: class_node.lineno - 1]
    )

    package_order = (
        "pyleecan.Classes",
        "pyleecan.definitions",
        "pyleecan.Functions",
    )
    imports_by_package = {package: {} for package in package_order}
    import_nodes = []
    for node in module.body:
        if not isinstance(node, ast.ImportFrom) or not node.module:
            continue
        package = next(
            (
                package
                for package in package_order
                if node.module == package or node.module.startswith(package + ".")
            ),
            None,
        )
        if package is None:
            continue
        import_nodes.append(node)
        aliases = imports_by_package[package].setdefault(node.module, {})
        for alias in node.names:
            aliases[(alias.name, alias.asname)] = alias

    if not import_nodes:
        return source

    grouped_lines = []
    for package in package_order:
        package_lines = []
        for import_module in sorted(imports_by_package[package]):
            aliases = imports_by_package[package][import_module]
            ordered_aliases = [
                aliases[key]
                for key in sorted(
                    aliases, key=lambda item: (item[0], item[1] or "")
                )
            ]
            package_lines.append(
                ast.unparse(
                    ast.ImportFrom(
                        module=import_module,
                        names=ordered_aliases,
                        level=0,
                    )
                )
            )
        grouped_lines.extend(package_lines)
    grouped_imports = "\n".join(grouped_lines) + "\n"

    source_lines = source.splitlines(keepends=True)
    import_edits = []
    for index, node in enumerate(sorted(import_nodes, key=lambda item: item.lineno)):
        start = node.lineno - 1
        end = node.end_lineno
        if index == 0:
            import_edits.append((start, end, grouped_imports))
        else:
            import_edits.append((start, end, ""))
    regrouped_lines = list(source_lines)
    for start, end, replacement in sorted(import_edits, reverse=True):
        regrouped_lines[start:end] = replacement.splitlines(keepends=True)
    regrouped_source = "".join(regrouped_lines)

    regrouped_module = ast.parse(regrouped_source, filename=class_path)
    regrouped_class = next(
        node
        for node in regrouped_module.body
        if isinstance(node, ast.ClassDef) and node.name == class_name
    )
    with tempfile.TemporaryDirectory(dir=dirname(class_path)) as temp_dir:
        temp_path = join(temp_dir, basename(class_path))
        with open(temp_path, "w", encoding="utf-8") as temp_file:
            temp_file.write(regrouped_source)
        result = subprocess.run(
            ["ruff", "format", temp_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
        if result.returncode:
            raise RuntimeError(
                "Ruff could not format grouped imports in "
                + class_path
                + ": "
                + (result.stderr or result.stdout).strip()
            )
        with open(temp_path, encoding="utf-8") as temp_file:
            formatted_source = temp_file.read()
        formatted_module = ast.parse(formatted_source, filename=class_path)
        formatted_class = next(
            node
            for node in formatted_module.body
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
        formatted_header_end = sum(
            len(line)
            for line in formatted_source.splitlines(keepends=True)[
                : formatted_class.lineno - 1
            ]
        )
    return formatted_source[:formatted_header_end] + source[original_header_end:]


def _is_numpy_import(node):
    return _is_package_import(node, "numpy")


def _is_package_import(node, package):
    if isinstance(node, ast.ImportFrom):
        return bool(
            node.module
            and (node.module == package or node.module.startswith(package + "."))
        )
    return isinstance(node, ast.Import) and any(
        alias.name == package or alias.name.startswith(package + ".")
        for alias in node.names
    )


def _normalize_method_numpy_imports(method_source, method_imports):
    """Normalize a method's NumPy imports before checking inter-method conflicts."""
    return _normalize_method_package_imports(
        method_source, method_imports, "numpy", "np"
    )


def _normalize_method_package_imports(method_source, method_imports, package, alias):
    """Normalize a method's package imports before checking inter-method conflicts."""
    import_source = "\n".join(ast.unparse(node) for node in method_imports)
    combined_source = (import_source + "\n\n" if import_source else "") + method_source
    normalized_source = _apply_package_import_style(combined_source, package, alias)
    tree = ast.parse(normalized_source)
    method_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    ]
    method_node = method_nodes[0]
    imports = [
        node
        for node in tree.body
        if isinstance(node, (ast.Import, ast.ImportFrom))
        and node.lineno < method_node.lineno
    ]

    lines = normalized_source.splitlines()
    start_line = min(
        [method_node.lineno]
        + [decorator.lineno for decorator in method_node.decorator_list]
    )
    import_end = max((node.end_lineno for node in imports), default=0)
    while start_line > import_end + 1 and lines[start_line - 2].lstrip().startswith(
        "#"
    ):
        start_line -= 1
    method_source = "\n".join(lines[start_line - 1 : method_nodes[-1].end_lineno])
    return method_source, imports


def _add_literal_keyword_defaults(method_source, literal_defaults, used_names):
    """Turn referenced module literals into keyword-only method defaults."""
    tree = ast.parse(method_source)
    method_node = next(
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    arguments = method_node.args
    defined_arguments = {
        argument.arg
        for argument in (
            arguments.posonlyargs
            + arguments.args
            + arguments.kwonlyargs
            + ([arguments.vararg] if arguments.vararg else [])
            + ([arguments.kwarg] if arguments.kwarg else [])
        )
    }
    method_locals = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del))
    }
    defaults = [
        (name, value)
        for name, value in literal_defaults.items()
        if name in used_names
        and name not in defined_arguments
        and name not in method_locals
    ]
    if not defaults:
        return method_source

    keyword_defaults = ", ".join(name + "=" + value for name, value in defaults)
    has_keyword_section = bool(arguments.vararg or arguments.kwonlyargs)
    if has_keyword_section:
        insertion = ", " + keyword_defaults
        insertion_argument = (
            arguments.kwonlyargs[-1] if arguments.kwonlyargs else arguments.vararg
        )
    else:
        insertion = ", *, " + keyword_defaults
        positional_arguments = arguments.posonlyargs + arguments.args
        insertion_argument = positional_arguments[-1] if positional_arguments else None

    encoded_lines = method_source.splitlines(keepends=True)

    def offset_for_position(line_number, column_offset):
        character_prefix = sum(len(line) for line in encoded_lines[: line_number - 1])
        current_line = encoded_lines[line_number - 1]
        character_column = len(
            current_line.encode("utf-8")[:column_offset].decode("utf-8")
        )
        return character_prefix + character_column

    def argument_end(argument):
        positional_arguments = arguments.posonlyargs + arguments.args
        if argument in positional_arguments:
            default_start = len(positional_arguments) - len(arguments.defaults)
            argument_index = positional_arguments.index(argument)
            if argument_index >= default_start:
                default = arguments.defaults[argument_index - default_start]
                return offset_for_position(default.end_lineno, default.end_col_offset)
        elif argument in arguments.kwonlyargs:
            default = arguments.kw_defaults[arguments.kwonlyargs.index(argument)]
            if default is not None:
                return offset_for_position(default.end_lineno, default.end_col_offset)
        return offset_for_position(argument.end_lineno, argument.end_col_offset)

    if insertion_argument is not None:
        offset = argument_end(insertion_argument)
    elif arguments.kwarg is not None:
        offset = offset_for_position(arguments.kwarg.lineno, arguments.kwarg.col_offset)
        insertion = "*, " + keyword_defaults + ", "
    else:
        closing_paren = method_source.find(")", method_node.args.end_col_offset)
        if closing_paren == -1:
            raise SyntaxError("Could not locate method signature closing parenthesis")
        offset = closing_paren
        insertion = "*, " + keyword_defaults

    return method_source[:offset] + insertion + method_source[offset:]


def _rewrite_hoisted_method_names(
    method_source, hoisted_names, method_name, instance_argument
):
    """Rewrite hoisted module names to instance attributes and restore defaults."""
    if not hoisted_names:
        return method_source, []
    if instance_argument is None:
        raise ValueError("Hoisted module assignments require an instance argument")

    tree = ast.parse(method_source)
    method_node = next(
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
    )
    source_bytes = method_source.encode("utf-8")
    line_offsets = [0]
    for index, value in enumerate(source_bytes):
        if value == ord("\n"):
            line_offsets.append(index + 1)

    replacements = []
    default_overrides = []

    def add_replacement(node, replacement):
        start = line_offsets[node.lineno - 1] + node.col_offset
        end = start + len(node.id.encode("utf-8"))
        replacements.append((start, end, replacement.encode("utf-8")))

    for statement in method_node.body:
        for node in ast.walk(statement):
            if (
                isinstance(node, ast.Name)
                and isinstance(node.ctx, ast.Load)
                and node.id in hoisted_names
            ):
                add_replacement(node, instance_argument + "." + node.id)

    positional_arguments = method_node.args.posonlyargs + method_node.args.args
    for index, default in enumerate(method_node.args.defaults):
        if isinstance(default, ast.Name) and default.id in hoisted_names:
            add_replacement(default, "None")
            default_index = index
            default_overrides.append(
                ast.parse(
                    method_name
                    + ".__defaults__ = "
                    + method_name
                    + ".__defaults__[:"
                    + str(default_index)
                    + "] + ("
                    + default.id
                    + ",) + "
                    + method_name
                    + ".__defaults__["
                    + str(default_index + 1)
                    + ":]"
                ).body[0]
            )
    for argument, default in zip(
        method_node.args.kwonlyargs, method_node.args.kw_defaults
    ):
        if isinstance(default, ast.Name) and default.id in hoisted_names:
            add_replacement(default, "None")
            default_overrides.append(
                ast.parse(
                    method_name
                    + ".__kwdefaults__["
                    + repr(argument.arg)
                    + "] = "
                    + default.id
                ).body[0]
            )

    for start, end, replacement in sorted(replacements, reverse=True):
        source_bytes = source_bytes[:start] + replacement + source_bytes[end:]
    return source_bytes.decode("utf-8"), default_overrides


def generate_class(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name="pyleecan",
    is_log=True,
    import_style="absolute",
    class_import_graph=None,
    is_new=False,
    output_name=None,
):
    """Generate the corresponding class file.

    Parameters
    ----------
    gen_dict : dict
        Dict with key = class name and value = class dict (name, package, properties, methods...)
    class_name : str
        name of the class to generate
    path_to_gen : str
        path to the file to save the class code
    import_style : str
        "relative" or "absolute" style for imports from the generated Pyleecan package
    class_import_graph : dict, optional
        Snapshot of class imports used to detect circular imports.
    is_new : bool, optional
        Generate the experimental dataclass version instead of the legacy class.
        The dataclass version uses the ``Classes_new`` inheritance hierarchy.
    output_name : str, optional
        Output module name for the dataclass version, without the .py extension.
        Defaults to the snake_case class name.

    Returns
    -------
    str or None
        The generated path for the dataclass version; None for the legacy version.

    """

    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")
    if not is_new and output_name is not None:
        raise ValueError("output_name is only supported when is_new=True")
    if is_new:
        validate_class_module_names(gen_dict)

    class_dict = gen_dict[class_name]
    class_pack = class_dict["package"]
    if is_new and class_import_graph is None:
        source_class_dir = join(dirname(path_to_gen), "Classes")
        class_import_graph = get_class_import_graph(source_class_dir, gen_dict, soft_name)
    reserved_names = {constant["name"] for constant in class_dict["constants"]} | {
        method.split(".")[-1] for method in class_dict["methods"]
    }
    reserved_names.update(prop["name"] for prop in class_dict["properties"])
    (
        method_sources,
        method_imports,
        fallback_reasons,
        class_attributes,
        method_default_overrides,
        class_error_definitions,
    ) = _prepare_class_methods(
        path_to_gen,
        class_pack,
        class_name,
        class_dict["methods"],
        soft_name,
        reserved_names=reserved_names,
        class_import_graph=class_import_graph,
    )

    if is_new:
        return _generate_dataclass_class(
            gen_dict,
            class_name,
            path_to_gen,
            soft_name,
            import_style,
            output_name,
            method_sources,
            method_imports,
            fallback_reasons,
            class_attributes,
            method_default_overrides,
            class_error_definitions,
        )

    # Start of file generation
    # Create or Erase the file by opening it
    class_file = open(join(path_to_gen, class_name + ".py"), "w", encoding="utf-8")

    # List of non python type to import
    import_type_list = list(find_import_type(gen_dict, class_dict, []))
    if class_name in import_type_list:  # For recursive class
        import_type_list.remove(class_name)
    # Encoding
    # class_file.write("# -*- coding: utf-8 -*-\n")

    # Warning
    class_file.write(
        "# File generated according to "
        + class_dict["path"][class_dict["path"].find("Generator") :]
        + "\n"
    )
    if class_dict["is_internal"]:
        class_file.write(
            "# WARNING! Internal version of the class: DO NOT SHARE ON GITHUB !\n"
        )
    class_file.write("# WARNING! All changes made in this file will be lost!\n")
    class_file.write(
        '"""Method code available at https://github.com/Eomys/'
        + soft_name
        + "/tree/master/"
        + soft_name
        + "/Methods/"
        + class_dict["package"]
        + "/"
        + class_dict["name"]
        + '\n"""\n\n'
    )
    class_file.writelines(
        name + " = " + repr(value) + "\n"
        for name, value in CLASS_MODULE_CONSTANTS.get(class_name, {}).items()
    )
    class_file.writelines(
        name + " = " + expression + "\n"
        for name, expression in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(
            class_name, {}
        ).items()
    )
    if (
        class_name in CLASS_MODULE_CONSTANTS
        or class_name in CLASS_MODULE_CONSTANT_EXPRESSIONS
    ):
        class_file.write("\n")
    if fallback_reasons:
        class_file.write("# Inline fallback report:\n")
        class_file.write(
            "# These methods remain imported because their source or imports cannot "
            "be safely moved into this class.\n"
        )
        class_file.writelines(
            "# - " + meth + ": " + reason + "\n"
            for meth, reason in fallback_reasons.items()
        )
        class_file.write("\n")

    # Import
    class_file.write("from os import linesep\n")
    class_file.write("from sys import getsizeof\n")
    if is_log:
        class_file.write("from logging import getLogger\n")

    if "ndarray" in import_type_list:
        class_file.write("from ._check import set_array, " + "check_var, raise_\n")
    else:
        class_file.write("from ._check import check_var, raise_\n")

    # Get logger function
    if is_log:
        class_file.write("from ..Functions.get_logger import get_logger\n")

    #
    # if len(class_dict["properties"]) == 0 and class_dict["mother"] == "":
    #     class_file.write("from ..Functions.get_logger import check_init_dict\n")

    # Save function
    class_file.write("from ..Functions.save import save\n")
    class_file.write("from ..Functions.load import load_init_dict\n")
    class_file.write("from ..Functions.Load.import_class import import_class\n")
    # Copy method
    class_file.write("from copy import deepcopy\n")

    # Import of the mother_class (FrozenClass by default)
    # All the classes file are in the Classes folder (regardless of their main package)
    if class_dict["mother"] != "" and "." not in class_dict["mother"]:
        class_file.write(
            "from ." + class_dict["mother"] + " import " + class_dict["mother"] + "\n\n"
        )
    elif class_dict["mother"] != "" and "." in class_dict["mother"]:
        class_split = class_dict["mother"].split(".")
        # Daughter of external package class
        class_file.write(
            "from " + ".".join(class_split[:-1]) + " import " + class_split[-1] + "\n\n"
        )
    else:
        class_file.write("from ._frozen import FrozenClass\n\n")

    # Import all the methods of the class
    # The methods are in Methods.<Main package>.<class name>, one file per method
    # if len(class_dict["methods"]) > 0:
    #     class_file.write("# Import all class method\n")
    #     class_file.write(
    #         "# Try/catch to remove unnecessary dependencies in unused method\n"
    #     )
    class_file.writelines(
        import_method(class_pack, class_name, meth)
        for meth in class_dict["methods"]
        if method_sources[meth] is None
    )
    class_file.writelines(ast.unparse(node) + "\n" for node in method_imports)
    if len(class_dict["methods"]) > 0:
        class_file.write("\n")

    # ImportMatrixVal for ImportMatrix setter
    if "ImportMatrix" in import_type_list:
        class_file.write("from ..Classes.ImportMatrixVal import ImportMatrixVal\n")
        class_file.write("from numpy import ndarray\n")
        if "ndarray" not in import_type_list and "{ndarray}" not in import_type_list:
            import_type_list.append("ndarray")
    # Import Array from numpy
    if (
        "{ndarray}" in import_type_list
        or "[ndarray]" in import_type_list
        or "ndarray" in import_type_list
    ):
        class_file.write("from numpy import array, array_equal\n")
    if "{ndarray}" in import_type_list:
        import_type_list.remove("{ndarray}")
    if "[ndarray]" in import_type_list:
        import_type_list.remove("[ndarray]")
    if "ndarray" in import_type_list:
        import_type_list.remove("ndarray")
    if "[]" in import_type_list:
        class_file.write("from numpy import array, ndarray\n")
    if "function" in import_type_list:
        class_file.write("from ntpath import basename\n")
        class_file.write("from os.path import isfile\n")
        class_file.write("from ._check import CheckTypeError\n")
        class_file.write("import numpy as np\n")
        class_file.write("import random\n")
        import_type_list.remove("function")
    class_file.write("from numpy import isnan\n")  # For compare

    # Import types from other package
    types_imported = []
    for import_type in import_type_list:
        if "." in import_type and "SciDataTool" not in import_type:
            class_file.write("from cloudpickle import dumps, loads\n")
            class_file.write("from ._check import CheckTypeError\n")

            # Remove the list if needed
            if import_type.startswith("["):
                import_type = import_type[1:-1]

            # Extract import name
            from_name = import_type[: import_type.rfind(".")]
            type_name = import_type[import_type.rfind(".") + 1 :]

            # Import the type if not already imported
            if type_name not in types_imported:
                class_file.write("try :\n")
                class_file.write(
                    TAB + "from " + from_name + " import " + type_name + "\n"
                )
                class_file.write("except ImportError :\n")
                class_file.write(TAB + type_name + " = ImportError\n")

                types_imported.append(type_name)

    # Import of all needed software type for empty init
    class_file.write("from ._check import InitUnKnowClassError\n")

    # Class declaration
    if class_dict["mother"] != "" and "." not in class_dict["mother"]:
        class_file.write(
            "\n\nclass " + class_name + "(" + class_dict["mother"] + "):\n"
        )
    elif class_dict["mother"] != "" and "." in class_dict["mother"]:
        class_file.write(
            "\n\nclass "
            + class_name
            + "("
            + class_dict["mother"].split(".")[-1]
            + "):\n"
        )
    else:
        class_file.write("\n\nclass " + class_name + "(FrozenClass):\n")

    # Class Docstring
    if class_dict["desc"] != "":
        class_file.write(TAB + '"""' + class_dict["desc"] + '"""\n')
    class_file.write("\n")

    # Declare all class Constante (VERSION should be a constante for every classes)
    class_file.writelines(
        TAB + cst["name"] + " = " + str(cst["value"]) + "\n"
        for cst in class_dict["constants"]
    )
    class_file.writelines(
        TAB + name + " = " + value + "\n"
        for name, value in CLASS_BODY_CONSTANTS.get(class_name, {}).items()
    )
    class_file.writelines(
        TAB + ast.unparse(assignment) + "\n" for assignment in class_attributes
    )
    class_file.write("\n")

    # Asign all the Methods of the class
    # if len(class_dict["methods"]) > 1:
    #     class_file.write(
    #         TAB
    #         + "# Check ImportError to remove unnecessary dependencies in unused method\n"
    #     )
    for meth in class_dict["methods"]:
        meth_name = meth.split(".")[-1]
        if class_pack not in ["", None]:
            class_file.write(
                TAB
                + "# cf Methods."
                + class_pack
                + "."
                + class_name
                + "."
                + meth
                + "\n"
            )
        else:
            class_file.write(TAB + "# cf Methods." + class_name + "." + meth + "\n")
        if method_sources[meth] is not None:
            class_file.write(indent(method_sources[meth], TAB) + "\n\n")
            for override in method_default_overrides[meth]:
                class_file.write(TAB + ast.unparse(override) + "\n")
                class_file.write("\n")
            continue
        # # class_file.write(TAB + "if isinstance(" + meth_name + ", ImportError):\n")
        # # class_file.write(TAB2 + meth_name + " = property(\n")
        # # class_file.write(TAB3 + "fget=lambda x: raise_(\n")
        # # PEP8 formating
        # if len(class_name) + 2 * len(meth_name) > 39:
        #     # 2 lines Import text
        #     class_file.write(TAB4 + "ImportError(\n")
        #     class_file.write(
        #         TAB5 + """"Can't use """ + class_name + " method " + meth_name + ': "\n'
        #     )
        #     class_file.write(TAB5 + "+ str(" + meth_name + ")\n")
        #     class_file.write(TAB4 + ")\n")
        # elif len(class_name) + 2 * len(meth_name) > 29:
        #     # Import text on line different line
        #     class_file.write(TAB4 + "ImportError(\n")
        #     class_file.write(
        #         TAB5 + """"Can't use """ + class_name + " method " + meth_name + ': "'
        #     )
        #     class_file.write(" + str(" + meth_name + ")\n")
        #     class_file.write(TAB4 + ")\n")
        # else:  # On one line
        #     class_file.write(
        #         TAB4
        #         + """ImportError("Can't use """
        #         + class_name
        #         + " method "
        #         + meth_name
        #         + ': " + str('
        #         + meth_name
        #         + "))\n"
        #     )
        # class_file.write(TAB3 + ")\n")
        # class_file.write(TAB2 + ")\n")
        # class_file.write(TAB + "else:\n")
        class_file.write(TAB + meth_name + " = " + meth_name + "\n")
    # Save methods
    class_file.write(TAB + "# generic save method is available in all object\n")
    if "save" not in class_dict["methods"]:
        class_file.write(TAB + "save = save\n")

    if is_log:
        class_file.write(TAB + "# get_logger method is available in all object\n")
        class_file.write(TAB + "get_logger = get_logger\n\n")

    # Add the __init__ method
    if "__init__" not in class_dict["methods"]:
        if len(class_dict["properties"]) == 0 and class_dict["mother"] == "":
            class_file.write(generate_init_void(class_name, soft_name=soft_name) + "\n")
        else:
            class_file.write(
                generate_init(gen_dict, class_dict, soft_name=soft_name) + "\n"
            )

    # Add the __str__ method
    if "__str__" not in class_dict["methods"]:
        class_file.write(generate_str(gen_dict, class_dict) + "\n")

    # Add the __eq__ method
    if "__eq__" not in class_dict["methods"]:
        class_file.write(generate_eq(gen_dict, class_dict) + "\n")

    # Add the compare method
    if "compare" not in class_dict["methods"]:
        class_file.write(generate_compare(gen_dict, class_dict) + "\n")

    # Add the __sizeof__ method
    class_file.write(generate_size_of(gen_dict, class_dict))

    # Add the as_dict method
    if "as_dict" not in class_dict["methods"]:
        class_file.write(generate_as_dict(gen_dict, class_dict) + "\n")

    # Add the copy method
    if "copy" not in class_dict["methods"]:
        class_file.write(generate_copy(gen_dict, class_dict) + "\n")

    # Add the _set_None method
    if "_set_None" not in class_dict["methods"]:
        class_file.write(generate_set_None(gen_dict, class_dict, soft_name=soft_name))

    # Add all the properties getter and setter
    if len(class_dict["properties"]) > 0:
        class_file.write(
            "\n" + generate_properties(gen_dict, class_dict, soft_name=soft_name) + "\n"
        )

    class_file.writelines(
        TAB + ast.unparse(definition).replace("\n", "\n" + TAB) + "\n\n"
        for definition in class_error_definitions
    )

    # End of class generation
    class_file.close()
    class_path = join(path_to_gen, class_name + ".py")
    if class_error_definitions:
        with open(class_path, "a", encoding="utf-8") as generated_file:
            generated_file.writelines(
                "\n"
                + definition.name
                + " = "
                + class_name
                + "."
                + definition.name
                + "\n"
                for definition in class_error_definitions
            )
    module_class_definitions = CLASS_MODULE_CLASS_DEFINITIONS.get(class_name)
    if module_class_definitions is not None:
        module_path = join(
            dirname(path_to_gen),
            "Methods",
            *module_class_definitions[0].split("."),
            "__init__.py",
        )
        with open(module_path, encoding="utf-8") as module_file:
            module = ast.parse(module_file.read(), filename=module_path)
        definitions = {
            node.name: node for node in module.body if isinstance(node, ast.ClassDef)
        }
        missing_definitions = set(module_class_definitions[1]).difference(definitions)
        if missing_definitions:
            raise ValueError(
                "Could not find configured module classes: "
                + ", ".join(sorted(missing_definitions))
                + " in "
                + module_path
            )
        with open(class_path, "a", encoding="utf-8") as generated_file:
            generated_file.write("\n")
            generated_file.writelines(
                ast.unparse(definitions[name]) + "\n\n"
                for name in module_class_definitions[1]
            )
    with open(class_path, encoding="utf-8") as generated_file:
        source = generated_file.read()
    source = _apply_numpy_import_style(source)
    source = _apply_pyvista_import_style(source)
    source = _apply_os_import_style(source)
    source = _apply_import_style(source, soft_name, import_style)
    source = _organize_header_imports(source, class_name, class_path)
    source = _regroup_pyleecan_imports(source, class_name, class_path)
    with open(class_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(source)


def generate_class_new(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name="pyleecan",
    is_log=True,
    import_style="absolute",
    output_name=None,
):
    """Compatibility wrapper for experimental dataclass generation."""
    return generate_class(
        gen_dict,
        class_name,
        path_to_gen,
        soft_name=soft_name,
        is_log=is_log,
        import_style=import_style,
        is_new=True,
        output_name=output_name,
    )


_BASE_TYPES = {"bool", "complex", "float", "int", "str"}


def _is_none_default(value):
    return value in ("", None, "None")


def _field_type(prop_type, default, gen_dict, soft_name):
    """Return a Python annotation and imports needed for one CSV property."""
    imports = set()

    def resolve_type(type_name):
        if type_name in _BASE_TYPES:
            return type_name
        if type_name == "ndarray":
            imports.add("import numpy as np")
            return "np.ndarray"
        if type_name == "function":
            imports.update(("from typing import Any, Callable",))
            return "Callable[..., Any]"
        if type_name in ("list", "[]"):
            imports.add("from typing import Any")
            return "list[Any]"
        if type_name == "dict":
            imports.add("from typing import Any")
            return "dict[str, Any]"
        if type_name in ("[ndarray]", "{ndarray}"):
            imports.add("import numpy as np")
            return (
                "list[np.ndarray]"
                if type_name == "[ndarray]"
                else "dict[str, np.ndarray]"
            )
        if is_list_pyleecan_type(type_name):
            return f"list[{resolve_type(type_name[1:-1])}]"
        if is_dict_list_pyleecan_type(type_name):
            return f"dict[str, list[{resolve_type(type_name[2:-2])}]]"
        if is_dict_pyleecan_type(type_name):
            return f"dict[str, {resolve_type(type_name[1:-1])}]"

        if type_name in gen_dict:
            imports.add(f"from {soft_name}.Classes.{type_name} import {type_name}")
            return type_name
        if "." in type_name:
            module_name, _, symbol = type_name.rpartition(".")
            imports.add(f"from {module_name} import {symbol}")
            return symbol
        imports.add("from typing import Any")
        return "Any"

    annotation = resolve_type(prop_type) if prop_type else "Any"
    if _is_none_default(default) and annotation not in ("Any", "None"):
        annotation = f"{annotation} | None"
    return annotation, imports


def _referenced_classes(prop_type, gen_dict):
    if prop_type in gen_dict:
        return {prop_type}
    if is_list_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[1:-1], gen_dict)
    if is_dict_list_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[2:-2], gen_dict)
    if is_dict_pyleecan_type(prop_type):
        return _referenced_classes(prop_type[1:-1], gen_dict)
    return set()


def _parent_type(class_name, gen_dict, soft_name):
    """Return the highest-level CSV classes that can own this class."""
    owners = set()
    for owner_name, owner_dict in gen_dict.items():
        if owner_name == class_name:
            continue
        if any(
            class_name in _referenced_classes(prop["type"], gen_dict)
            for prop in owner_dict["properties"]
        ):
            owners.add(owner_name)

    highest_owners = set()
    for owner in owners:
        seen = set()
        while (
            owner in gen_dict
            and gen_dict[owner]["mother"] in gen_dict
            and owner not in seen
        ):
            seen.add(owner)
            owner = gen_dict[owner]["mother"]
        highest_owners.add(owner)

    if not highest_owners:
        return (), set()
    parent_names = sorted(highest_owners)
    imports = {
        f"from {soft_name}.Classes.{name} import {name}" for name in parent_names
    }
    return tuple(parent_names), imports


def _field_default(prop):
    """Format a dataclass default, using field() only when it is required."""
    prop_type = prop["type"]
    value = prop["value"]
    metadata = {}
    if prop.get("as_dict") not in (None, ""):
        metadata["as_dict"] = prop["as_dict"]

    requires_field = False
    if value in ("", None):
        if prop_type in ("list", "[]", "[ndarray]"):
            default = "default_factory=list"
            requires_field = True
        elif prop_type in ("dict", "{ndarray}"):
            default = "default_factory=dict"
            requires_field = True
        else:
            default = "None"
    elif prop_type == "list" and value == -1:
        default = "default_factory=list"
        requires_field = True
    elif prop_type == "dict" and value == -1:
        default = "default_factory=dict"
        requires_field = True
    elif prop_type == "ndarray" and isinstance(value, list):
        default = f"default_factory=partial(deepcopy, np.array({value!r}))"
        requires_field = True
    elif prop_type in ("list", "dict", "[ndarray]", "{ndarray}") and isinstance(
        value, (list, dict)
    ):
        if not value:
            factory = "dict" if prop_type in ("dict", "{ndarray}") else "list"
            default = f"default_factory={factory}"
        else:
            default = f"default_factory=partial(deepcopy, {value!r})"
        requires_field = True
    elif prop_type in PYTHON_TYPE:
        default = get_value_str(value, prop_type)
    elif isinstance(value, str) and value.endswith("()"):
        default = f"default_factory={value[:-2]}"
        requires_field = True
    else:
        default = repr(value)

    if metadata:
        requires_field = True
    if not requires_field:
        return default

    field_args = (
        default if default.startswith("default_factory=") else f"default={default}"
    )
    if metadata:
        field_args += f", metadata={metadata!r}"
    return f"field({field_args})"


def _attribute_docstring(description):
    """Format a CSV description as a safe triple-quoted attribute docstring."""
    escaped_description = repr(description)[1:-1]
    return f'"""{escaped_description}"""'


def _property_description(prop):
    description = prop.get("desc") or ""
    if prop.get("type") == "bool":
        description = re.sub(
            r"(?<![\w.])([01])(?![\w.])",
            lambda match: "True" if match.group(1) == "1" else "False",
            description,
        )
    return description


def _format_source_with_ruff(source, class_path):
    result = subprocess.run(
        ["ruff", "format", "--stdin-filename", class_path, "-"],
        input=source,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    if result.returncode:
        raise RuntimeError(
            "Ruff could not format generated class "
            + class_path
            + ": "
            + (result.stderr or result.stdout).strip()
        )
    return result.stdout


def _display_default(prop):
    value = prop["value"]
    prop_type = prop["type"]
    if value in ("", None, "None"):
        if prop_type == "list":
            return "[]"
        if prop_type == "dict":
            return "{}"
        return "None"
    if prop_type in PYTHON_TYPE:
        return get_value_str(value, prop_type)
    return repr(value)


def _class_docstring(class_dict):
    """Build a NumPy-style class docstring from class and property metadata."""
    description = class_dict.get("desc") or class_dict["name"]
    lines = [description, "", "Attributes", "----------"]
    for prop in class_dict["properties"]:
        prop_type = prop.get("type") or "Any"
        property_description = _property_description(prop)
        if prop.get("value") in ("", None, "None"):
            prop_type += " or None"
        lines.extend(
            [
                f"{prop['name']} : {prop_type}",
                *(
                    [f"    {line}" for line in property_description.splitlines()]
                    if property_description
                    else ["    No description provided."]
                ),
            ]
        )
        details = []
        if prop.get("unit") and prop["unit"] != "-":
            details.append(f"Unit: {prop['unit']}")
        details.append(f"Default: {_display_default(prop)}")
        if prop.get("min") not in (None, ""):
            details.append(f"Minimum: {prop['min']}")
        if prop.get("max") not in (None, ""):
            details.append(f"Maximum: {prop['max']}")
        lines.append(f"    {'; '.join(details)}")
    return '"""' + "\n".join(lines) + '\n"""'


def _generate_dataclass_class(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name,
    import_style,
    output_name,
    method_sources,
    method_imports,
    fallback_reasons,
    class_attributes,
    method_default_overrides,
    class_error_definitions,
):
    """Write an experimental dataclass using the prepared class methods."""
    class_dict = gen_dict[class_name]
    generated_name = class_name
    output_module_name = output_name or class_module_name(class_name)
    class_pack = class_dict["package"]

    class_path = join(path_to_gen, output_module_name + ".py")
    mother = class_dict["mother"]
    if mother in gen_dict:
        parent_class = mother
        parent_module = class_module_name(mother)
    else:
        parent_class = "PyleecanClass"
        parent_module = "_" + class_module_name(parent_class)
    imports = {
        "from dataclasses import dataclass, field",
        "from typing import Any, ClassVar",
        f"from {soft_name}.Classes_new.{parent_module} import {parent_class}",
    }
    parent_types = ()
    if parent_class == "PyleecanClass":
        parent_types, parent_imports = _parent_type(class_name, gen_dict, soft_name)
        imports.update(parent_imports)

    for prop in class_dict["properties"]:
        annotation, type_imports = _field_type(
            prop["type"], prop["value"], gen_dict, soft_name
        )
        imports.update(type_imports)
    if any(
        "default_factory=partial(deepcopy" in _field_default(prop)
        for prop in class_dict["properties"]
    ):
        imports.update(("from copy import deepcopy", "from functools import partial"))

    for method in class_dict["methods"]:
        if method_sources[method] is None:
            imports.add(import_method(class_pack, class_name, method).strip())
    imports.update(ast.unparse(node) for node in method_imports)
    imports.update(
        f"from {soft_name}.Classes.{name} import {name}"
        for name in find_import_type(gen_dict, class_dict, [])
        if name in gen_dict and name != class_name
    )

    chunks = [
        "# Experimental dataclass generated from "
        + class_dict["path"][class_dict["path"].find("Generator") :]
        + "\n",
        '"""Generated experimental dataclass; do not edit by hand."""\n\n',
        "\n".join(sorted(imports)) + "\n\n",
        f"@dataclass(eq=False)\nclass {generated_name}({parent_class}):\n",
        indent(_class_docstring(class_dict), TAB) + "\n\n",
    ]

    body = []
    body.extend(
        f"{TAB}{name}: ClassVar = {value!r}\n"
        for name, value in CLASS_MODULE_CONSTANTS.get(class_name, {}).items()
        if name != "VERSION"
    )
    body.extend(
        f"{TAB}{name}: ClassVar = {expression}\n"
        for name, expression in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(
            class_name, {}
        ).items()
        if name != "VERSION"
    )
    body.extend(
        f"{TAB}{name}: ClassVar = {expression}\n"
        for name, expression in CLASS_BODY_CONSTANTS.get(class_name, {}).items()
        if name != "VERSION"
    )
    body.extend(
        f"{TAB}{constant['name']}: ClassVar = {constant['value']}\n"
        for constant in class_dict["constants"]
        if constant["name"] != "VERSION"
        if constant["name"] not in CLASS_MODULE_CONSTANTS.get(class_name, {})
        and constant["name"]
        not in CLASS_MODULE_CONSTANT_EXPRESSIONS.get(class_name, {})
    )
    body.extend(f"{TAB}{ast.unparse(assignment)}\n" for assignment in class_attributes)

    for prop in class_dict["properties"]:
        annotation, _ = _field_type(prop["type"], prop["value"], gen_dict, soft_name)
        body.append(f"{TAB}{prop['name']}: {annotation} = {_field_default(prop)}\n")
        description = _property_description(prop)
        if description:
            body.append(f"{TAB}{_attribute_docstring(description)}\n")

    if parent_class == "PyleecanClass":
        body.append(f"\n{TAB}def __post_init__(self):\n")
        body.append(f"{TAB}{TAB}super().__post_init__()\n")
        if parent_types:
            accepted_types = ", ".join(parent_types)
            expected_types = " or ".join(parent_types)
            body.extend(
                [
                    f"\n{TAB}def _assert_parent_type(self, parent):\n",
                    f"{TAB}{TAB}if parent is not None and not isinstance(parent, ({accepted_types},)):\n",
                    f"{TAB}{TAB}{TAB}raise TypeError(\n",
                    f'{TAB}{TAB}{TAB}{TAB}"{generated_name} parent must be an instance of {expected_types}, or None; "\n',
                    f'{TAB}{TAB}{TAB}{TAB}+ f"got {{type(parent).__name__}}"\n',
                    f"{TAB}{TAB}{TAB})\n",
                ]
            )

    for method in class_dict["methods"]:
        if method_sources[method] is None:
            body.append(f"\n{TAB}{method.split('.')[-1]} = {method.split('.')[-1]}\n")
            continue
        body.append(
            f"\n{TAB}# Inlined from Methods.{class_pack}.{class_name}.{method}\n"
        )
        body.append(indent(method_sources[method], TAB) + "\n")
        for override in method_default_overrides[method]:
            body.append(f"{TAB}{ast.unparse(override)}\n")
    for definition in class_error_definitions:
        if (
            isinstance(definition, ast.ClassDef)
            and len(definition.body) == 2
            and isinstance(definition.body[0], ast.Expr)
            and isinstance(definition.body[0].value, ast.Constant)
            and isinstance(definition.body[0].value.value, str)
            and isinstance(definition.body[1], ast.Pass)
        ):
            definition.body.pop()
        body.append(
            f"\n{TAB}{ast.unparse(definition).replace(chr(10), chr(10) + TAB)}\n"
        )
    chunks.append("".join(body))
    if class_error_definitions:
        chunks.append(
            "\n"
            + "".join(
                f"{definition.name} = {generated_name}.{definition.name}\n"
                for definition in class_error_definitions
            )
        )
    if fallback_reasons:
        chunks.append(
            "\n# Methods retained as imports because they could not be inlined:\n"
            + "".join(
                f"# {method}: {reason}\n" for method, reason in fallback_reasons.items()
            )
        )

    source = "".join(chunks)
    source = _apply_numpy_import_style(source)
    source = _apply_pyvista_import_style(source)
    source = _apply_os_import_style(source)
    # Inlined methods and their imports were prepared relative to Classes.
    source = _apply_import_style(source, soft_name, "absolute")
    source = _apply_import_style(source, soft_name, import_style, "Classes_new")
    source = _organize_header_imports(source, generated_name, class_path)
    source = _regroup_pyleecan_imports(source, generated_name, class_path)
    source = _organize_header_imports(source, generated_name, class_path)
    source = _format_source_with_ruff(source, class_path)
    with open(class_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(source)
    return class_path
