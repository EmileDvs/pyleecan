# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotM18.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotM18
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
import numpy as np, matplotlib.pyplot as plt
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Functions.labels import (
    COND_BOUNDARY_PROP_LAB,
    YSMR_LAB,
    YSML_LAB,
    YOKE_LAB,
)
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.definitions import config_dict
from pyleecan.Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from pyleecan.Classes import ParentMissingError


from pyleecan.Classes._check import InitUnKnowClassError


class SlotM18(Slot):
    """Polar Ring magnet"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotM18._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        sp = 2 * np.pi / self.Zs
        Z1 = Rbo * np.exp(-1j * sp / 2)
        ZM1 = Rbo * np.exp(-1j * sp / 2)

        if self.is_outwards():
            ZM2 = (Rbo - self.H0) * np.exp(-1j * sp / 2)
        else:  # inward slot
            ZM2 = (Rbo + self.H0) * np.exp(-1j * sp / 2)

        point_dict = dict()
        point_dict["Z1"] = Z1
        point_dict["ZM1"] = ZM1
        point_dict["ZM2"] = ZM2
        # symetry
        point_dict["Z2"] = Z1.conjugate()
        point_dict["ZM3"] = ZM2.conjugate()
        point_dict["ZM4"] = ZM1.conjugate()

        return point_dict

    # cf Methods.Slot.SlotM18.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        curve_list: list
            A list of 3 Segments

        """
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]

        # Creation of curve
        curve_list = list()
        curve_list.append(Arc1(Z1, Z2, Rbo, is_trigo_direction=True))

        return curve_list

    # cf Methods.Slot.SlotM18.check
    def check(self):
        """Check that the SlotM18 object is correct

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        None
        """
        pass

    # cf Methods.Slot.SlotM18.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]

        """

        return 2 * np.pi / self.Zs

    # cf Methods.Slot.SlotM18.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Htot: float
            Height of the slot [m]

        """

        return 0

    # cf Methods.Slot.SlotM18.comp_height_active
    def comp_height_active(self):
        """Compute the height of the active area

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Hwind: float
            Height of the active area [m]

        """

        return self.H0

    # cf Methods.Slot.SlotM18.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return 0

    # cf Methods.Slot.SlotM18.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner active surface (by analytical computation)

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        Swind: float
            Slot inner active surface [m**2]

        """

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]

        R1 = abs(ZM1)
        R2 = abs(ZM2)

        S1 = np.pi * R1**2 / self.Zs
        S2 = np.pi * R2**2 / self.Zs

        return abs(S1 - S2)

    # cf Methods.Slot.SlotM18.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_act: Surface
            Surface corresponding to the Active Area
        """

        # get the name of the lamination
        st = self.get_name_lam()
        Rbo = self.get_Rbo()

        point_dict = self._comp_point_coordinate()
        ZM1 = point_dict["ZM1"]
        ZM2 = point_dict["ZM2"]
        ZM3 = point_dict["ZM3"]
        ZM4 = point_dict["ZM4"]

        curve_list = list()
        curve_list.append(
            Segment(ZM1, ZM2, prop_dict={COND_BOUNDARY_PROP_LAB: YSMR_LAB})
        )

        if self.is_outwards():
            curve_list.append(Arc1(ZM2, ZM3, (Rbo - self.H0), is_trigo_direction=True))
        else:
            curve_list.append(Arc1(ZM2, ZM3, (Rbo + self.H0), is_trigo_direction=True))

        curve_list.append(
            Segment(ZM3, ZM4, prop_dict={COND_BOUNDARY_PROP_LAB: YSML_LAB})
        )

        if self.is_outwards():
            curve_list.append(Arc1(ZM4, ZM1, -Rbo, is_trigo_direction=False))
        else:
            curve_list.append(Arc1(ZM4, ZM1, -Rbo, is_trigo_direction=False))
        # If no lamination, BC is required on bore
        curve_list[-1].prop_dict = {COND_BOUNDARY_PROP_LAB: YOKE_LAB}

        Zmid = (abs(ZM1) + abs(ZM3)) / 2

        surface = SurfLine(
            line_list=curve_list, label="Wind_" + st + "_R0_T0_S0", point_ref=Zmid
        )

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotM18.is_airgap_active
    def is_airgap_active(self):
        """Return True if a part or the full active surface is in the airgap

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        is_airgap_active : bool
            True if a part or the full active surface is in the airgap
        """

        return True

    # cf Methods.Slot.SlotM18.is_full_pitch_active
    def is_full_pitch_active(self):
        """Returns True if the active surface angular width
        matches the slot pitch (like SlotM17 or SlotM18)
        (used to set Boundary conditions in FEMM airgap)

        Parameters
        ----------
        self : SlotM18
            A SlotM18 object

        Returns
        -------
        is_full_pitch_active : bool
            True if the active surface angular width matches the slot pitch
        """

        return True

    # cf Methods.Slot.SlotM18.plot_schematics
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
        self : SlotM18
            A SlotM18 object
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
            slot = type(self)(Zs=16, H0=15e-3)
            lam = LamSlot(
                Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
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
                alpha=np.pi / self.Zs, is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis
            point_dict = self._comp_point_coordinate()
            if self.is_outwards():
                sign = +1
            else:
                sign = -1
            Rbo = self.get_Rbo()

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
                # H0
                line = Segment(point_dict["ZM3"], point_dict["ZM4"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * self.H0 * 0.7,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Ox axis
                line = Segment(0, lam.Rext * 1.5)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Magnet separation lines
                for ii in range(self.Zs):
                    line = Segment(
                        point_dict["ZM1"] * np.exp(1j * 2 * np.pi / self.Zs * ii),
                        point_dict["ZM2"] * np.exp(1j * 2 * np.pi / self.Zs * ii),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color="k",
                        linestyle="-",
                        linewidth=MAIN_LINE_WIDTH,
                    )

            if type_add_active == 1:
                self.plot_active(fig=fig, ax=ax, is_show_fig=False)
            elif type_add_active == 2:
                self.plot_active(
                    fig=fig,
                    ax=ax,
                    is_show_fig=False,
                    enforced_default_color=self.MAGNET_COLOR,
                )

            # Zooming and cleaning
            W = point_dict["ZM3"].imag * 3
            Rint, Rext = self.comp_radius()

            ax.axis("equal")
            ax.set_xlim(Rint, Rext)
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
        self,
        H0=0.001,
        Zs=36,
        wedge_mat=None,
        is_bore=True,
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
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.H0 = H0
        # Call Slot init
        super(SlotM18, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotM18_str = ""
        # Get the properties inherited from Slot
        SlotM18_str += super(SlotM18, self).__str__()
        SlotM18_str += "H0 = " + str(self.H0) + linesep
        return SlotM18_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotM18, self).__eq__(other):
            return False
        if other.H0 != self.H0:
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
            super(SlotM18, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._H0 is not None
            and self._H0 is not None
            and np.isnan(other._H0)
            and np.isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotM18, self).__sizeof__()
        S += getsizeof(self.H0)
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
        SlotM18_dict = super(SlotM18, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotM18_dict["H0"] = self.H0
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotM18_dict["__class__"] = "SlotM18"
        return SlotM18_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        H0_val = self.H0
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            H0=H0_val, Zs=Zs_val, wedge_mat=wedge_mat_val, is_bore=is_bore_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.H0 = None
        # Set to None the properties inherited from Slot
        super(SlotM18, self)._set_None()

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Magnet Height

        :Type: float
        :min: 0
        """,
    )
