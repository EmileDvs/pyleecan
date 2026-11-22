from ....classes_common.parents import container_or_parent
from matplotlib.patches import Patch
import matplotlib.pyplot as plt

from ....Functions_new.utils.labels import decode_label, WIND_LAB, BAR_LAB
from ....Functions_new.Winding.gen_phase_list import gen_name
from ....Functions_new.utils.init_fig import init_fig
from ....definitions import config_dict
from ....Classes_new.machine.winding_sc import WindingSC
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.machine import Machine

PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
PLUS_HATCH = "++"
MINUS_HATCH = ".."


def plot(
    self,
    fig: Figure | None = None,
    ax: Axes | None = None,
    is_lam_only: bool = False,
    sym: int = 1,
    alpha: float = 0,
    delta: complex = 0,
    is_edge_only: bool = False,
    edgecolor: str | None = None,
    is_add_arrow: bool = False,
    is_display: bool = True,
    is_add_sign: bool = False,
    is_show_fig: bool = True,
    save_path: str | None = None,
    win_title: str | None = None,
    is_winding_connection: bool = False, machine: Machine | None = None,
) -> list | tuple[Figure, Axes]:
    """Plot the Lamination with empty Slots in a matplotlib fig

    Parameters
    ----------
    self : LamSlotMulti
        A LamSlotMulti object
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the data
    is_lam_only: bool
        True to plot only the lamination
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation
    is_edge_only: bool
        To plot transparent Patches
    edgecolor:
        Color of the edges if is_edge_only=True
    is_display : bool
        False to return the patches
    is_show_fig : bool
        To call show at the end of the method
    is_winding_connection : bool
        True to display winding connections (not used)
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    patches : list
        List of Patches
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    ax : Matplotlib.axes.Axes object
        Axis containing the plot
    """
    machine = container_or_parent(self, machine, "machine")

    from ....Classes_new.machine.machine import Machine
    from ....Classes_new.machine.winding import Winding
    (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

    # getting the number of phases and winding connection matrix
    if self.winding is not None:
        if isinstance(self.winding, WindingSC):  # plot only one phase for WindingSC
            wind_mat = None
            qs = 1
        else:
            try:
                wind_mat = self.winding.get_connection_mat(self.get_Zs(), lam=self)
                qs = self.winding.qs
            except:
                wind_mat = None
                qs = 1
    else:
        wind_mat = None
        qs = 1

    # Get the LamSlot surface(s)
    surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta, machine=machine)
    patches = list()
    for surf in surf_list:
        label_dict = decode_label(surf.label)
        if WIND_LAB in label_dict["surf_type"] or BAR_LAB in label_dict["surf_type"]:
            if not is_lam_only:
                if wind_mat is None:  # No winding, WindingSC: first phase color
                    color, sign = Winding._find_wind_phase_color(surf.label, None)
                else:
                    color, sign = self.winding.find_wind_phase_color(
                        label=surf.label, wind_mat=wind_mat, lam=self
                    )
                if sign == "+" and is_add_sign:
                    hatch = PLUS_HATCH
                elif sign == "-" and is_add_sign:
                    hatch = MINUS_HATCH
                else:
                    hatch = None
                patches.extend(
                    surf.get_patches(
                        color=color,
                        is_edge_only=is_edge_only,
                        hatch=hatch,
                        edgecolor=edgecolor,
                    )
                )
        else:
            color, legend = Machine.get_color_legend_from_surface(surf, is_lam_only)

            if color is not None:
                patches.extend(
                    surf.get_patches(
                        color=color,
                        is_edge_only=is_edge_only,
                        edgecolor=edgecolor,
                    )
                )
            if not is_edge_only and legend is not None and legend not in label_leg:
                label_leg.append(legend)
                patch_leg.append(Patch(color=color))

    # Display the result
    if is_display:
        (fig, ax, patch_leg, label_leg) = init_fig(fig)
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # Window title
        if self.is_stator:
            prefix = "Stator "
        else:
            prefix = "Rotor "
        if (
            win_title is None
            and machine is not None
            and machine.name not in [None, ""]
        ):
            win_title = machine.name + " " + prefix[:-1]
        elif win_title is None:
            win_title = prefix[:-1]
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(win_title)

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Add the legend
        if not is_edge_only:
            if self.is_stator and "Stator" not in label_leg:
                ax.set_title("Stator with empty slot")
            elif not self.is_stator and "Rotor" not in label_leg:
                ax.set_title("Rotor with Winding")
            # Add the winding legend only if needed
            if not is_lam_only:
                if self.winding is not None:
                    phase_name = [prefix + n for n in gen_name(qs, is_add_phase=True)]
                    for ii in range(qs):
                        if not phase_name[ii] in label_leg and not is_add_sign:
                            # Avoid adding twice the same label
                            index = ii % len(PHASE_COLORS)
                            patch_leg.append(Patch(color=PHASE_COLORS[index]))
                            label_leg.append(phase_name[ii])
                        if not "Phase +" in label_leg and is_add_sign:
                            # Avoid adding twice the same label
                            index = ii % len(PHASE_COLORS)
                            patch_leg.append(
                                Patch(color=PHASE_COLORS[index], hatch=PLUS_HATCH)
                            )
                            label_leg.append(phase_name[ii] + " +")
                        if not "Phase -" in label_leg and is_add_sign:
                            # Avoid adding twice the same label
                            index = ii % len(PHASE_COLORS)
                            patch_leg.append(
                                Patch(color=PHASE_COLORS[index], hatch=MINUS_HATCH)
                            )
                            label_leg.append(phase_name[ii] + " -")
            ax.legend(patch_leg, label_leg)

        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        if is_show_fig:
            fig.show()
        return fig, ax
    else:
        return patches
