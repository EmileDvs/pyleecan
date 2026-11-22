from ....classes_common.parents import container_or_parent
import matplotlib.pyplot as plt
import numpy as np


from ....Functions_new.Plot import dict_2D
from ....definitions import config_dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from ....Classes_new.machine.machine import Machine

PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]


def plot_mmf_unit(self, save_path: str | None = None, is_show_fig: bool = False, machine: Machine | None = None) -> Figure:
    """Plot the winding unit mmf as a function of space

    Parameters
    ----------
    self : LamSlotWind
        an LamSlotWind object
    save_path : str
        File path to save the figure
    is_show_fig : bool
        To call show at the end of the method
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    """
    machine = container_or_parent(self, machine, "machine")

    name = ""
    if machine is not None and machine.name not in [None, ""]:
        name += machine.name + " "
    if self.is_stator:
        name += "Stator "
    else:
        name += "Rotor "

    # Compute the winding function and mmf
    qs = self.winding.qs
    p = self.get_pole_pair_number()
    MMF_U, WF = self.comp_mmf_unit(Nt=1, Na=400 * p, machine=machine)

    color_list = config_dict["PLOT"]["COLOR_DICT"]["COLOR_LIST"][:qs]

    fig, axs = plt.subplots(2, 1, tight_layout=True, figsize=(8, 8))

    dict_2D_0 = dict_2D.copy()
    dict_2D_0["color_list"] = color_list + ["k"]

    WF.plot_2D_Data(
        "angle{°}",
        "phase[]",
        data_list=[MMF_U],
        fig=fig,
        ax=axs[0],
        is_show_fig=is_show_fig,
        win_title=name + "phase MMF",
        **dict_2D_0,
    )

    dict_2D_0["color_list"] = [color_list[0], "k"]

    r_max = 100
    WF.plot_2D_Data(
        "wavenumber=[0," + str(r_max) + "]",
        data_list=[MMF_U],
        fig=fig,
        ax=axs[1],
        is_show_fig=is_show_fig,
        win_title=name + "phase MMF FFT",
        save_path=save_path,
        **dict_2D_0,
    )
    # Local import (circular: the GUI imports the classes)
    from ....GUI_new.Tools.set_plot_gui_icon import set_plot_gui_icon

    set_plot_gui_icon()

    return fig
