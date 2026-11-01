# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/CondType12.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/CondType12
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - check: module uses a wildcard import whose names cannot be resolved safely
# - plot: import name 'pi' refers to different sources (numpy.pi and ..Methods.Machine.CondType12.plot.pi)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Conductor import Conductor

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Machine.CondType12.check import check
from ..Methods.Machine.CondType12.plot import plot
from numpy import sqrt, pi
import matplotlib.pyplot as plt
from .Segment import Segment
from ..Functions.Plot import ARROW_COLOR, ARROW_WIDTH, SC_FONT_SIZE, TEXT_BOX

from numpy import isnan
from ._check import InitUnKnowClassError


class CondType12(Conductor):
    """parallel stranded conductor consisting of at least a single round wire"""

    VERSION = 1

    # cf Methods.Machine.CondType12.check
    check = check

    # cf Methods.Machine.CondType12.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return self.comp_width()

    # cf Methods.Machine.CondType12.comp_height_wire
    def comp_height_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Wire diameter [m]

        """

        return self.Wwire

    # cf Methods.Machine.CondType12.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return int(sqrt(self.Nwppc))

    # cf Methods.Machine.CondType12.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Nwppc_rad: int
            Number of adjacent wires in radial direction

        """

        return int(sqrt(self.Nwppc))

    # cf Methods.Machine.CondType12.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        return pi * ((self.comp_width() / 2.0) ** 2)

    # cf Methods.Machine.CondType12.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = ((self.Wwire / 2.0) ** 2) * pi * self.Nwppc

        return Sact

    # cf Methods.Machine.CondType12.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        if self.Wins_cond is None:
            if self.Nwppc == 1:
                Wins_wire = self.Wins_wire if self.Wins_wire is not None else 0
                width = self.Wwire + 2 * Wins_wire
            else:
                raise Exception("Conductor diameter not set")
        else:
            width = self.Wins_cond

        return width

    # cf Methods.Machine.CondType12.comp_width_wire
    def comp_width_wire(self):
        """Return wire diameter

        Parameters
        ----------
        self : CondType12
            A CondType12 object

        Returns
        -------
        W: float
            Wire diameter [m]

        """

        return self.Wwire

    # cf Methods.Machine.CondType12.is_round_wire
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

        return True

    # cf Methods.Machine.CondType12.plot
    plot = plot

    # cf Methods.Machine.CondType12.plot_schematics
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
        self : CondType12
            A CondType12 object
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
            cond = type(self)(Wins_cond=40e-3, Wwire=35e-3, Wins_wire=5e-3, Nwppc=1)
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
            cond = type(self)(Wins_cond=40e-3, Wwire=10e-3, Wins_wire=2e-3, Nwppc=4)
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
            a = self.Wwire / 2 + self.Wins_wire

            # Adding schematics
            if is_add_schematics:
                if is_single:
                    # Wwire
                    line = Segment(-self.Wwire / 2, self.Wwire / 2)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor diameter",
                        offset_label=1j * self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        1j * (self.Wwire / 2 + self.Wins_wire), 1j * self.Wwire / 2
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
                        a - self.Wwire / 2 + 1j * a, a + self.Wwire / 2 + 1j * a
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand diameter",
                        offset_label=1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        -self.Wwire / 2 - self.Wins_wire + 1j * self.Wins_wire,
                        -self.Wwire / 2 - self.Wins_wire,
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=-8 * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_cond
                    line = Segment(-1j * self.Wins_cond / 2, 1j * self.Wins_cond / 2)
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Overall diameter",
                        offset_label=-1j * self.Wins_cond * 0.25 + self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Nwppc_rad
                    ax.text(
                        -a - 2 * self.Wwire,
                        2.5 * a,
                        "Strands in hand: 4",
                        fontsize=SC_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            # Zooming and cleaning
            if is_single:
                W = self.comp_width() * 1.2
            else:
                W = self.comp_width() * 1.05

            ax.axis("equal")
            ax.set_xlim(-W / 2, W / 2)
            ax.set_ylim(-W / 2, W / 2)
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
        Wwire=0.015,
        Wins_cond=0.015,
        Nwppc=1,
        Wins_wire=0,
        Kwoh=0.5,
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
            if "Wwire" in list(init_dict.keys()):
                Wwire = init_dict["Wwire"]
            if "Wins_cond" in list(init_dict.keys()):
                Wins_cond = init_dict["Wins_cond"]
            if "Nwppc" in list(init_dict.keys()):
                Nwppc = init_dict["Nwppc"]
            if "Wins_wire" in list(init_dict.keys()):
                Wins_wire = init_dict["Wins_wire"]
            if "Kwoh" in list(init_dict.keys()):
                Kwoh = init_dict["Kwoh"]
            if "cond_mat" in list(init_dict.keys()):
                cond_mat = init_dict["cond_mat"]
            if "ins_mat" in list(init_dict.keys()):
                ins_mat = init_dict["ins_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.Wwire = Wwire
        self.Wins_cond = Wins_cond
        self.Nwppc = Nwppc
        self.Wins_wire = Wins_wire
        self.Kwoh = Kwoh
        # Call Conductor init
        super(CondType12, self).__init__(cond_mat=cond_mat, ins_mat=ins_mat)
        # The class is frozen (in Conductor init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        CondType12_str = ""
        # Get the properties inherited from Conductor
        CondType12_str += super(CondType12, self).__str__()
        CondType12_str += "Wwire = " + str(self.Wwire) + linesep
        CondType12_str += "Wins_cond = " + str(self.Wins_cond) + linesep
        CondType12_str += "Nwppc = " + str(self.Nwppc) + linesep
        CondType12_str += "Wins_wire = " + str(self.Wins_wire) + linesep
        CondType12_str += "Kwoh = " + str(self.Kwoh) + linesep
        return CondType12_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Conductor
        if not super(CondType12, self).__eq__(other):
            return False
        if other.Wwire != self.Wwire:
            return False
        if other.Wins_cond != self.Wins_cond:
            return False
        if other.Nwppc != self.Nwppc:
            return False
        if other.Wins_wire != self.Wins_wire:
            return False
        if other.Kwoh != self.Kwoh:
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
            super(CondType12, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
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
        if (
            other._Wins_cond is not None
            and self._Wins_cond is not None
            and isnan(other._Wins_cond)
            and isnan(self._Wins_cond)
        ):
            pass
        elif other._Wins_cond != self._Wins_cond:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Wins_cond)
                    + ", other="
                    + str(other._Wins_cond)
                    + ")"
                )
                diff_list.append(name + ".Wins_cond" + val_str)
            else:
                diff_list.append(name + ".Wins_cond")
        if other._Nwppc != self._Nwppc:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Nwppc) + ", other=" + str(other._Nwppc) + ")"
                )
                diff_list.append(name + ".Nwppc" + val_str)
            else:
                diff_list.append(name + ".Nwppc")
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
            other._Kwoh is not None
            and self._Kwoh is not None
            and isnan(other._Kwoh)
            and isnan(self._Kwoh)
        ):
            pass
        elif other._Kwoh != self._Kwoh:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Kwoh) + ", other=" + str(other._Kwoh) + ")"
                )
                diff_list.append(name + ".Kwoh" + val_str)
            else:
                diff_list.append(name + ".Kwoh")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Conductor
        S += super(CondType12, self).__sizeof__()
        S += getsizeof(self.Wwire)
        S += getsizeof(self.Wins_cond)
        S += getsizeof(self.Nwppc)
        S += getsizeof(self.Wins_wire)
        S += getsizeof(self.Kwoh)
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
        CondType12_dict = super(CondType12, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        CondType12_dict["Wwire"] = self.Wwire
        CondType12_dict["Wins_cond"] = self.Wins_cond
        CondType12_dict["Nwppc"] = self.Nwppc
        CondType12_dict["Wins_wire"] = self.Wins_wire
        CondType12_dict["Kwoh"] = self.Kwoh
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        CondType12_dict["__class__"] = "CondType12"
        return CondType12_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Wwire_val = self.Wwire
        Wins_cond_val = self.Wins_cond
        Nwppc_val = self.Nwppc
        Wins_wire_val = self.Wins_wire
        Kwoh_val = self.Kwoh
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
            Wwire=Wwire_val,
            Wins_cond=Wins_cond_val,
            Nwppc=Nwppc_val,
            Wins_wire=Wins_wire_val,
            Kwoh=Kwoh_val,
            cond_mat=cond_mat_val,
            ins_mat=ins_mat_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Wwire = None
        self.Wins_cond = None
        self.Nwppc = None
        self.Wins_wire = None
        self.Kwoh = None
        # Set to None the properties inherited from Conductor
        super(CondType12, self)._set_None()

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
        doc="""cf schematics, single strand diameter without insulation

        :Type: float
        :min: 0
        """,
    )

    def _get_Wins_cond(self):
        """getter of Wins_cond"""
        return self._Wins_cond

    def _set_Wins_cond(self, value):
        """setter of Wins_cond"""
        check_var("Wins_cond", value, "float", Vmin=0)
        self._Wins_cond = value

    Wins_cond = property(
        fget=_get_Wins_cond,
        fset=_set_Wins_cond,
        doc="""(advanced) cf schematics, conductor diameter

        :Type: float
        :min: 0
        """,
    )

    def _get_Nwppc(self):
        """getter of Nwppc"""
        return self._Nwppc

    def _set_Nwppc(self, value):
        """setter of Nwppc"""
        check_var("Nwppc", value, "int", Vmin=1)
        self._Nwppc = value

    Nwppc = property(
        fget=_get_Nwppc,
        fset=_set_Nwppc,
        doc="""number of strands in parallel per conductor

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

    def _get_Kwoh(self):
        """getter of Kwoh"""
        return self._Kwoh

    def _set_Kwoh(self, value):
        """setter of Kwoh"""
        check_var("Kwoh", value, "float", Vmin=0)
        self._Kwoh = value

    Kwoh = property(
        fget=_get_Kwoh,
        fset=_set_Kwoh,
        doc="""winding overhang factor which describes the fact that random round wire end-windings can be more or less compressed (0.5 for small motors, 0.8 for large motors) - can be used to tune the average turn length (relevant if type_cond==1)

        :Type: float
        :min: 0
        """,
    )
