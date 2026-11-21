"""Legacy functions moved to a class as methods (PLAN.md Step 5).

A legacy function that depends on the meaning or the data of one class
becomes a method of that class:

- the method generator writes the function module in the method folder of
  the class (``Methods_new/<sub-package>/<Class>/<method>.py``): the first
  parameter becomes ``self`` (regular method), or the function gets
  ``@staticmethod`` (function not using the object);
- the class generator adds the method to the class (the CSV files are not
  changed: ``add_moved_methods`` extends the generation dictionary);
- the callers in Methods_new and Functions_new call the method
  (``obj.method(...)``; a static method on ``self`` in its class, else on the
  class, imported in the calling function);
- the function generator keeps the old function path in Functions_new as a
  deprecated alias, until Phase 2.

A legacy module can hold several moved functions (a tuple of MovedFunction):
each one gets its own method module, and calls between them go through the
class.
"""

import ast
from importlib.util import resolve_name
from typing import NamedTuple


class MovedFunction(NamedTuple):
    """Legacy function moved to a class."""

    class_name: str
    """Class receiving the method"""
    method: str
    """Name of the method (and of the legacy function)"""
    static: bool = False
    """True: @staticmethod (the function does not use the object)"""
    bound: tuple = ()
    """(parameter, getter): the first parameter of the legacy function is data
    of the object. The legacy body becomes the static method "_<method>", and
    "<method>" a regular method taking that parameter as an optional keyword
    argument, given by ``self.<getter>()`` by default. A caller holding
    ``x = obj.<getter>(...)`` calls ``obj.<method>(..., parameter=x)``; the
    other callers call the static method"""
    function: str = ""
    """Name of the legacy function when it differs from the method
    (``n2dqh_DataTime`` -> ``DataTime.n2dqh``)"""
    local_imports: bool = False
    """True: the class imports of the legacy module go in the method body (the
    class module would import a class depending on it: import cycle)"""
    self_parameter: str = ""
    """Parameter of the legacy function that becomes self, when it is not the
    first one (``comp_MTPA(machine, LUT, ...)`` -> ``LUT.comp_MTPA(machine,
    ...)``); the alias keeps the legacy signature"""

    @property
    def legacy_name(self):
        """Name of the legacy function"""
        return self.function or self.method

    @property
    def implementation(self):
        """Name of the method holding the legacy body"""
        return "_" + self.method if self.bound else self.method

    @property
    def methods(self):
        """Names of the methods added to the class"""
        return (self.implementation, self.method) if self.bound else (self.method,)


MOVED_FUNCTIONS = {
    "MeshSolution.get_area": MovedFunction("MeshSolution", "get_area"),
    "MeshSolution.get_indices_limited": MovedFunction(
        "MeshSolution", "get_indices_limited"
    ),
    "Simulation.VarSimu.run_multisim_step": MovedFunction(
        "VarSimu", "run_multisim_step", static=True
    ),
    # Step 8, group 7 (decision 2026-11-21): the geometry helpers of the
    # laminations and holes
    "Geometry.merge_notch_list": MovedFunction(
        "Lamination", "merge_notch_list", static=True
    ),
    "Geometry.transform_hole_surf": MovedFunction(
        "Hole", "transform_hole_surf", static=True
    ),
    # Step 8, group 4: datakeepers of the multi-simulations
    "Simulation.VarSimu.get_elec_datakeeper_dict": MovedFunction(
        "VarSimu", "get_elec_datakeeper_dict", static=True
    ),
    "Simulation.VarSimu.log_datakeeper_step_result": MovedFunction(
        "VarSimu", "log_datakeeper_step_result", static=True
    ),
    # Step 8, group 3: NSGA-II with DEAP (the functions work on the DEAP
    # individuals of OptiGenAlgNsga2Deap.create_toolbox; OptiBayesAlgSmoot
    # imported them without using them and has its own evaluate)
    "Optimization.evaluate": MovedFunction("OptiGenAlgNsga2Deap", "evaluate"),
    "Optimization.check_cstr": MovedFunction("OptiGenAlgNsga2Deap", "check_cstr"),
    "Optimization.tournamentDCD": MovedFunction(
        "OptiGenAlgNsga2Deap", "tournamentDCD", static=True
    ),
    "Optimization.update": MovedFunction("OptiGenAlgNsga2Deap", "update", static=True),
    # Step 8: n phases to dqh transformation of the Data objects (the other
    # functions of these modules are merged in SciDataTool.dqh_transformation,
    # MERGED_MODULES; DataDual.n2dqh is a new method, NEW_METHODS)
    "Electrical.dqh_transformation": (
        MovedFunction("DataTime", "n2dqh", function="n2dqh_DataTime"),
        MovedFunction("DataTime", "dqh2n", function="dqh2n_DataTime"),
    ),
    "Electrical.dqh_transformation_freq": (
        MovedFunction("DataFreq", "n2dqh", function="n2dqh_DataFreq"),
        MovedFunction("DataFreq", "dqh2n", function="dqh2n_DataFreq"),
    ),
    # Step 8, group 9: animation of any plot of Data objects (no caller)
    # Step 8, group 8: MTPA from the LUT of a machine (no caller)
    "Electrical.comp_MTPA": MovedFunction(
        "LUTdq", "comp_MTPA", self_parameter="LUT", local_imports=True
    ),
    "Plot.animate_as_gif": MovedFunction(
        "Data", "animate_as_gif", static=True, local_imports=True
    ),
    # Step 8, group 5: solution constructors; the magnetic meshsolution of an
    # output and the frame suffix of a group (it reads output.mag)
    "MeshSolution.build_solution_data": MovedFunction(
        "SolutionData", "build_solution_data", static=True
    ),
    "MeshSolution.build_solution_vector": MovedFunction(
        "SolutionVector", "build_solution_vector", static=True
    ),
    "MeshSolution.get_frame_meshsolution": MovedFunction(
        "Output", "get_frame_meshsolution"
    ),
    # Step 8, group 2: winding matrix operations (Winding), single conductor
    # winding function (Conductor); gen_phase_list stays a utility
    "Winding.comp_cond_function": MovedFunction(
        "Conductor", "comp_cond_function", static=True
    ),
    "Winding.reverse_wind_mat": (
        MovedFunction("Winding", "reverse_wind_mat", static=True),
        MovedFunction("Winding", "reverse_layer", static=True),
        MovedFunction("Winding", "change_layer", static=True),
        MovedFunction("Winding", "permute_B_C", static=True),
    ),
    "Winding.shift_wind_mat": MovedFunction("Winding", "shift_wind_mat", static=True),
    # get_phase_id reads the connection matrix of the winding (regular method,
    # wind_mat optional); find_wind_phase_color stays static: the plots call
    # it without matrix on purpose (no winding, WindingSC: first phase color)
    "Winding.find_wind_phase_color": (
        MovedFunction("Winding", "find_wind_phase_color", static=True),
        MovedFunction(
            "Winding", "get_phase_id", bound=("wind_mat", "get_connection_mat")
        ),
    ),
}
"""{legacy function module below Functions: MovedFunction or tuple of them}"""

DEPRECATION_MESSAGE = "{function} is deprecated, use {target} (removed in Phase 2)"

REMOVED_FUNCTION_ALIASES = {
    # Deleted upstream (#751): it only called the MeshSolution constructor
    "MeshSolution.build_meshsolution": '''"""Deprecated alias of the MeshSolution constructor (removed in Phase 2)."""

from warnings import warn


def build_meshsolution(solution_dict, mesh, label="", dimension=2, group=None):
    """Deprecated: use MeshSolution(label=, mesh=, solution_dict=, dimension=, group=)"""
    from ...Classes.MeshSolution import MeshSolution

    warn(
        "build_meshsolution is deprecated, use MeshSolution(label=..., mesh=..., "
        "solution_dict=..., dimension=..., group=...) (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return MeshSolution(
        label=label, mesh=mesh, solution_dict=solution_dict, dimension=dimension, group=group
    )
''',
}
"""{legacy module below Functions, deleted from the legacy code: source of its
deprecated alias in Functions_new} (written by the functions generator)"""

DEPRECATED_MODULES = {
    # Step 8: replaced by the methods of the SciDataTool classes
    "Plot.plot_2D_Data": "use the plot_2D_Data method of the Data object",
    "Plot.plot_3D_Data": "use the plot_3D_Data method of the Data object",
    # Imported by LUTdq.interp_Ploss_dqh and LossModelWinding.comp_loss, never
    # called (the Joule losses are computed by LossModelJoule)
    "Electrical.comp_loss_joule": "it is not used by pyleecan",
    # Step 9: the loggers without the parent chain
    "get_logger": "use classes_common.logger_context.get_logger",
    # Step 8: no MotorCAD rule uses it (add_rule_slotW23 converts H1 with a
    # simple rule)
    "Converter.MotorCAD.slotW23_H1": "it is not used by the MotorCAD conversion rules",
    # Step 8 group 1 (decision 2026-11-21): dead code, no caller in pyleecan
    # (the FEMM and pyvista ones are left out of femm_pyleecan /
    # pv_plotter_pyleecan, at their legacy path)
    "Plot.Pyvista.get_arrows_plt": "it is not used by pyleecan",
    "Geometry.create_surface": "it is not used by pyleecan",
    "FEMM.comp_FEMM_Jcus": "it is not used by pyleecan",
    "FEMM.create_FEMM_bar": "it is not used by pyleecan",
    "getattr_recursive": "it is not used by pyleecan",
    "short_filepath": "it is not used by pyleecan",
}
"""{legacy module below Functions: replacement}: the public functions of the
module warn (DeprecationWarning) in Functions_new, removed in Phase 2"""


MERGED_MODULES = {
    # The dqh transformations next to the other SciDataTool utilities; the
    # Data object functions are methods (n2dqh_DataTime -> DataTime.n2dqh,
    # n2dqh_DataFreq -> DataFreq.n2dqh); the checks of the DataND axes are
    # dropped
    "SciDataTool.dqh_transformation": {
        "sources": (
            ("Electrical.dqh_transformation", {}),
            (
                "Electrical.dqh_transformation_freq",
                {
                    "n2dqh": "n2dqh_freq",
                    "abc2dqh": "abc2dqh_freq",
                    "dqh2n": "dqh2n_freq",
                    "dqh2abc": "dqh2abc_freq",
                    "get_phase_dir": "get_phase_dir_freq",
                },
            ),
        ),
        "dropped": ("_check_data", "_check_DataTime", "_check_DataFreq"),
    },
    # Structural.conversions deprecated (decision 2026-11-21): its functions in
    # SciDataTool.conversions. xyz_to_rphiz, xyz_to_rphiz_field and
    # rphiz_to_xyz_field give the same results as the SciDataTool ones
    # (identical); cart2pol / pol2cart (angle from the points) and
    # rphiz_to_xyz (z kept) are different functions (renamed)
    "SciDataTool.conversions": {
        "sources": (
            ("SciDataTool.conversions", {}),
            (
                "Structural.conversions",
                {
                    "cart2pol": "cart2pol_points",
                    "pol2cart": "pol2cart_points",
                    "rphiz_to_xyz": "rphiz_to_xyz_3d",
                },
            ),
        ),
        "dropped": (),
        "identical": ("xyz_to_rphiz", "xyz_to_rphiz_field", "rphiz_to_xyz_field"),
        "errors": ("DimError",),
    },
    # Step 8 group 7 (decision 2026-11-21): the geometry utilities in one
    # module of the utils package
    "utils.geometry": {
        "sources": tuple(
            (f"Geometry.{module}", {})
            for module in (
                "inter_line_circle",
                "inter_line_line",
                "inter_circle_circle",
                "circle_from_3_points",
                "comp_flower_arc",
                "cut_lines_between_angle",
                "comp_surface_num",
            )
        ),
        "dropped": (),
    },
}
"""{new module below Functions: {"sources": ((legacy module, {function: new
name}), ...), "dropped": functions removed with their calls}}: the functions of
the legacy modules (except the moved ones) in one module of Functions_new; the
legacy paths are deprecated aliases"""

NEW_METHODS = {
    "DataDual": {
        # DataDual holds the time (axes_dt, values_dt) and frequency data: the
        # transformation of its DataTime (the checks of the legacy function
        # switched the axes and values of the object to the time ones)
        "n2dqh": '''def n2dqh(self, is_dqh_rms=True, phase_dir=None):
    """n phases to dqh equivalent coordinate transformation of the time data

    Parameters
    ----------
    self : DataDual
        A DataDual object
    is_dqh_rms : bool
        True to return dq currents in rms value (Pyleecan convention), False to return peak values
    phase_dir : int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_dqh : DataTime
        data object transformed in dqh frame
    """
    from ....Classes.DataTime import DataTime

    data_time = DataTime(
        name=self.name,
        unit=self.unit,
        symbol=self.symbol,
        axes=self.axes_dt,
        values=self.values_dt,
        normalizations=self.normalizations,
        is_real=self.is_real,
    )
    return data_time.n2dqh(is_dqh_rms=is_dqh_rms, phase_dir=phase_dir)
''',
        # Same for the inverse transformation (DataTime.dqh2n)
        "dqh2n": '''def dqh2n(self, n, is_n_rms=False, phase_dir=None):
    """dqh to n phase coordinate transformation of the time data

    Parameters
    ----------
    self : DataDual
        A DataDual object
    n : int
        number of phases
    is_n_rms : bool
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir : int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_n : DataTime
        data object containing values over time in n phase frame
    """
    from ....Classes.DataTime import DataTime

    data_time = DataTime(
        name=self.name,
        unit=self.unit,
        symbol=self.symbol,
        axes=self.axes_dt,
        values=self.values_dt,
        normalizations=self.normalizations,
        is_real=self.is_real,
    )
    return data_time.dqh2n(n=n, is_n_rms=is_n_rms, phase_dir=phase_dir)
''',
    },
}
"""{class: {method: source}}: methods without legacy source, written by the
method generator in Methods_new (legacy-style imports, as the other method
modules)"""


def merged_sources():
    """Legacy modules merged into another module."""
    return [
        module
        for spec in MERGED_MODULES.values()
        for module, _ in spec["sources"]
    ]


def merged_location(legacy_module):
    """(new module, {function: new name}) of a merged legacy module, or None."""
    for new_module, spec in MERGED_MODULES.items():
        for module, renames in spec["sources"]:
            if module == legacy_module:
                return new_module, renames
    return None


def _merged_spec(legacy_module):
    for new_module, spec in MERGED_MODULES.items():
        if legacy_module in [module for module, _ in spec["sources"]]:
            return new_module, spec
    return None, None


def _remove_statements(source, predicate):
    """Remove the statements matching predicate (a block left empty gets pass,
    an else left empty is removed)."""
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    removals = []  # (first line, last line, replacement)
    for parent in ast.walk(tree):
        for field in ("body", "orelse", "finalbody"):
            block = getattr(parent, field, None)
            if not isinstance(block, list) or not block:
                continue
            removed = [stmt for stmt in block if isinstance(stmt, ast.stmt) and predicate(stmt)]
            if not removed:
                continue
            if len(removed) == len(block):
                if field == "orelse" and isinstance(parent, (ast.If, ast.For, ast.While)) and not (
                    isinstance(parent, ast.If) and len(block) == 1 and isinstance(block[0], ast.If)
                ):
                    # Remove "else:" with the block (and the comments between)
                    else_line = block[0].lineno - 2
                    while else_line > 0 and not lines[else_line].strip().startswith("else"):
                        else_line -= 1
                    removals.append((else_line, block[-1].end_lineno, ""))
                    continue
                indent = " " * block[0].col_offset
                removals.append((block[0].lineno - 1, block[-1].end_lineno, indent + "pass\n"))
                continue
            for stmt in removed:
                first = stmt.lineno - 1
                # The comment lines just above the statement go with it
                while first > 0 and lines[first - 1].strip().startswith("#"):
                    first -= 1
                removals.append((first, stmt.end_lineno, ""))
    for first, last, text in sorted(removals, reverse=True):
        lines[first:last] = [text] if text else []
    return "".join(lines)


def _is_call_of(stmt, names):
    return (
        isinstance(stmt, ast.Expr)
        and isinstance(stmt.value, ast.Call)
        and isinstance(stmt.value.func, ast.Name)
        and stmt.value.func.id in names
    )


def _imports_merged_module(stmt, package):
    """True for an import from one of the merged legacy modules."""
    if not isinstance(stmt, ast.ImportFrom):
        return False
    module = (
        resolve_name("." * stmt.level + (stmt.module or ""), package)
        if stmt.level
        else stmt.module
    )
    return module is not None and module.removeprefix("pyleecan.Functions.") in merged_sources()


def drop_merged_calls(source, legacy_module):
    """Remove the calls of the dropped functions of a merged module."""
    _, spec = _merged_spec(legacy_module)
    if spec is None or not spec["dropped"]:
        return source
    dropped = set(spec["dropped"])
    source = _remove_statements(source, lambda stmt: _is_call_of(stmt, dropped))
    # The imports of the dropped functions (from the other merged module)
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    replacements = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.ImportFrom) or not any(
            alias.name in dropped for alias in node.names
        ):
            continue
        kept = [alias for alias in node.names if alias.name not in dropped]
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        text = (
            ast.unparse(ast.ImportFrom(module=node.module, names=kept, level=node.level))
            if kept
            else "pass"  # Removed by the next pass if it is not alone in its block
        )
        replacements.append((start, end, text))
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return _remove_statements(
        source,
        lambda stmt: isinstance(stmt, ast.Pass)
        and stmt.col_offset == 0,  # Module-level import left empty
    )


def _rename_names(source, renames):
    """Rename the functions and the names of renames {old: new} in source."""
    if not renames:
        return source
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    replacements = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Name) and node.id in renames:
            start = offsets[node.lineno - 1] + node.col_offset
            replacements.append((start, start + len(node.id), renames[node.id]))
        elif isinstance(node, ast.FunctionDef) and node.name in renames:
            start = offsets[node.lineno - 1]
            start += source[start:].index("def " + node.name) + 4
            replacements.append((start, start + len(node.name), renames[node.name]))
    for start, end, text in sorted(replacements, reverse=True):
        source = source[:start] + text + source[end:]
    return source


def merged_module_source(new_module, read_source):
    """Legacy-style source of a merged module (MERGED_MODULES).

    Parameters
    ----------
    new_module : str
        Merged module below Functions ("SciDataTool.dqh_transformation")
    read_source : callable
        legacy module below Functions -> its source

    Returns
    -------
    source : str
        Imports and functions of the legacy modules, the moved functions and
        the dropped ones (with their calls) removed, the functions renamed
    """
    spec = MERGED_MODULES[new_module]
    package = ".".join(["pyleecan", "Functions", *new_module.split(".")[:-1]])
    imports, functions = [], []
    for legacy_module, renames in spec["sources"]:
        old_package = ".".join(["pyleecan", "Functions", *legacy_module.split(".")[:-1]])
        source = read_source(legacy_module)
        source = drop_merged_calls(source, legacy_module)
        # Local imports of the other merged modules: the names are in this module
        source = _remove_statements(
            source, lambda stmt: _imports_merged_module(stmt, old_package)
        )
        source = _rename_names(source, renames)
        source = _relocate_relative_imports(source, old_package, package)
        moved = {
            target.legacy_name for target in moved_targets(MOVED_FUNCTIONS.get(legacy_module, ()))
        }
        tree = ast.parse(source)
        lines = source.splitlines(keepends=True)
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                text = ast.unparse(node)
                if text not in imports:
                    imports.append(text)
            elif isinstance(node, ast.FunctionDef):
                if node.name in moved or node.name in spec["dropped"]:
                    continue
                if legacy_module != spec["sources"][0][0] and node.name in spec.get(
                    "identical", ()
                ):
                    continue  # Same function in the first module
                first = node.lineno - 1 - len(node.decorator_list)
                functions.append("".join(lines[first : node.end_lineno]).rstrip() + "\n")
            elif isinstance(node, (ast.Assign, ast.AnnAssign)):  # Constants
                first = node.lineno - 1
                functions.insert(
                    len([f for f in functions if not f.startswith("def ")]),
                    "".join(lines[first : node.end_lineno]).rstrip() + "\n",
                )
            elif isinstance(node, ast.ClassDef) and node.name in spec.get("errors", ()):
                # Shared errors (classes_common.errors)
                text = ast.unparse(
                    ast.ImportFrom(
                        module="classes_common.errors",
                        names=[ast.alias(node.name)],
                        level=len(package.split(".")),
                    )
                )
                if text not in imports:
                    imports.append(text)
            elif not (
                isinstance(node, ast.Expr)
                and isinstance(node.value, ast.Constant)
                and isinstance(node.value.value, str)
            ):
                raise ValueError(f"{legacy_module}: unsupported top-level statement in a merged module")
    # Class imports in the functions: the classes import the merged module
    # (their methods use its functions), no import cycle
    class_imports = {}  # local name: import line
    module_imports = []
    for text in imports:
        node = ast.parse(text).body[0]
        module = (
            resolve_name("." * node.level + (node.module or ""), package)
            if isinstance(node, ast.ImportFrom) and node.level
            else getattr(node, "module", None)
        )
        if isinstance(node, ast.ImportFrom) and module and module.startswith("pyleecan.Classes."):
            for alias in node.names:
                class_imports[alias.asname or alias.name] = ast.unparse(
                    ast.ImportFrom(module=node.module, names=[alias], level=node.level)
                )
        else:
            module_imports.append(text)
    localized = []
    for function in functions:
        node = ast.parse(function).body[0]
        used = sorted(
            {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}.intersection(class_imports)
        )
        if used:
            first = node.body[1] if ast.get_docstring(node) is not None and len(node.body) > 1 else node.body[0]
            lines = function.splitlines(keepends=True)
            indent = " " * first.col_offset
            lines.insert(
                first.lineno - 1,
                "".join(indent + class_imports[name] + "\n" for name in used) + "\n",
            )
            function = "".join(lines)
        localized.append(function)
    origins = ", ".join(module for module, _ in spec["sources"])
    header = f'"""Functions merged from {origins} (PLAN.md Step 8)."""\n\n'
    return header + "\n".join(module_imports) + "\n\n\n" + "\n\n".join(localized)


def merged_alias_source(legacy_module, source):
    """Deprecated aliases of a merged legacy module (and of its moved functions).

    Parameters
    ----------
    legacy_module : str
        Legacy module below Functions
    source : str
        Its legacy source

    Returns
    -------
    source : str
        One deprecated alias per public function: the method for a moved
        function, the function of the merged module otherwise
    """
    new_module, renames = merged_location(legacy_module)
    _, spec = _merged_spec(legacy_module)
    moved_value = MOVED_FUNCTIONS.get(legacy_module)
    moved = moved_targets(moved_value) if moved_value is not None else ()
    moved_names = {target.legacy_name for target in moved}
    text = alias_source(legacy_module, moved) if moved else (
        f'"""Deprecated aliases (merged into {new_module}, removed in Phase 2)."""\n\nfrom warnings import warn\n'
    )
    up = "." * (len(legacy_module.split(".")) + 1)
    new_import = up + "Functions." + new_module
    errors = [
        node.name
        for node in ast.parse(source).body
        if isinstance(node, ast.ClassDef) and node.name in spec.get("errors", ())
    ]
    if errors:  # The shared errors of the legacy module
        text += f"from {up}classes_common.errors import {', '.join(errors)}  # noqa: F401\n"
    for node in ast.parse(source).body:
        if (
            not isinstance(node, ast.FunctionDef)
            or node.name.startswith("_")
            or node.name in moved_names
            or node.name in spec["dropped"]
        ):
            continue
        new_name = renames.get(node.name, node.name)
        message = DEPRECATION_MESSAGE.format(
            function=node.name, target=f"{new_module}.{new_name}"
        )
        text += (
            f"\n\ndef {node.name}(*args, **kwargs):\n"
            f'    """Deprecated: use {new_module}.{new_name}"""\n'
            f"    from {new_import} import {new_name} as function\n\n"
            f'    warn("{message}", DeprecationWarning, stacklevel=2)\n'
            f"    return function(*args, **kwargs)\n"
        )
    return text


def deprecate_source(source, replacement):
    """Add a DeprecationWarning at the start of the public functions of a module.

    Parameters
    ----------
    source : str
        Source of the legacy function module
    replacement : str
        What to use instead (in the message)

    Returns
    -------
    source : str
        Source warning on each call of its public functions
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    inserts = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef) or node.name.startswith("_"):
            continue
        message = f"{node.name} is deprecated, {replacement} (removed in Phase 2)"
        first = node.body[1] if ast.get_docstring(node) is not None and len(node.body) > 1 else node.body[0]
        indent = " " * first.col_offset
        inserts.append(
            (first.lineno - 1, f"{indent}warn({message!r}, DeprecationWarning, stacklevel=2)\n")
        )
    if not inserts:
        return source
    for index, text in sorted(inserts, reverse=True):
        lines.insert(index, text)
    # Import after the module docstring and the __future__ imports
    position = 0
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ) or (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
            position = node.end_lineno
        else:
            break
    lines.insert(position, "from warnings import warn\n")
    return "".join(lines)


def moved_targets(value):
    """The MovedFunction of a MOVED_FUNCTIONS value, as a tuple."""
    return (value,) if isinstance(value, MovedFunction) else tuple(value)


def all_moved_targets(moved=None):
    """[(legacy module, MovedFunction)] of all the moved functions."""
    moved = MOVED_FUNCTIONS if moved is None else moved
    return [
        (module, target) for module, value in moved.items() for target in moved_targets(value)
    ]


def add_moved_methods(gen_dict, moved=None):
    """Add the moved functions to the method lists of the generation dictionary.

    Parameters
    ----------
    gen_dict : dict
        Generation dictionary (changed in place)
    moved : dict, optional
        {legacy module: MovedFunction} (default: MOVED_FUNCTIONS)

    Returns
    -------
    gen_dict : dict
        The same dictionary
    """
    for _, target in all_moved_targets(moved):
        methods = gen_dict[target.class_name]["methods"]
        for name in target.methods:
            if name not in methods:
                methods.append(name)
    if moved is None:  # Methods without legacy source
        for class_name, new_methods in NEW_METHODS.items():
            if class_name in gen_dict:
                methods = gen_dict[class_name]["methods"]
                methods.extend(name for name in new_methods if name not in methods)
    return gen_dict


def _line_offsets(source):
    offsets = [0]
    for line in source.splitlines(keepends=True):
        offsets.append(offsets[-1] + len(line))
    return offsets


def _function_node(tree, name):
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return node
    raise ValueError(f"Function {name} not found")


def _relocate_relative_imports(source, old_package, new_package):
    """Rewrite the relative imports of a module moved to another package."""
    offsets = _line_offsets(source)
    replacements = []
    for node in ast.walk(ast.parse(source)):
        if not isinstance(node, ast.ImportFrom) or not node.level:
            continue
        absolute = resolve_name("." * node.level + (node.module or ""), old_package)
        package_parts = new_package.split(".")
        target_parts = absolute.split(".")
        common = 0
        while (
            common < min(len(package_parts), len(target_parts))
            and package_parts[common] == target_parts[common]
        ):
            common += 1
        replacement = ast.ImportFrom(
            module=".".join(target_parts[common:]) or None,
            names=node.names,
            level=len(package_parts) - common + 1,
        )
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        replacements.append((start, end, ast.unparse(replacement)))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def _split_moved_siblings(source, module_name, siblings, renames=None, method_name=None):
    """Remove the other functions of the module, imported instead.

    The import from the legacy module (``from .module import sibling``) is
    then rewritten by ``redirect_moved_calls`` into calls on the class.
    ``module_name`` is a module of the same folder, or a relative module
    (``..SciDataTool.dqh_transformation``, a merged module); ``renames``
    {name: name in that module} imports ``new as name``. A function of a
    merged module with the name of the method (``n2dqh`` in
    ``DataTime.n2dqh``) is imported as ``<name>_fct``.
    """
    renames = dict(renames or {})
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    removed = []
    for node in reversed(tree.body):
        if isinstance(node, ast.FunctionDef) and node.name in siblings:
            first = node.lineno - 1 - len(node.decorator_list)
            del lines[first : node.end_lineno]
            removed.append(node.name)
    if not removed:
        return source
    source = "".join(lines)
    used = {
        node.id for node in ast.walk(ast.parse(source)) if isinstance(node, ast.Name)
    }
    imported = sorted(name for name in removed if name in used)
    if not imported:
        return source
    if module_name.startswith("..") and method_name in imported:
        # Same name as the method: imported as <name>_fct
        local = method_name + "_fct"
        source = _rename_names(source, {method_name: local})
        renames[local] = renames.get(method_name, method_name)
        imported = sorted(local if name == method_name else name for name in imported)
    # After the module docstring and the __future__ imports
    tree = ast.parse(source)
    position = 0
    for node in tree.body:
        if (
            isinstance(node, ast.Expr)
            and isinstance(node.value, ast.Constant)
            and isinstance(node.value.value, str)
        ) or (isinstance(node, ast.ImportFrom) and node.module == "__future__"):
            position = node.end_lineno
        else:
            break
    lines = source.splitlines(keepends=True)
    module = module_name if module_name.startswith(".") else "." + module_name

    def import_line(names, indent=""):
        aliases = ", ".join(
            f"{renames[name]} as {name}" if renames.get(name, name) != name else name
            for name in names
        )
        return f"{indent}from {module} import {aliases}\n"

    if not module_name.startswith(".."):
        lines.insert(position, import_line(imported))
        return "".join(lines)
    # Merged module: imported in the functions (the merged module imports the
    # classes, which import their methods: no import cycle)
    inserts = []
    for node in tree.body:
        if not isinstance(node, ast.FunctionDef):
            continue
        used_here = sorted(
            {n.id for n in ast.walk(node) if isinstance(n, ast.Name)}.intersection(imported)
        )
        if not used_here:
            continue
        first = node.body[1] if ast.get_docstring(node) is not None and len(node.body) > 1 else node.body[0]
        inserts.append((first.lineno - 1, import_line(used_here, " " * first.col_offset)))
    for index, text in sorted(inserts, reverse=True):
        lines.insert(index, text + "\n")
    return "".join(lines)


def _move_parameter_first(source, function_name, parameter):
    """Move a positional parameter (without default) to the first position."""
    node = _function_node(ast.parse(source), function_name)
    arguments = node.args.args
    names = [argument.arg for argument in arguments]
    if parameter not in names:
        raise ValueError(f"{function_name}: no parameter {parameter}")
    index = names.index(parameter)
    if index >= len(names) - len(node.args.defaults):
        raise ValueError(f"{function_name}: {parameter} must not have a default")
    if index == 0:
        return source
    offsets = _line_offsets(source)
    argument = arguments[index]
    start = offsets[argument.lineno - 1] + argument.col_offset
    following = arguments[index + 1]
    end = offsets[following.lineno - 1] + following.col_offset
    first = arguments[0]
    first_start = offsets[first.lineno - 1] + first.col_offset
    source = source[:start] + source[end:]  # Remove "LUT,\n    "
    return source[:first_start] + parameter + ", " + source[first_start:]


def _self_parameter_alias(source, target, message):
    """Alias keeping the legacy signature, calling the method on the parameter."""
    node = _function_node(ast.parse(source), target.legacy_name)
    names = [argument.arg for argument in node.args.args]
    call = ", ".join(name for name in names if name != target.self_parameter)
    return [
        f"def {target.legacy_name}({ast.unparse(node.args)}):",
        f'    """Deprecated: use {target.class_name}.{target.method}"""',
        f'    warn("{message}", DeprecationWarning, stacklevel=2)',
        f"    return {target.self_parameter}.{target.method}({call})",
    ]


def _localize_class_imports(source, package, function_name):
    """Move the module-level class imports into the body of the function.

    The comment above them keeps them local in the generated class (the class
    generator hoists the other method imports to the class module).
    """
    tree = ast.parse(source)
    lines = source.splitlines(keepends=True)
    moved, removals = [], []
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        module = (
            resolve_name("." * node.level + (node.module or ""), package)
            if node.level
            else node.module
        )
        if module and module.startswith("pyleecan.Classes."):
            moved.append(ast.unparse(node))
            removals.append((node.lineno - 1, node.end_lineno))
    if not moved:
        return source
    function = _function_node(tree, function_name)
    first = function.body[1] if ast.get_docstring(function) is not None and len(function.body) > 1 else function.body[0]
    indent = " " * first.col_offset
    block = (
        f"{indent}# Local import: circular import with the class module\n"
        + "".join(f"{indent}{text}\n" for text in moved)
        + "\n"
    )
    lines.insert(first.lineno - 1, block)
    for first_line, last_line in sorted(removals, reverse=True):
        del lines[first_line:last_line]
    return "".join(lines)


def method_source(source, target, old_package, new_package, siblings=()):
    """Source of the method module of a moved function.

    Parameters
    ----------
    source : str
        Source of the legacy function module
    target : MovedFunction
        Where the function goes
    old_package : str
        Package of the legacy module ("pyleecan.Functions.MeshSolution")
    new_package : str
        Package of the method module ("pyleecan.Methods.MeshSolution")
    siblings : tuple, optional
        (legacy module name, names of the other moved functions of the module):
        removed from the method module, imported from the legacy module (calls
        redirected to the class by redirect_moved_calls)

    Returns
    -------
    source : str
        Source of the method module
    """
    if siblings:
        module_name, names = siblings[:2]
        renames = siblings[2] if len(siblings) > 2 else {}
        source = _split_moved_siblings(
            source, module_name, set(names), renames, method_name=target.method
        )
    if target.local_imports:
        source = _localize_class_imports(source, old_package, target.legacy_name)
    source = _relocate_relative_imports(source, old_package, new_package)
    # Name of the method: "_<method>" (bound), the method name (renamed)
    new_name = target.implementation
    if new_name != target.legacy_name:
        node = _function_node(ast.parse(source), target.legacy_name)
        start = _line_offsets(source)[node.lineno - 1]
        name_start = start + source[start:].index("def " + target.legacy_name) + 4
        source = (
            source[:name_start] + new_name + source[name_start + len(target.legacy_name) :]
        )
    if target.self_parameter:  # The parameter becoming self goes first
        source = _move_parameter_first(source, new_name, target.self_parameter)
    node = _function_node(ast.parse(source), new_name)
    offsets = _line_offsets(source)
    if target.static or target.bound:
        start = offsets[node.lineno - 1]
        return source[:start] + "@staticmethod\n" + source[start:]
    if not node.args.args:
        raise ValueError(f"{target.method} has no parameter to become self")
    first = node.args.args[0].arg
    positions = [node.args.args[0]]
    positions.extend(
        name
        for name in ast.walk(node)
        if isinstance(name, ast.Name) and name.id == first
    )
    replacements = []
    for item in positions:
        start = offsets[item.lineno - 1] + item.col_offset
        replacements.append((start, start + len(first), "self"))
    docstring = node.body[0] if ast.get_docstring(node) is not None else None
    if docstring is not None:
        doc_start = offsets[docstring.lineno - 1] + docstring.col_offset
        doc_end = offsets[docstring.end_lineno - 1] + docstring.end_col_offset
        text = source[doc_start:doc_end]
        lines = text.split("\n")
        for index, line in enumerate(lines):
            stripped = line.lstrip()
            if stripped.split(":")[0].strip() == first and ":" in stripped:
                indent = line[: len(line) - len(stripped)]
                lines[index] = indent + "self" + stripped[len(first) :]
                break
        replacements.append((doc_start, doc_end, "\n".join(lines)))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source


def bound_method_source(source, target):
    """Source of the regular method of a bound moved function.

    ``get_phase_id(wind_mat, Nrad, Ntan, Zs)`` with bound=("wind_mat",
    "get_connection_mat") becomes::

        def get_phase_id(self, Nrad, Ntan, Zs, wind_mat=None):
            if wind_mat is None:
                wind_mat = self.get_connection_mat()
            return self._get_phase_id(wind_mat, Nrad, Ntan, Zs)

    The docstring of the legacy function is kept (with ``self`` and the
    default of the bound parameter documented).
    """
    parameter, getter = target.bound
    node = _function_node(ast.parse(source), target.legacy_name)
    arguments = node.args
    if arguments.posonlyargs or arguments.vararg or arguments.kwarg or arguments.kwonlyargs:
        raise ValueError(f"{target.method}: only positional parameters are supported")
    names = [argument.arg for argument in arguments.args]
    if not names or names[0] != parameter:
        raise ValueError(f"{target.method}: the first parameter must be {parameter}")
    defaults = dict(zip(names[len(names) - len(arguments.defaults) :], arguments.defaults))
    if parameter in defaults:
        raise ValueError(f"{target.method}: {parameter} must not have a default")
    signature = ["self"] + [
        name + ("=" + ast.unparse(defaults[name]) if name in defaults else "")
        for name in names[1:]
    ] + [parameter + "=None"]
    lines = [f"def {target.method}({', '.join(signature)}):"]
    docstring = ast.get_docstring(node, clean=True)
    if docstring is not None:
        doc_lines = docstring.split("\n")
        for index, line in enumerate(doc_lines):
            if line.strip() == "----------" and index and doc_lines[index - 1].strip() == "Parameters":
                doc_lines[index + 1 : index + 1] = [
                    f"self : {target.class_name}",
                    f"    A {target.class_name} object",
                ]
                break
        for index, line in enumerate(doc_lines):
            if line.split(":")[0].strip() == parameter and ":" in line:
                end = index + 1
                while end < len(doc_lines) and doc_lines[end].startswith("    "):
                    end += 1
                doc_lines.insert(end, f"    (default: self.{getter}())")
                break
        body = "\n".join(("    " + line).rstrip() for line in doc_lines)
        lines.append('    """' + body.lstrip() + "\n    " + '"""')
    lines += [
        f"    if {parameter} is None:",
        f"        {parameter} = self.{getter}()",
        f"    return self.{target.implementation}({', '.join(names)})",
    ]
    return "\n".join(lines) + "\n"


def alias_source(legacy_module, target, source=None):
    """Legacy source of the deprecated aliases kept at the old function path.

    The alias goes through the function generator like the other legacy
    function modules (class imports relocated, pydantic rewriting). ``target``
    is a MovedFunction or a tuple of them (one alias per moved function of the
    module).
    """
    targets = moved_targets(target)
    depth = len(legacy_module.split("."))  # Functions/<...>/<module>.py
    up = "." * (depth + 1)
    moved_names = ", ".join(f"{t.class_name}.{t.method}" for t in targets)
    lines = [
        f'"""Deprecated alias of {moved_names} (moved to the class, removed in Phase 2)."""',
        "",
        "from warnings import warn",
    ]
    for item in targets:
        message = DEPRECATION_MESSAGE.format(
            function=item.legacy_name, target=f"{item.class_name}.{item.method}"
        )
        lines += ["", ""]
        if item.self_parameter:  # Legacy signature, method on that parameter
            if source is None:
                raise ValueError(f"{legacy_module}: the legacy source is required")
            lines += _self_parameter_alias(source, item, message)
        elif item.static or item.bound:  # Legacy signature: the static method
            lines += [
                f"def {item.legacy_name}(*args, **kwargs):",
                f'    """Deprecated: use {item.class_name}.{item.method}"""',
                f"    from {up}Classes.{item.class_name} import {item.class_name}",
                "",
                f'    warn("{message}", DeprecationWarning, stacklevel=2)',
                f"    return {item.class_name}.{item.implementation}(*args, **kwargs)",
            ]
        elif item.function:
            # Renamed method (n2dqh_DataFreq -> DataFreq.n2dqh): other classes
            # have a method of the same name, the legacy function applied the
            # one of the target class to any object
            lines += [
                f"def {item.legacy_name}(obj, *args, **kwargs):",
                f'    """Deprecated: use {item.class_name}.{item.method}"""',
                f"    from {up}Classes.{item.class_name} import {item.class_name}",
                "",
                f'    warn("{message}", DeprecationWarning, stacklevel=2)',
                f"    return {item.class_name}.{item.method}(obj, *args, **kwargs)",
            ]
        else:
            lines += [
                f"def {item.legacy_name}(obj, *args, **kwargs):",
                f'    """Deprecated: use {item.class_name}.{item.method}"""',
                f'    warn("{message}", DeprecationWarning, stacklevel=2)',
                f"    return obj.{item.method}(*args, **kwargs)",
            ]
    return "\n".join(lines) + "\n"


def _class_lineage(class_name, gen_dict):
    """The class and its mother classes (from the generation dictionary)."""
    lineage = []
    while class_name and class_name not in lineage:
        lineage.append(class_name)
        class_name = (gen_dict or {}).get(class_name, {}).get("mother") or None
    return lineage


def _is_static_function(node):
    """True for a function without self: @staticmethod or no parameter."""
    if any(
        isinstance(decorator, ast.Name) and decorator.id == "staticmethod"
        for decorator in node.decorator_list
    ):
        return True
    args = node.args.posonlyargs + node.args.args
    return not args or args[0].arg != "self"


def _bound_receiver(call, caller, target, source, offsets):
    """Object of a bound call: ``x = obj.<getter>(...)`` before ``f(x, ...)``.

    Returns the source of ``obj`` when the first argument is a name whose
    nearest assignment before the call, in the calling function, is a call of
    the getter of the target; else None.
    """
    if caller is None or not call.args or not isinstance(call.args[0], ast.Name):
        return None
    name = call.args[0].id
    getter = target.bound[1]
    assignments = [
        node
        for node in ast.walk(caller)
        if isinstance(node, ast.Assign)
        and node.lineno < call.lineno
        and any(isinstance(t, ast.Name) and t.id == name for t in node.targets)
    ]
    if not assignments:
        return None
    value = max(assignments, key=lambda node: node.lineno).value
    if not (
        isinstance(value, ast.Call)
        and isinstance(value.func, ast.Attribute)
        and value.func.attr == getter
    ):
        return None
    obj = value.func.value
    start = offsets[obj.lineno - 1] + obj.col_offset
    end = offsets[obj.end_lineno - 1] + obj.end_col_offset
    return source[start:end]


def redirect_moved_calls(source, package, class_name=None, moved=None, gen_dict=None):
    """Call the moved methods instead of the legacy functions.

    ``from ....Functions.MeshSolution.get_area import get_area`` is removed and
    ``get_area(ms, ...)`` becomes ``ms.get_area(...)``. A static method is
    called on ``self`` in a regular method of its class or of a daughter
    class, else on the class (static method, other class, function), the class
    being imported in the calling function (as the other class imports of the
    methods).

    Parameters
    ----------
    source : str
        Source of a legacy method module
    package : str
        Package of the module (to resolve its relative imports)
    class_name : str, optional
        Class of the method module
    moved : dict, optional
        {legacy module: MovedFunction} (default: MOVED_FUNCTIONS)
    gen_dict : dict, optional
        Generation dictionary, for the mother classes of class_name

    Returns
    -------
    source : str
        Source calling the methods
    """
    moved = MOVED_FUNCTIONS if moved is None else moved
    if not any(
        target.legacy_name in source for _, target in all_moved_targets(moved)
    ) and not any(
        module.split(".")[-1] in source for module in merged_sources()
    ):
        return source
    tree = ast.parse(source)
    offsets = _line_offsets(source)
    replacements = []
    names = {}  # Local name: MovedFunction
    for node in tree.body:
        if not isinstance(node, ast.ImportFrom):
            continue
        module = (
            resolve_name("." * node.level + (node.module or ""), package)
            if node.level
            else node.module
        )
        if not module or not module.startswith("pyleecan.Functions."):
            continue
        key = module[len("pyleecan.Functions.") :]
        value = moved.get(key)
        merged = merged_location(key)  # Module merged into another one
        if merged is not None and merged[0] == key and not merged[1]:
            merged = None  # The merge target itself: same module, same names
        if value is None and merged is None:
            continue
        targets = (
            {target.legacy_name: target for target in moved_targets(value)}
            if value is not None
            else {}
        )
        kept = [alias for alias in node.names if alias.name not in targets]
        if merged is None and len(kept) == len(node.names):
            continue
        for alias in node.names:
            if alias.name in targets:
                names[alias.asname or alias.name] = targets[alias.name]
        start = offsets[node.lineno - 1] + node.col_offset
        end = offsets[node.end_lineno - 1] + node.end_col_offset
        if kept and merged is not None:  # From the merged module
            new_module, renames = merged
            # The shared errors from classes_common.errors
            shared = set(_merged_spec(key)[1].get("errors", ()))
            error_aliases = [alias for alias in kept if alias.name in shared]
            kept = [alias for alias in kept if alias.name not in shared]
            error_text = (
                ast.unparse(
                    ast.ImportFrom(
                        module="classes_common.errors",
                        names=error_aliases,
                        level=len(package.split(".")),
                    )
                )
                if error_aliases
                else ""
            )
            aliases = []
            for alias in kept:
                new_name = renames.get(alias.name, alias.name)
                local = alias.asname or alias.name
                aliases.append(ast.alias(new_name, local if local != new_name else None))
            text = (
                ast.unparse(
                    ast.ImportFrom(
                        module="Functions." + new_module,
                        names=aliases,
                        level=len(package.split(".")),
                    )
                )
                if aliases
                else ""
            )
            if error_text:
                indent = " " * node.col_offset
                text = error_text if not text else text + "\n" + indent + error_text
        elif kept:
            text = ast.unparse(
                ast.ImportFrom(module=node.module, names=kept, level=node.level)
            )
        else:  # Remove the line
            text = ""
            end = offsets[node.end_lineno]
            start = offsets[node.lineno - 1]
        replacements.append((start, end, text))
    if not names and not replacements:
        return source
    lineage = _class_lineage(class_name, gen_dict)
    # Functions of the module and methods of its classes (femm_pyleecan)
    functions = [node for node in tree.body if isinstance(node, ast.FunctionDef)] + [
        item
        for node in tree.body
        if isinstance(node, ast.ClassDef)
        for item in node.body
        if isinstance(item, ast.FunctionDef)
    ]
    class_imports = {}  # Static function: classes to import in its body
    for node in ast.walk(tree):
        if not (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id in names
        ):
            continue
        target = names[node.func.id]
        func_start = offsets[node.func.lineno - 1] + node.func.col_offset
        func_end = offsets[node.func.end_lineno - 1] + node.func.end_col_offset
        caller = next(
            (f for f in functions if f.lineno <= node.lineno <= f.end_lineno), None
        )
        if target.bound:
            receiver = _bound_receiver(node, caller, target, source, offsets)
            if receiver is not None:  # obj.method(..., parameter=x)
                first = node.args[0]
                first_start = offsets[first.lineno - 1] + first.col_offset
                first_end = offsets[first.end_lineno - 1] + first.end_col_offset
                value = source[first_start:first_end]
                rest = node.args[1:] + node.keywords
                if rest:
                    following = min(rest, key=lambda item: (item.lineno, item.col_offset))
                    replacements.append(
                        (first_start, offsets[following.lineno - 1] + following.col_offset, "")
                    )
                    closing = offsets[node.end_lineno - 1] + node.end_col_offset - 1
                    replacements.append((closing, closing, f", {target.bound[0]}={value}"))
                else:
                    replacements.append(
                        (first_start, first_end, f"{target.bound[0]}={value}")
                    )
                replacements.append((func_start, func_end, f"{receiver}.{target.method}"))
                continue
        if target.static or target.bound:
            if caller is None:
                raise ValueError(
                    f"{package}: call of {target.method} outside of a function"
                )
            if target.class_name in lineage and not _is_static_function(caller):
                owner = "self"  # Method of the class or of a daughter class
            else:  # Static method, other class or function: on the class
                class_imports.setdefault(caller.name, (caller, set()))[1].add(
                    target.class_name
                )
                owner = target.class_name
            replacements.append(
                (func_start, func_end, f"{owner}.{target.implementation}")
            )
            continue
        if not node.args or isinstance(node.args[0], ast.Starred):
            raise ValueError(f"{package}: call of {target.method} without object")
        first = node.args[0]
        first_start = offsets[first.lineno - 1] + first.col_offset
        first_end = offsets[first.end_lineno - 1] + first.end_col_offset
        obj = source[first_start:first_end]
        if not isinstance(first, (ast.Name, ast.Attribute, ast.Subscript, ast.Call)):
            obj = f"({obj})"
        # Remove the object argument and its separator
        rest = node.args[1:] + node.keywords
        if rest:
            following = min(rest, key=lambda item: (item.lineno, item.col_offset))
            next_start = offsets[following.lineno - 1] + following.col_offset
            replacements.append((first_start, next_start, ""))
        else:
            replacements.append((first_start, first_end, ""))
        replacements.append((func_start, func_end, f"{obj}.{target.method}"))
    # Class import at the start of the body of the static functions
    up = "." * len(package.split("."))  # pyleecan.<...>: one dot per package
    for caller, classes in class_imports.values():
        body = caller.body
        first = body[1] if ast.get_docstring(caller) is not None and len(body) > 1 else body[0]
        indent = " " * first.col_offset
        start = offsets[first.lineno - 1]
        text = "".join(
            f"{indent}from {up}Classes.{name} import {name}\n" for name in sorted(classes)
        )
        replacements.append((start, start, text))
    for start, end, replacement in sorted(replacements, reverse=True):
        source = source[:start] + replacement + source[end:]
    return source
