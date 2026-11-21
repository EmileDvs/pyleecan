"""Fixes of legacy method bugs, applied by the method generator (PLAN.md Step 5).

The legacy ``Methods`` are never edited: a line of a legacy method that raises
an exception whenever it runs (NameError, TypeError, UnboundLocalError...) is
fixed in the copy written to ``Methods_new``, before the modernization passes.
A fix changes the behaviour against legacy only where legacy raised an error.

Each fix replaces a text of the legacy module: the text must be found the
expected number of times, so that a legacy change (merge of an upstream pull
request, Step 7) that touches a fixed line stops the generation instead of
being silently ignored. Each fix is listed under "Fixed" in the CHANGELOG.
"""

import tokenize
from pathlib import Path
from typing import NamedTuple


class LegacyFix(NamedTuple):
    """Text replacement in a legacy method module."""

    old: str
    """Legacy text (newlines as "\\n")"""
    new: str
    """Fixed text"""
    count: int = 1
    """Number of occurrences of the legacy text in the module"""


class LegacyFixError(ValueError):
    """The legacy text of a fix is not found as expected (legacy changed)."""


_DATAND_COMPARE = LegacyFix(
    # get_interpolation needs the index of the axis in the array; get_along
    # squeezes the single-value axes, so the index counts the axes left
    old="""\
        # Get the common bases
        common_axis_values = {}
        for axis in axes.keys():
            common_axis_values[axis] = axes[axis]
            for i, data in enumerate(data_list):
                common_axis_values[axis] = get_common_base(
                    common_axis_values[axis], data_axis_values[i][axis]
                )
            # Interpolate over common axis values
            values = get_interpolation(values, axes[axis], common_axis_values[axis])
            for i, data in enumerate(data_list):
                data_values[i] = get_interpolation(
                    data_values[i],
                    data_axis_values[i][axis],
                    common_axis_values[axis],
                )
""",
    new="""\
        # Get the common bases
        common_axis_values = {}
        # Index of the current axis in each array (single-value axes squeezed)
        index = 0
        data_index = [0] * len(data_list)
        for axis in axes.keys():
            common_axis_values[axis] = axes[axis]
            for i, data in enumerate(data_list):
                common_axis_values[axis] = get_common_base(
                    common_axis_values[axis], data_axis_values[i][axis]
                )
            # Interpolate over common axis values
            if len(axes[axis]) > 1:
                values = get_interpolation(
                    values, axes[axis], common_axis_values[axis], index
                )
                index += 1
            for i, data in enumerate(data_list):
                if len(data_axis_values[i][axis]) > 1:
                    data_values[i] = get_interpolation(
                        data_values[i],
                        data_axis_values[i][axis],
                        common_axis_values[axis],
                        data_index[i],
                    )
                    data_index[i] += 1
""",
)

_CONVERT_MC_SLOT = LegacyFix(
    # name_slot is not assigned in the else branch (UnboundLocalError)
    old='f"Type of slot {name_slot} has not equivalent',
    new='f"Type of slot {type(slot).__name__} has not equivalent',
)

_RULE_FUNCTIONS_IMPORT = (
    "    # Local import (circular: the registry imports the rule modules)\n"
    "    from ....Functions_new.Converter.rule_functions import rule_function_module\n\n"
)

def _log_error_fixes(logger):
    """log_error without popup in a method: the error logged (no GUI import)."""
    return (
        LegacyFix(old="from ....Functions.GUI.log_error import log_error\n", new=""),
        LegacyFix(
            old="            log_error(\n"
            "                self,\n"
            "                err_msg,\n"
            f"                {logger},\n"
            "                is_popup=False,\n"
            "                is_warning=False,\n"
            "            )\n",
            new=f"            {logger}.error(err_msg)\n",
        ),
    )


LEGACY_FIXES = {
    # log_error moved to the GUI (Step 8 group 13): the core methods calling it
    # without popup log the error instead of importing the GUI
    ("MeshMat", "save_vtk.py"): _log_error_fixes("self.get_logger()"),
    ("MeshVTK", "save_vtk.py"): _log_error_fixes("self.get_logger()"),
    ("MeshSolution", "export_to_mat.py"): _log_error_fixes("self.mesh.get_logger()"),
    # The functions of a complex rule read from the static registry when the
    # rule is applied (Step 8): the custom setter of fct_name that stored them
    # on the object is not wired in the new classes, and a pydantic model
    # cannot hold these attributes
    ("RuleComplex", "convert_to_P.py"): (
        LegacyFix(
            old="    machine = self.other_to_P(self, machine, other_dict, other_unit_dict)\n",
            new=_RULE_FUNCTIONS_IMPORT
            + "    machine = rule_function_module(self.fct_name).other_to_P(\n"
            "        self, machine, other_dict, other_unit_dict\n"
            "    )\n",
        ),
    ),
    ("RuleComplex", "convert_to_other.py"): (
        LegacyFix(
            old="    other_dict = self.P_to_other(self, machine, other_dict)\n",
            new=_RULE_FUNCTIONS_IMPORT
            + "    other_dict = rule_function_module(self.fct_name).P_to_other(\n"
            "        self, machine, other_dict\n"
            "    )\n",
        ),
    ),
    ("VectorField", "get_harm_xyz_along.py"): (
        # pol2cart not imported (NameError)
        LegacyFix(
            old="from ....Functions.SciDataTool import AxisError\n",
            new="from ....Functions.SciDataTool import AxisError\n"
            "from ....Functions.SciDataTool.conversions import pol2cart\n",
        ),
    ),
    ("EEC_SCIM", "_comp_flux_mean.py"): (
        # n2abc has no n parameter, it takes the phase number from the shape
        LegacyFix(
            old="n2abc(Phi[:, id0:id1], n=qsr_per_pole)",
            new="n2abc(Phi[:, id0:id1])",
        ),
    ),
    ("DataND", "compare_along.py"): (_DATAND_COMPARE,),
    ("DataND", "compare_magnitude_along.py"): (_DATAND_COMPARE,),
    ("DataND", "compare_phase_along.py"): (_DATAND_COMPARE,),
    ("ModelBH", "fit_model.py"): (
        # Hmax imposed without Bmax: number of added points unbound
        LegacyFix(
            old="""\
    if Hmax is not None:
        added_H = np.linspace(H[-1], Hmax, iteration)
""",
            new="""\
    if Hmax is not None:
        if Bmax is None:
            # Same step as the extrapolation up to Bmax (1% of the last H)
            iteration = max(int(np.ceil((Hmax - H[-1]) / (H[-1] * 0.01))), 0)
        added_H = np.linspace(H[-1], Hmax, iteration)
""",
        ),
        # No Bmax, no Hmax: undefined Bs and a, new_BH unbound
        LegacyFix(
            old="""\
    else:
        new_B = self.BH_func(H, Bs, a)
""",
            new="""\
    else:
        new_B = self.BH_func(H, param1, param2)
        new_BH = np.column_stack((H, new_B))
""",
        ),
    ),
    ("ConvertMC", "convert_to_other/convert_slot_to_other.py"): (_CONVERT_MC_SLOT,),
    ("ConvertMC", "convert_to_other/convert_slot_rotor_to_other.py"): (
        _CONVERT_MC_SLOT,
    ),
    ("BoreSinePole", "get_bore_line.py"): (
        # raise () (TypeError): explicit error
        LegacyFix(
            old="raise ()  # TODO",
            # One line: the two occurrences have different indentations
            new='raise ValueError(f"BoreSinePole: {len(inter)} q axis intersections, 1 expected")',
            count=2,
        ),
    ),
    ("OP", "get_OP_array.py"): (
        # arg_list is the *args tuple: no append (AttributeError)
        LegacyFix(
            old="        arg_list = arg_list[0]\n",
            new="        arg_list = arg_list[0]\n    arg_list = list(arg_list)\n",
        ),
        # OP_matrix sized before the default columns are added (IndexError)
        LegacyFix(
            old="    # Init OP_matrix\n    OP_matrix = zeros((1, len(arg_list)))\n\n",
            new="",
        ),
        LegacyFix(
            old="    # Set column by column according to arg_list\n",
            new="    # Init OP_matrix\n"
            "    OP_matrix = zeros((1, len(arg_list)))\n\n"
            "    # Set column by column according to arg_list\n",
        ),
    ),
    ("OPMatrix", "get_OP_array.py"): (
        # OP_matrix sized before the default columns are added (IndexError)
        LegacyFix(
            old="    # Init OP_matrix\n"
            "    N_OP = self.get_N_OP()\n"
            "    OP_matrix = zeros((N_OP, len(arg_list)))\n\n",
            new="",
        ),
        LegacyFix(
            old="    arg_list_lower = [arg.lower() for arg in arg_list]\n",
            new="    # Init OP_matrix\n"
            "    N_OP = self.get_N_OP()\n"
            "    OP_matrix = zeros((N_OP, len(arg_list)))\n\n"
            "    arg_list_lower = [arg.lower() for arg in arg_list]\n",
        ),
    ),
    ("Data", "animate_as_gif.py"): (
        # Function moved from Plot.animate_as_gif (Step 8): the VectorField
        # branch of a single Data object used an undefined name (NameError)
        LegacyFix(
            old="            if isinstance(data_list, VectorField):\n"
            "                if component_list is None:  # default: extract all components\n"
            "                    component_list = data.components.keys()\n",
            new="            if isinstance(data_list, VectorField):\n"
            "                if component_list is None:  # default: extract all components\n"
            "                    component_list = data_list.components.keys()\n",
        ),
    ),
    ("ElecLUTdq", "run.py"): (
        # OutLoss has no Pjoule... fields (TypeError): one OutLossModel per
        # loss, named as in LUTdq.interp_Ploss_dqh
        LegacyFix(
            old="from ....Classes.OutLoss import OutLoss\n",
            new="from ....Classes.OutLoss import OutLoss\n"
            "from ....Classes.OutLossModel import OutLossModel\n",
        ),
        LegacyFix(
            old="""\
        output.loss = OutLoss(
            Pjoule=out_dict["Pjoule"],
            Pstator=out_dict["Pstator"],
            Pmagnet=out_dict["Pmagnet"],
            Protor=out_dict["Protor"],
            Pprox=out_dict["Pprox"],
        )
""",
            new="""\
        output.loss = OutLoss(
            loss_dict={
                name: OutLossModel(
                    name=name, scalar_value=out_dict[key], coeff_dict=None
                )
                for name, key in [
                    ("joule", "Pjoule"),
                    ("stator core", "Pstator"),
                    ("magnets", "Pmagnet"),
                    ("rotor core", "Protor"),
                    ("proximity", "Pprox"),
                ]
            }
        )
""",
        ),
    ),
}
"""{(class name, method module below the class folder): fixes in order}"""


def apply_fixes(source, fixes, label="module"):
    """Apply text fixes to a legacy module source.

    Parameters
    ----------
    source : str
        Legacy source (newlines as "\\n")
    fixes : tuple
        LegacyFix to apply in order
    label : str
        Name of the module in the error messages

    Returns
    -------
    source : str
        Fixed source

    Raises
    ------
    LegacyFixError
        The legacy text of a fix is not found the expected number of times
    """
    for fix in fixes:
        found = source.count(fix.old)
        if found != fix.count:
            raise LegacyFixError(
                f"{label}: legacy text found {found} times instead of "
                f"{fix.count}, update legacy_fixes.py:\n{fix.old}"
            )
        source = source.replace(fix.old, fix.new)
    return source


def apply_legacy_fixes(target_root, classes, fixes=None):
    """Fix the method modules copied in Methods_new (method generator).

    Parameters
    ----------
    target_root : Path
        Methods_new folder
    classes : dict
        {class name: sub-package} of the classes copied in Methods_new
    fixes : dict, optional
        {(class name, module): fixes} (default: LEGACY_FIXES)

    Returns
    -------
    fixed : list
        Paths of the fixed modules
    """
    fixes = LEGACY_FIXES if fixes is None else fixes
    fixed = []
    for (class_name, module), module_fixes in sorted(fixes.items()):
        if class_name not in classes:
            continue  # Partial generation or frozen package
        path = Path(target_root, classes[class_name], class_name, module)
        with tokenize.open(path) as source_file:
            source = source_file.read()
            encoding = source_file.encoding
        source = apply_fixes(source, module_fixes, f"{class_name}/{module}")
        path.write_text(source, encoding=encoding, newline="")
        fixed.append(path)
    return fixed
