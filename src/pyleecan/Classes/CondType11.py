# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/CondType11.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/CondType11
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Conductor import Conductor

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.CondType11.plot import COND_COLOR, INS_COLOR
from matplotlib.patches import Patch, Rectangle
from pyleecan.Functions.init_fig import init_fig
import matplotlib.pyplot as plt
from pyleecan.Classes.Segment import Segment
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
    TEXT_BOX,
)

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class CondType11(Conductor):
    """parallel stranded conductor consisting of at least a single rectangular wire"""

    VERSION = 1

    # cf Methods.Machine.CondType11.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Hwire) * self.Nwppc_rad

    # cf Methods.Machine.CondType11.comp_height_wire
    def comp_height_wire(self):
        """Return wire height

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        H: float
            Height of the wire [m]

        """

        return self.Hwire

    # cf Methods.Machine.CondType11.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return self.Nwppc_tan

    # cf Methods.Machine.CondType11.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return self.Nwppc_rad

    # cf Methods.Machine.CondType11.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        S = self.comp_height() * self.comp_width()

        return S

    # cf Methods.Machine.CondType11.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = self.Hwire * self.Wwire * self.Nwppc_tan * self.Nwppc_rad

        return Sact

    # cf Methods.Machine.CondType11.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_tan

    # cf Methods.Machine.CondType11.comp_width_wire
    def comp_width_wire(self):
        """Return wire width

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        W: float
            Width of the wire [m]

        """

        return self.Wwire

    # cf Methods.Machine.CondType11.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always False since wire is rectangular

        """

        return False

    # cf Methods.Machine.CondType11.plot
    def plot(self, is_show_fig=True, fig=None, ax=None):
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        patches_list = []

        # Conductor insulation
        Wcond = self.comp_width()
        Hcond = self.comp_height()
        patches_list.append(Rectangle((0, 0), Wcond, Hcond, color=INS_COLOR))

        # Wire conductor
        for ii in range(self.Nwppc_tan):
            for jj in range(self.Nwppc_rad):
                # Computation of bottom left corner coodinates
                x = self.Wins_wire + ii * (self.Wwire + 2 * self.Wins_wire)
                y = self.Wins_wire + jj * (self.Hwire + 2 * self.Wins_wire)
                patches_list.append(
                    Rectangle((x, y), self.Wwire, self.Hwire, color=COND_COLOR)
                )

        # Display
        (fig, ax, _, _) = init_fig(fig=fig, ax=ax)
        for patch in patches_list:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The conductor is centered
        ax.set_xlim(0 - Wcond / 10, Wcond * 11.0 / 10.0)
        ax.set_ylim(0 - Hcond / 10, Hcond * 11.0 / 10.0)

        # Legend
        patch_leg = list()  # Symbol
        label_leg = list()  # Text
        if self.Wins_wire > 0:
            patch_leg.append(Patch(color=INS_COLOR))
            label_leg.append("Wire insulation")

        patch_leg.append(Patch(color=COND_COLOR))
        label_leg.append("Active wire section")

        ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # cf Methods.Machine.CondType11.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_add_schematics=True,
        is_add_main_line=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
        is_single=False,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Use some default parameter
        if is_default and is_single:
            cond = type(self)(
                Hwire=10e-3, Wwire=22e-3, Wins_wire=2e-3, Nwppc_rad=1, Nwppc_tan=1
            )
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
                is_single=is_single,
            )
        elif is_default:
            cond = type(self)(
                Hwire=10e-3, Wwire=22e-3, Wins_wire=2e-3, Nwppc_rad=3, Nwppc_tan=2
            )
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            fig, ax = self.plot(
                is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis

            # Adding schematics
            if is_add_schematics:
                if is_single:
                    # Wwire
                    line = Segment(
                        self.Wins_wire + 1j * (self.Wins_wire + self.Hwire / 2),
                        self.Wins_wire
                        + self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor width",
                        offset_label=-4 * self.Wins_wire - 1j * 2 * self.Wins_wire / 3,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Hwire
                    line = Segment(
                        1j * (self.Wins_wire) + (self.Wins_wire + self.Wwire / 2),
                        1j * (self.Wins_wire + self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor height",
                        offset_label=self.Wins_wire / 3 + 1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        2 * self.Wins_wire + 1j * (2 * self.Wins_wire + self.Hwire),
                        2 * self.Wins_wire + 1j * (self.Wins_wire + self.Hwire),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                else:
                    # Wwire
                    line = Segment(
                        3 * self.Wins_wire
                        + self.Wwire
                        + 1j * (3 * self.Wins_wire + self.Hwire * 3 / 2),
                        3 * self.Wins_wire
                        + 2 * self.Wwire
                        + 1j * (3 * self.Wins_wire + self.Hwire * 3 / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand width",
                        offset_label=1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Hwire
                    line = Segment(
                        1j * (3 * self.Wins_wire + self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                        1j * (3 * self.Wins_wire + 2 * self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand height",
                        offset_label=self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        2 * self.Wins_wire
                        + self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                        3 * self.Wins_wire
                        + 1 * self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Nwppc_rad/tan
                    ax.text(
                        -self.Wins_wire,
                        5 * self.Wins_wire + 2.5 * self.Hwire,
                        "Strands in radial direction: 3\nStrands in tangential direction: 2",
                        fontsize=SC_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            if is_add_main_line:
                for ii in range(1, self.Nwppc_tan):
                    line = Segment(
                        ii * (self.Wwire + 2 * self.Wins_wire),
                        ii * (self.Wwire + 2 * self.Wins_wire)
                        + 1j * self.comp_height(),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                for ii in range(1, self.Nwppc_rad):
                    line = Segment(
                        1j * ii * (self.Hwire + 2 * self.Wins_wire),
                        1j * ii * (self.Hwire + 2 * self.Wins_wire) + self.comp_width(),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

            # Zooming and cleaning
            W = self.comp_width() * 1.1
            H = self.comp_height() * 1.1

            ax.axis("equal")
            ax.set_xlim(-W * 0.1, W)
            ax.set_ylim(-H * 0.1, H)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Hwire=0.01,
        Wwire=0.01,
        Nwppc_rad=1,
        Nwppc_tan=1,
        Wins_wire=0,
        Wins_coil=0,
        type_winding_shape=0,
        alpha_ew=58,
        cond_mat=-1,
        ins_mat=-1,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "Hwire" in list(init_dict.keys()):
                Hwire = init_dict["Hwire"]
            if "Wwire" in list(init_dict.keys()):
                Wwire = init_dict["Wwire"]
            if "Nwppc_rad" in list(init_dict.keys()):
                Nwppc_rad = init_dict["Nwppc_rad"]
            if "Nwppc_tan" in list(init_dict.keys()):
                Nwppc_tan = init_dict["Nwppc_tan"]
            if "Wins_wire" in list(init_dict.keys()):
                Wins_wire = init_dict["Wins_wire"]
            if "Wins_coil" in list(init_dict.keys()):
                Wins_coil = init_dict["Wins_coil"]
            if "type_winding_shape" in list(init_dict.keys()):
                type_winding_shape = init_dict["type_winding_shape"]
            if "alpha_ew" in list(init_dict.keys()):
                alpha_ew = init_dict["alpha_ew"]
            if "cond_mat" in list(init_dict.keys()):
                cond_mat = init_dict["cond_mat"]
            if "ins_mat" in list(init_dict.keys()):
                ins_mat = init_dict["ins_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.Hwire = Hwire
        self.Wwire = Wwire
        self.Nwppc_rad = Nwppc_rad
        self.Nwppc_tan = Nwppc_tan
        self.Wins_wire = Wins_wire
        self.Wins_coil = Wins_coil
        self.type_winding_shape = type_winding_shape
        self.alpha_ew = alpha_ew
        # Call Conductor init
        super(CondType11, self).__init__(cond_mat=cond_mat, ins_mat=ins_mat)
        # The class is frozen (in Conductor init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        CondType11_str = ""
        # Get the properties inherited from Conductor
        CondType11_str += super(CondType11, self).__str__()
        CondType11_str += "Hwire = " + str(self.Hwire) + linesep
        CondType11_str += "Wwire = " + str(self.Wwire) + linesep
        CondType11_str += "Nwppc_rad = " + str(self.Nwppc_rad) + linesep
        CondType11_str += "Nwppc_tan = " + str(self.Nwppc_tan) + linesep
        CondType11_str += "Wins_wire = " + str(self.Wins_wire) + linesep
        CondType11_str += "Wins_coil = " + str(self.Wins_coil) + linesep
        CondType11_str += (
            "type_winding_shape = " + str(self.type_winding_shape) + linesep
        )
        CondType11_str += "alpha_ew = " + str(self.alpha_ew) + linesep
        return CondType11_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Conductor
        if not super(CondType11, self).__eq__(other):
            return False
        if other.Hwire != self.Hwire:
            return False
        if other.Wwire != self.Wwire:
            return False
        if other.Nwppc_rad != self.Nwppc_rad:
            return False
        if other.Nwppc_tan != self.Nwppc_tan:
            return False
        if other.Wins_wire != self.Wins_wire:
            return False
        if other.Wins_coil != self.Wins_coil:
            return False
        if other.type_winding_shape != self.type_winding_shape:
            return False
        if other.alpha_ew != self.alpha_ew:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Conductor
        diff_list.extend(
            super(CondType11, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Hwire is not None
            and self._Hwire is not None
            and isnan(other._Hwire)
            and isnan(self._Hwire)
        ):
            pass
        elif other._Hwire != self._Hwire:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Hwire) + ", other=" + str(other._Hwire) + ")"
                )
                diff_list.append(name + ".Hwire" + val_str)
            else:
                diff_list.append(name + ".Hwire")
        if (
            other._Wwire is not None
            and self._Wwire is not None
            and isnan(other._Wwire)
            and isnan(self._Wwire)
        ):
            pass
        elif other._Wwire != self._Wwire:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Wwire) + ", other=" + str(other._Wwire) + ")"
                )
                diff_list.append(name + ".Wwire" + val_str)
            else:
                diff_list.append(name + ".Wwire")
        if other._Nwppc_rad != self._Nwppc_rad:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nwppc_rad)
                    + ", other="
                    + str(other._Nwppc_rad)
                    + ")"
                )
                diff_list.append(name + ".Nwppc_rad" + val_str)
            else:
                diff_list.append(name + ".Nwppc_rad")
        if other._Nwppc_tan != self._Nwppc_tan:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nwppc_tan)
                    + ", other="
                    + str(other._Nwppc_tan)
                    + ")"
                )
                diff_list.append(name + ".Nwppc_tan" + val_str)
            else:
                diff_list.append(name + ".Nwppc_tan")
        if (
            other._Wins_wire is not None
            and self._Wins_wire is not None
            and isnan(other._Wins_wire)
            and isnan(self._Wins_wire)
        ):
            pass
        elif other._Wins_wire != self._Wins_wire:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Wins_wire)
                    + ", other="
                    + str(other._Wins_wire)
                    + ")"
                )
                diff_list.append(name + ".Wins_wire" + val_str)
            else:
                diff_list.append(name + ".Wins_wire")
        if (
            other._Wins_coil is not None
            and self._Wins_coil is not None
            and isnan(other._Wins_coil)
            and isnan(self._Wins_coil)
        ):
            pass
        elif other._Wins_coil != self._Wins_coil:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Wins_coil)
                    + ", other="
                    + str(other._Wins_coil)
                    + ")"
                )
                diff_list.append(name + ".Wins_coil" + val_str)
            else:
                diff_list.append(name + ".Wins_coil")
        if other._type_winding_shape != self._type_winding_shape:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_winding_shape)
                    + ", other="
                    + str(other._type_winding_shape)
                    + ")"
                )
                diff_list.append(name + ".type_winding_shape" + val_str)
            else:
                diff_list.append(name + ".type_winding_shape")
        if (
            other._alpha_ew is not None
            and self._alpha_ew is not None
            and isnan(other._alpha_ew)
            and isnan(self._alpha_ew)
        ):
            pass
        elif other._alpha_ew != self._alpha_ew:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._alpha_ew)
                    + ", other="
                    + str(other._alpha_ew)
                    + ")"
                )
                diff_list.append(name + ".alpha_ew" + val_str)
            else:
                diff_list.append(name + ".alpha_ew")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Conductor
        S += super(CondType11, self).__sizeof__()
        S += getsizeof(self.Hwire)
        S += getsizeof(self.Wwire)
        S += getsizeof(self.Nwppc_rad)
        S += getsizeof(self.Nwppc_tan)
        S += getsizeof(self.Wins_wire)
        S += getsizeof(self.Wins_coil)
        S += getsizeof(self.type_winding_shape)
        S += getsizeof(self.alpha_ew)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from Conductor
        CondType11_dict = super(CondType11, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        CondType11_dict["Hwire"] = self.Hwire
        CondType11_dict["Wwire"] = self.Wwire
        CondType11_dict["Nwppc_rad"] = self.Nwppc_rad
        CondType11_dict["Nwppc_tan"] = self.Nwppc_tan
        CondType11_dict["Wins_wire"] = self.Wins_wire
        CondType11_dict["Wins_coil"] = self.Wins_coil
        CondType11_dict["type_winding_shape"] = self.type_winding_shape
        CondType11_dict["alpha_ew"] = self.alpha_ew
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        CondType11_dict["__class__"] = "CondType11"
        return CondType11_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Hwire_val = self.Hwire
        Wwire_val = self.Wwire
        Nwppc_rad_val = self.Nwppc_rad
        Nwppc_tan_val = self.Nwppc_tan
        Wins_wire_val = self.Wins_wire
        Wins_coil_val = self.Wins_coil
        type_winding_shape_val = self.type_winding_shape
        alpha_ew_val = self.alpha_ew
        if self.cond_mat is None:
            cond_mat_val = None
        else:
            cond_mat_val = self.cond_mat.copy()
        if self.ins_mat is None:
            ins_mat_val = None
        else:
            ins_mat_val = self.ins_mat.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Hwire=Hwire_val,
            Wwire=Wwire_val,
            Nwppc_rad=Nwppc_rad_val,
            Nwppc_tan=Nwppc_tan_val,
            Wins_wire=Wins_wire_val,
            Wins_coil=Wins_coil_val,
            type_winding_shape=type_winding_shape_val,
            alpha_ew=alpha_ew_val,
            cond_mat=cond_mat_val,
            ins_mat=ins_mat_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Hwire = None
        self.Wwire = None
        self.Nwppc_rad = None
        self.Nwppc_tan = None
        self.Wins_wire = None
        self.Wins_coil = None
        self.type_winding_shape = None
        self.alpha_ew = None
        # Set to None the properties inherited from Conductor
        super(CondType11, self)._set_None()

    def _get_Hwire(self):
        """getter of Hwire"""
        return self._Hwire

    def _set_Hwire(self, value):
        """setter of Hwire"""
        check_var("Hwire", value, "float", Vmin=0)
        self._Hwire = value

    Hwire = property(
        fget=_get_Hwire,
        fset=_set_Hwire,
        doc="""cf schematics, single strand height without insulation

        :Type: float
        :min: 0
        """,
    )

    def _get_Wwire(self):
        """getter of Wwire"""
        return self._Wwire

    def _set_Wwire(self, value):
        """setter of Wwire"""
        check_var("Wwire", value, "float", Vmin=0)
        self._Wwire = value

    Wwire = property(
        fget=_get_Wwire,
        fset=_set_Wwire,
        doc="""cf schematics, single strand width without insulation

        :Type: float
        :min: 0
        """,
    )

    def _get_Nwppc_rad(self):
        """getter of Nwppc_rad"""
        return self._Nwppc_rad

    def _set_Nwppc_rad(self, value):
        """setter of Nwppc_rad"""
        check_var("Nwppc_rad", value, "int", Vmin=1)
        self._Nwppc_rad = value

    Nwppc_rad = property(
        fget=_get_Nwppc_rad,
        fset=_set_Nwppc_rad,
        doc="""number of form wound strands in parallel per conductor along radial (vertical) direction

        :Type: int
        :min: 1
        """,
    )

    def _get_Nwppc_tan(self):
        """getter of Nwppc_tan"""
        return self._Nwppc_tan

    def _set_Nwppc_tan(self, value):
        """setter of Nwppc_tan"""
        check_var("Nwppc_tan", value, "int", Vmin=1)
        self._Nwppc_tan = value

    Nwppc_tan = property(
        fget=_get_Nwppc_tan,
        fset=_set_Nwppc_tan,
        doc="""number of form wound strands in parallel per conductor along tangential (horizontal) direction

        :Type: int
        :min: 1
        """,
    )

    def _get_Wins_wire(self):
        """getter of Wins_wire"""
        return self._Wins_wire

    def _set_Wins_wire(self, value):
        """setter of Wins_wire"""
        check_var("Wins_wire", value, "float", Vmin=0)
        self._Wins_wire = value

    Wins_wire = property(
        fget=_get_Wins_wire,
        fset=_set_Wins_wire,
        doc="""(advanced) cf schematics, winding strand insulation thickness

        :Type: float
        :min: 0
        """,
    )

    def _get_Wins_coil(self):
        """getter of Wins_coil"""
        return self._Wins_coil

    def _set_Wins_coil(self, value):
        """setter of Wins_coil"""
        check_var("Wins_coil", value, "float", Vmin=0)
        self._Wins_coil = value

    Wins_coil = property(
        fget=_get_Wins_coil,
        fset=_set_Wins_coil,
        doc="""(advanced) cf schematics, winding coil insulation  thickness

        :Type: float
        :min: 0
        """,
    )

    def _get_type_winding_shape(self):
        """getter of type_winding_shape"""
        return self._type_winding_shape

    def _set_type_winding_shape(self, value):
        """setter of type_winding_shape"""
        check_var("type_winding_shape", value, "int", Vmin=0, Vmax=1)
        self._type_winding_shape = value

    type_winding_shape = property(
        fget=_get_type_winding_shape,
        fset=_set_type_winding_shape,
        doc="""type of winding shape for end winding length calculation\n0 for hairpin windings\n1 for normal windings

        :Type: int
        :min: 0
        :max: 1
        """,
    )

    def _get_alpha_ew(self):
        """getter of alpha_ew"""
        return self._alpha_ew

    def _set_alpha_ew(self, value):
        """setter of alpha_ew"""
        check_var("alpha_ew", value, "float", Vmin=0, Vmax=180)
        self._alpha_ew = value

    alpha_ew = property(
        fget=_get_alpha_ew,
        fset=_set_alpha_ew,
        doc="""angle of winding overhang hairpin coils [deg]

        :Type: float
        :min: 0
        :max: 180
        """,
    )
