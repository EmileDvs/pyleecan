# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM17.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM17
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
from pyleecan.Classes.Slot import Slot

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Slot.Slot import SlotCheckError
from numpy import pi, exp
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Methods.Slot.SlotM17.plot_schematics import MAGNET_COLOR
import matplotlib.pyplot as plt
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
)
from pyleecan.Methods import ParentMissingError

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class SlotM17(Slot):
    """Full rotor magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1

    # cf Methods.Slot.SlotM17.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        curve_list: list
            Empty list (no lamination, only active surface)

        """

        return list()

    # cf Methods.Slot.SlotM17.check
    def check(self):
        """Check that the SlotM17 object is correct

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        None
        """
        if self.parent is None:
            raise SlotCheckError("SlotM17 must be inside a lamination")
        if self.Zs != 2:
            raise SlotCheckError("SlotM17 must have p=1")
        if not self.parent.is_internal:
            raise SlotCheckError("SlotM17 must be inside an internal lamination")

    # cf Methods.Slot.SlotM17.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return pi

    # cf Methods.Slot.SlotM17.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return self.parent.Rext - self.parent.Rint

    # cf Methods.Slot.SlotM17.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.parent.Rext - self.parent.Rint

    # cf Methods.Slot.SlotM17.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return pi / 2 * (self.parent.Rext**2 - self.parent.Rint**2)

    # cf Methods.Slot.SlotM17.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        Swind: float
            Slot inner active surface [m**2]

        """

        return pi / 2 * (self.parent.Rext**2 - self.parent.Rint**2)

    # cf Methods.Slot.SlotM17.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """

        self.check()
        # get the name of the lamination
        st = self.get_name_lam()
        Rext = self.parent.Rext
        Rint = self.parent.Rint

        Z1 = -Rext * 1j
        Z2 = Rext
        Z3 = Rext * 1j
        curve_list = list()
        curve_list.append(Arc1(Z1, Z2, Rext, True))
        curve_list.append(Arc1(Z2, Z3, Rext, True))
        if Rint == 0:
            curve_list.append(Segment(Z3, Z1))
        else:
            Z4 = Rint * 1j
            Z5 = Rint
            Z6 = -Rint * 1j
            curve_list.append(Segment(Z3, Z4))
            curve_list.append(Arc1(Z4, Z5, -Rint, False))
            curve_list.append(Arc1(Z5, Z6, -Rint, False))
            curve_list.append(Segment(Z6, Z1))

        surface = SurfLine(
            line_list=curve_list,
            label="Wind_" + st + "_R0_T0_S0",
            point_ref=Rint + (Rext - Rint) / 2,
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM17.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return True

    # cf Methods.Slot.SlotM17.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return True

    # cf Methods.Slot.SlotM17.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotM17
            A SlotM17 object
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
            0: No active surface, 1: active surface as winding, 2: active surface as magnet
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
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            slot = type(self)(Zs=2)
            lam = LamSlot(
                Rint=0.05, Rext=0.135, is_internal=True, is_stator=False, slot=slot
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
                )
        else:
            # Getting the main plot
            if self.parent is None:
                raise ParentMissingError("Error: The slot is not inside a Lamination")
            lam = self.parent
            fig, ax = lam.plot(
                alpha=pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis

            # Adding schematics
            if is_add_schematics:
                # Rext
                line = Segment(0, lam.Rext * exp(1j * pi / 4))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rext",
                    offset_label=0.2 * lam.Rext,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Rint
                line = Segment(0, lam.Rint * exp(1j * 7 * pi / 4))
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rint",
                    offset_label=0.2 * lam.Rint,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(-lam.Rext * 2.5, lam.Rext * 2.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            if type_add_active == 1:
                self.plot_active(fig=fig, ax=ax, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = lam.Rext * 1.1

            ax.axis("equal")
            ax.set_xlim(-W, W)
            ax.set_ylim(-W, W)
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, Zs=36, wedge_mat=None, is_bore=True, init_dict=None, init_str=None
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
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        # Call Slot init
        super(SlotM17, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM17_str = ""
        # Get the properties inherited from Slot
        SlotM17_str += super(SlotM17, self).__str__()
        return SlotM17_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM17, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Slot
        diff_list.extend(
            super(SlotM17, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotM17, self).__sizeof__()
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

        # Get the properties inherited from Slot
        SlotM17_dict = super(SlotM17, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM17_dict["__class__"] = "SlotM17"
        return SlotM17_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(Zs=Zs_val, wedge_mat=wedge_mat_val, is_bore=is_bore_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from Slot
        super(SlotM17, self)._set_None()
