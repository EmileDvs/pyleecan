import ast
import warnings
from os.path import dirname, join
from textwrap import indent

from ...Generator import TAB
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
)


def _get_method_source(path_to_gen, class_pack, class_name, meth, soft_name):
    """Return a method definition and the imports it needs."""
    method_parts = [part for part in (class_pack or "").split(".") if part]
    method_parts.extend([class_name, *meth.split(".")])
    method_path = join(dirname(path_to_gen), "Methods", *method_parts) + ".py"

    try:
        with open(method_path, encoding="utf-8") as method_file:
            source = method_file.read()
    except FileNotFoundError:
        return None, [], "method source file is missing"

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
        return None, [], "method function is missing"
    if any(
        isinstance(node, ast.ImportFrom) and node.module == "__future__"
        for node in module.body
    ):
        return None, [], "module has a __future__ import"

    used_names = {
        node.id
        for node in ast.walk(method_node)
        if isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load)
    }
    if any(isinstance(node, ast.Global) for node in ast.walk(method_node)):
        return None, [], "method declares module globals"

    helper_bindings = set()
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
                    "module uses a wildcard import whose names cannot be resolved safely",
                )
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            helper_bindings.add(node.name)
            has_module_helpers = True
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            helper_bindings.update(
                child.id
                for target in targets
                for child in ast.walk(target)
                if isinstance(child, ast.Name) and isinstance(child.ctx, ast.Store)
            )
            has_module_helpers = True
        else:
            return (
                None,
                [],
                "module contains unsupported top-level "
                + type(node).__name__
                + " statements",
            )

    source_package = [
        soft_name,
        "Methods",
        *[part for part in (class_pack or "").split(".") if part],
        class_name,
        *meth.split(".")[:-1],
    ]
    target_package = [soft_name, "Classes"]
    method_imports = []

    if has_module_helpers:
        helper_names = sorted(used_names.intersection(helper_bindings))
        if helper_names:
            helper_module = source_package + [method_name]
            common = 0
            while (
                common < len(target_package)
                and common < len(helper_module)
                and target_package[common] == helper_module[common]
            ):
                common += 1
            method_imports.append(
                ast.ImportFrom(
                    module=".".join(helper_module[common:]),
                    names=[ast.alias(name=name) for name in helper_names],
                    level=len(target_package) - common + 1,
                )
            )

    for node in module.body:
        if isinstance(node, ast.Import):
            aliases = [
                alias
                for alias in node.names
                if (alias.asname or alias.name.split(".")[0]) in used_names
            ]
            if aliases:
                method_imports.append(ast.Import(names=aliases))
        elif isinstance(node, ast.ImportFrom):
            aliases = [
                alias
                for alias in node.names
                if alias.name == "*" or (alias.asname or alias.name) in used_names
            ]
            if not aliases:
                continue

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
            method_imports.append(node)

    source_lines = source.splitlines()
    start_line = min(
        [method_node.lineno]
        + [decorator.lineno for decorator in method_node.decorator_list]
    )
    while start_line > 1 and source_lines[start_line - 2].lstrip().startswith("#"):
        start_line -= 1
    method_source = "\n".join(source_lines[start_line - 1 : method_node.end_lineno])
    return method_source, method_imports, None


def _prepare_class_methods(path_to_gen, class_pack, class_name, methods, soft_name):
    """Inline methods and collect their imports without name conflicts."""
    prepared = {}
    fallback_reasons = {}
    imports = []
    import_groups = {}
    import_bindings = {}
    import_keys = set()
    target_package = [soft_name, "Classes"]

    for meth in methods:
        method_source, method_imports, reason = _get_method_source(
            path_to_gen, class_pack, class_name, meth, soft_name
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

        candidate_bindings = {}
        conflict = False
        conflict_name = None
        conflict_imports = None
        for import_node in method_imports:
            for alias in import_node.names:
                binding = alias.asname or (
                    alias.name.split(".")[0]
                    if isinstance(import_node, ast.Import)
                    else alias.name
                )
                identity = _get_import_identity(import_node, alias, target_package)
                existing = import_bindings.get(binding)
                if (existing is not None and existing != identity) or (
                    binding in candidate_bindings
                    and candidate_bindings[binding] != identity
                ):
                    conflict = True
                    conflict_name = binding
                    conflict_imports = (
                        (
                            existing
                            if existing is not None
                            else candidate_bindings[binding]
                        ),
                        identity,
                    )
                    break
                candidate_bindings[binding] = identity
            if conflict:
                break

        if conflict:
            fallback_reason = (
                "import name '"
                + conflict_name
                + "' refers to different sources ("
                + _format_import_identity(conflict_imports[0])
                + " and "
                + _format_import_identity(conflict_imports[1])
                + ")"
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
        import_bindings.update(candidate_bindings)
        for import_node in method_imports:
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

    return prepared, [node for node in imports if node.names], fallback_reasons


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


def _apply_import_style(source, soft_name, import_style):
    """Apply the configured Pyleecan import style without rewriting other code."""
    target_package = [soft_name, "Classes"]
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


def generate_class(
    gen_dict,
    class_name,
    path_to_gen,
    soft_name="pyleecan",
    is_log=True,
    import_style="absolute",
):
    """generate the corresponding class file (erase the previous code)

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

    Returns
    -------
    None

    """

    if import_style not in ("relative", "absolute"):
        raise ValueError("import_style must be 'relative' or 'absolute'")

    class_dict = gen_dict[class_name]
    class_pack = class_dict["package"]
    method_sources, method_imports, fallback_reasons = _prepare_class_methods(
        path_to_gen,
        class_pack,
        class_name,
        class_dict["methods"],
        soft_name,
    )

    # Start of file generation
    # Create or Erase the file by opening it
    class_file = open(join(path_to_gen, class_name + ".py"), "w", encoding="utf-8")

    # List of non python type to import
    import_type_list = list(find_import_type(gen_dict, class_dict, []))
    if class_name in import_type_list:  # For recursive class
        import_type_list.remove(class_name)
    # Encoding
    class_file.write("# -*- coding: utf-8 -*-\n")

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
    if fallback_reasons:
        class_file.write("# Inline fallback report:\n")
        class_file.write(
            "# These methods remain imported because their source or imports cannot "
            "be safely moved into this class.\n"
        )
        for meth, reason in fallback_reasons.items():
            class_file.write("# - " + meth + ": " + reason + "\n")
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
    if len(class_dict["methods"]) > 0:
        class_file.write("# Import all class method\n")
        class_file.write(
            "# Try/catch to remove unnecessary dependencies in unused method\n"
        )
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

    # End of class generation
    class_file.close()
    class_path = join(path_to_gen, class_name + ".py")
    with open(class_path, encoding="utf-8") as generated_file:
        source = generated_file.read()
    source = _apply_import_style(source, soft_name, import_style)
    with open(class_path, "w", encoding="utf-8") as generated_file:
        generated_file.write(source)
