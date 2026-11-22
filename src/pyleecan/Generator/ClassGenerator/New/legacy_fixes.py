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


_LEGEND_COLORS_AT_IMPORT = '''if "WEDGE_COLOR" not in config_dict["PLOT"]["COLOR_DICT"]:
    config_dict["PLOT"]["COLOR_DICT"]["WEDGE_COLOR"] = "y"
WEDGE_COLOR = config_dict["PLOT"]["COLOR_DICT"]["WEDGE_COLOR"]

if "KEY_COLOR" not in config_dict["PLOT"]["COLOR_DICT"]:
    config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"] = "y"
KEY_COLOR = config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"]

VENT_COLOR = config_dict["PLOT"]["COLOR_DICT"]["VENT_COLOR"]
ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
BAR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["BAR_COLOR"]

PLUS_HATCH = "++"
MINUS_HATCH = ".."
'''

_LEGEND_COLORS_AT_CALL = '''        Legend to display for the surface
    """
    # The colors of the configuration when called (the defaults of the
    # wedges and keys added once)
    color_dict = config_dict["PLOT"]["COLOR_DICT"]
    color_dict.setdefault("WEDGE_COLOR", "y")
    color_dict.setdefault("KEY_COLOR", "y")
    WEDGE_COLOR = color_dict["WEDGE_COLOR"]
    KEY_COLOR = color_dict["KEY_COLOR"]
    VENT_COLOR = color_dict["VENT_COLOR"]
    ROTOR_COLOR = color_dict["ROTOR_COLOR"]
    STATOR_COLOR = color_dict["STATOR_COLOR"]
    MAGNET_COLOR = color_dict["MAGNET_COLOR"]
    BAR_COLOR = color_dict["BAR_COLOR"]
'''

_LOSS_MODEL_MESH_SOLUTION = '''    # The loss density on all the elements of the mesh (indice_element axis
    # since the OutMag meshsolution of #751; the density of a model is given
    # on the elements of its group), as OutLoss.get_meshsolution
    Indice_Element = axes_dict["indice_element"]
    Nelem = Indice_Element.get_length()
    loss_density = self.loss_density
    if loss_density.shape[-1] != Nelem:
        loss_density_all = np.zeros((loss_density.shape[0], Nelem), dtype=float)
        loss_density_all[:, ms_mag.group[self.group]] = loss_density
        loss_density = loss_density_all
    if loss_density.shape[0] == 1:  # Frequency model: average value
        Loss_density_df = DataFreq(
            name=f"{self.name} loss density",
            unit="W/m3",
            symbol="L",
            values=loss_density,
            is_real=True,
            axes=[axes_dict["freqs"], Indice_Element],
        )
    else:  # Time model
        from ....Classes.DataTime import DataTime

        Loss_density_df = DataTime(
            name=f"{self.name} loss density",
            unit="W/m3",
            symbol="L",
            values=loss_density,
            is_real=True,
            axes=[axes_dict["time"], Indice_Element],
        )
'''

GUI_LEGACY_FIXES = {
    # The Qt Designer modules build the line edits with their parent as only
    # positional argument (FloatEdit(self.g_x)): it was taken as the unit,
    # the line edit created without parent but kept by its layout. Owned by
    # both Python and Qt (and holding its parent through self.unit), it is
    # deleted twice when the garbage collector frees the dialog: access
    # violation (DBore, DMatSetup...). The unit is always set afterwards
    # (lf_x.unit = "m"), never given positionally.
    "Tools/FloatEdit.py": (
        LegacyFix(
            old='    def __init__(self, unit="", *args, **kwargs):\n',
            new='    def __init__(self, *args, unit="", **kwargs):\n',
        ),
    ),
}
"""Fixes of the legacy GUI modules, applied by the GUI generator:
{module path in GUI (posix): fixes}"""

LEGACY_FIXES = {
    # The loss density of a model on the whole mesh: the "indice" axis no
    # longer exists (KeyError when plotting the losses of a model)
    ("OutLossModel", "get_mesh_solution.py"): (
        LegacyFix(
            old="from ....Classes.DataFreq import DataFreq\n",
            new="import numpy as np\n\nfrom ....Classes.DataFreq import DataFreq\n",
        ),
        LegacyFix(
            old='''    Loss_density_df = DataFreq(
        name=f"{self.name} loss density",
        unit="W/m3",
        symbol="L",
        values=self.loss_density,
        is_real=True,
        axes=[axes_dict["freqs"], axes_dict["indice"]],
    )
''',
            new=_LOSS_MODEL_MESH_SOLUTION,
        ),
    ),
    # The new classes store a copy of an assigned dict (the legacy property
    # kept the object): the overall loss is added to the stored dict, read
    # back through the local name (KeyError: 'overall' before)
    ("LossFEA", "run.py"): (
        LegacyFix(
            old="    output.loss.loss_dict = loss_dict\n",
            new="    output.loss.loss_dict = loss_dict\n"
            "    loss_dict = output.loss.loss_dict  # The stored dict\n",
        ),
    ),
    # Step 8 group 9 (decision 2026-11-21): Machine.get_color_legend_from_surface
    # reads the plot colors when called, not when the module is imported (the
    # unused PHASE_COLORS and hatches dropped)
    ("Machine", "get_color_legend_from_surface.py"): (
        LegacyFix(old=_LEGEND_COLORS_AT_IMPORT, new=""),
        LegacyFix(
            old='''        Legend to display for the surface
    """
''',
            new=_LEGEND_COLORS_AT_CALL,
        ),
    ),
    # The defaults of the wedge and key colors were set in the configuration
    # by the import of get_color_legend_from_surface (now read when called):
    # the other plots read them with the same default
    ("Slot", "plot_active.py"): (
        LegacyFix(
            old='config_dict["PLOT"]["COLOR_DICT"]["WEDGE_COLOR"]',
            new='config_dict["PLOT"]["COLOR_DICT"].get("WEDGE_COLOR", "y")',
        ),
    ),
    ("SlotM10", "plot_schematics.py"): (
        LegacyFix(
            old='config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"]',
            new='config_dict["PLOT"]["COLOR_DICT"].get("KEY_COLOR", "y")',
        ),
    ),
    ("SlotM11", "plot_schematics.py"): (
        LegacyFix(
            old='config_dict["PLOT"]["COLOR_DICT"]["KEY_COLOR"]',
            new='config_dict["PLOT"]["COLOR_DICT"].get("KEY_COLOR", "y")',
        ),
    ),
    # set_plot_gui_icon moved to the GUI (Step 8 group 9): imported when the
    # plot is shown, so that the class module does not import the GUI (Qt)
    ("LamSlotWind", "plot_mmf_unit.py"): (
        LegacyFix(
            old="from ....Functions.Plot.set_plot_gui_icon import set_plot_gui_icon\n",
            new="",
        ),
        LegacyFix(
            old="    set_plot_gui_icon()\n",
            new="    # Local import (circular: the GUI imports the classes)\n"
            "    from ....Functions.Plot.set_plot_gui_icon import set_plot_gui_icon\n\n"
            "    set_plot_gui_icon()\n",
        ),
    ),
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
