from ....classes_common.parents import container_or_parent
import matplotlib.pyplot as plt
import numpy as np


from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.machine.lam_slot import LamSlot
from ....Classes_new.machine.lam_slot_wind import LamSlotWind
from ....Classes_new.machine.winding import Winding
from ....Classes_new.geometry.segment import Segment
from ....definitions import config_dict
from ....Functions_new.Plot import ARROW_COLOR, ARROW_WIDTH, MAIN_LINE_COLOR, MAIN_LINE_STYLE, MAIN_LINE_WIDTH, P_FONT_SIZE, SC_FONT_SIZE, SC_LINE_COLOR, SC_LINE_STYLE, SC_LINE_WIDTH, TEXT_BOX, plot_quote
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.lamination import Lamination

MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]


def plot_schematics(
    self,
    is_default: bool = False,
    is_return_default: bool = False,
    is_add_point_label: bool = False,
    is_add_schematics: bool = True,
    is_add_main_line: bool = True,
    type_add_active: int = 1,
    save_path: str | None = None,
    is_show_fig: bool = True,
    fig: Figure | None = None,
    ax: Axes | None = None,
    lam: Lamination | None = None,
) -> tuple[Figure, Axes] | Lamination:
    """Plot the schematics of the slot

    Parameters
    ----------
    self : SlotW61
        A SlotW61 object
    is_default : bool
        True: plot default schematics, else use current slot values
    is_return_default : bool
        True: return the default lamination used for the schematics (skip plot)
    is_add_point_label : bool
        True to display the name of the points (Z1, Z2....)
    is_add_schematics : bool
        True to display the schematics information (W0, H0...)
    is_add_main_line : bool
        True to display "main lines" (slot opening and 0x axis)
    type_add_active : int
        0: No active surface, 1: active surface as winding, 2: active surface as magnet, 3: active surface as winding + wedges
    save_path : str
        full path including folder, name and extension of the file to save if save_path is not None
    is_show_fig : bool
        To call show at the end of the method
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the data
    lam : Lamination
        Lamination of the slot (default: the parent of the slot)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the schematics
    ax : Matplotlib.axes.Axes object
        Axis containing the schematics
    -------
    lam : LamSlot
        Default lamination used for the schematics
    """
    lam = container_or_parent(self, lam, "lam")

    # Use some default parameter
    if is_default:
        slot = type(self)(
            Zs=12,
            H0=20e-3,
            W0=40e-3,
            H1=20e-3,
            H2=65e-3,
            W1=100e-3,
            W2=40e-3,
            W3=16e-3,
            H3=16e-3,
            H4=16e-3,
        )
        lam = LamSlot(
            Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, slot=slot
        )
        if is_return_default:
            return lam
        else:
            return slot.plot_schematics(
                is_default=False,
                is_return_default=False,
                is_add_point_label=is_add_point_label,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                type_add_active=type_add_active,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
                lam=lam,
            )
    else:
        # Getting the main plot
        if lam is None:
            raise ParentMissingError("Error: The slot is not inside a Lamination")
        fig, ax = lam.plot(is_show_fig=False, fig=fig, ax=ax)  # center slot on Ox axis
        point_dict = dict()
        point_dict_temp = self._comp_point_coordinate(lam=lam)
        for key in point_dict_temp:
            point_dict[key] = point_dict_temp[key] * np.exp(
                1j * (np.pi / self.Zs + 4 * np.pi / self.Zs)
            )
            point_dict[key + "d"] = point_dict[key] * np.exp(1j * (2 * np.pi / self.Zs))
            point_dict[key + "dd"] = point_dict[key + "d"] * np.exp(
                1j * (2 * np.pi / self.Zs)
            )

        if self.is_outwards(lam=lam):
            sign = 1
        else:
            sign = -1
        # Adding point label
        if is_add_point_label:
            for name, Z in point_dict.items():
                ax.text(
                    Z.real,
                    Z.imag,
                    name,
                    fontsize=P_FONT_SIZE,
                    bbox=TEXT_BOX,
                )

        # Adding schematics
        if is_add_schematics:
            # W0
            Zlim1 = point_dict["Z1d"] + 0.005j
            Zlim2 = point_dict["Z10"] + 0.005j
            plot_quote(
                point_dict["Z1d"],
                Zlim1,
                Zlim2,
                point_dict["Z10"],
                offset_label=self.H0 * 0.1 + 1j * self.W0 * 0.3 - (0.009 + 0.005j),
                fig=fig,
                ax=ax,
                label="W0",
            )
            # H0
            Zlim1 = point_dict["Z2d"]
            Zlim2 = point_dict["Z2d"].real + 1j * point_dict["Z1d"].imag
            plot_quote(
                point_dict["Z2d"],
                Zlim1 - (0.006 + 0j),
                Zlim2 - (0.006 + 0j),
                point_dict["Z1d"],
                offset_label=self.H0 * -1.2 + 1j * self.W0 * 0.05 - (-0.004 + 0.005j),
                fig=fig,
                ax=ax,
                label="H0",
            )
            # W1
            line = Segment(
                begin=(point_dict["Z2d"] + point_dict["Z3d"]) / 2,
                end=(point_dict["Z9"] + point_dict["Z8"]) / 2,
            )
            line.plot(
                fig=fig,
                ax=ax,
                label="W1",
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                offset_label=2.1j * self.W0 * 0.1 - (0.007 + 0j),
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H1
            Zlim1 = point_dict["Z9"]
            Zlim2 = point_dict["Z8"]
            plot_quote(
                point_dict["Z9"],
                Zlim1 + (0.006 + 0j),
                Zlim2 + (0.006 + 0j),
                point_dict["Z8"],
                offset_label=self.H0 * 0.6 + 1j * self.W0 * 0.05 - (0.005 + 0.005j),
                fig=fig,
                ax=ax,
                label="H1",
            )
            # H2
            Zlim1 = point_dict["Z4d"]
            Zlim2 = point_dict["Z5d"]
            plot_quote(
                point_dict["Z4d"],
                Zlim1 - (0.035 + 0j),
                Zlim2 - (0.035 + 0j),
                point_dict["Z5d"],
                offset_label=self.H0 * -1.0 + 1j * self.W0 * 0.05,
                fig=fig,
                ax=ax,
                label="H2",
            )
            # W2
            line = Segment(
                begin=(point_dict["Z4dd"] + point_dict["Z5dd"]) / 2,
                end=(point_dict["Z7d"] + point_dict["Z6d"]) / 2,
            )
            line.plot(
                fig=fig,
                ax=ax,
                label="W2",
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                offset_label=(-5.3j * self.W0 * 0.1) - (0.000 - 0.005j),
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W5
            Zlim1 = point_dict["Zw5"]
            Zlim2 = point_dict["Zw5"]
            plot_quote(
                point_dict["Z3"],
                Zlim1,
                Zlim2,
                point_dict["Z5"],
                offset_label=0,
                fig=fig,
                ax=ax,
                label=None,
            )
            # W5s
            Zlim1 = point_dict["Zw5s"]
            Zlim2 = point_dict["Zw5s"]
            plot_quote(
                point_dict["Z6"],
                Zlim1,
                Zlim2,
                point_dict["Z8"],
                offset_label=0,
                fig=fig,
                ax=ax,
                label=None,
            )
            if type_add_active != 0:
                # W3
                line = Segment(
                    begin=((point_dict["Zw5"] + point_dict["Z3"]) / 2),
                    end=((point_dict["Zw4"] + point_dict["Zw3"]) / 2),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="W3",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=(-4.8j * self.W0 * 0.1) - (0.007 + 0j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H3
                line = Segment(
                    begin=((point_dict["Z8"] + point_dict["Z7"]) / 2) - (0.008 + 0j),
                    end=((point_dict["Zw4s"] + point_dict["Zw1s"]) / 2),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H3",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=(-0.2j * self.W0 * 0.1) + (0.008 - 0.002j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H4
                line = Segment(
                    begin=((point_dict["Z6"] + point_dict["Zw5s"]) / 2) - (0.008 + 0j),
                    end=((point_dict["Zw2s"] + point_dict["Zw3s"]) / 2),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    label="H4",
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    offset_label=(-0.2j * self.W0 * 0.1) + (0.008 - 0.002j),
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

        if is_add_main_line:
            # Ox axis
            line = Segment(begin=0, end=lam.Rext * 1.5)
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # Top arc
            line = Arc1(
                begin=self.get_Rbo(lam=lam),
                end=-self.get_Rbo(lam=lam),
                radius=self.get_Rbo(lam=lam),
                is_trigo_direction=True,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

        if type_add_active in [1, 3]:  # Wind and Wedge
            is_add_wedge = False  # No wedge for this false
            self.plot_active(
                fig=fig,
                ax=ax,
                is_show_fig=False,
                is_add_wedge=is_add_wedge,
                wind_mat=np.ones((1, 2, self.Zs, 1)),
                alpha=np.pi / self.Zs + 2 * np.pi / self.Zs, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False),
            )
            self.plot_active(
                fig=fig,
                ax=ax,
                is_show_fig=False,
                is_add_wedge=is_add_wedge,
                wind_mat=np.ones((1, 2, self.Zs, 1)),
                alpha=np.pi / self.Zs + 4 * np.pi / self.Zs, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False),
            )
            self.plot_active(
                fig=fig,
                ax=ax,
                is_show_fig=False,
                is_add_wedge=is_add_wedge,
                wind_mat=np.ones((1, 2, self.Zs, 1)),
                alpha=np.pi / self.Zs + 6 * np.pi / self.Zs, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False),
            )
            self.plot_active(
                fig=fig,
                ax=ax,
                is_show_fig=False,
                is_add_wedge=is_add_wedge,
                wind_mat=np.ones((1, 2, self.Zs, 1)),
                alpha=np.pi / self.Zs + 8 * np.pi / self.Zs, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False),
            )
        elif type_add_active == 2:  # Magnet
            self.plot_active(
                fig=fig,
                ax=ax,
                is_show_fig=False,
                enforced_default_color=MAGNET_COLOR, lam=lam, lam_label=None if lam is None else lam.get_label(is_add_id=False),
            )

        # Zooming and cleaning
        ax.axis("equal")
        ax.set_ylim(abs(point_dict["Z1"]) * 0.5, abs(point_dict["Z1"]) * 1.2)
        ax.set_xlim(-2 * self.W0, 2 * self.W0)
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(type(self).__name__ + " Schematics")
        ax.set_title("")
        ax.get_legend().remove()
        ax.set_axis_off()
        fig.tight_layout()

        # Save / Show
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        if is_show_fig:
            fig.show()
        return fig, ax
