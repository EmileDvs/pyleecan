# File generated according to Generator/ClassesRef/Slot/SlotCirc.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotCirc"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.LamSlot import LamSlot
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.Slot import Slot
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var
from pyleecan.definitions import config_dict
from pyleecan.Functions.Geometry.circle_from_3_points import circle_from_3_points
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import DRAW_PROP_LAB, WIND_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SlotCirc(Slot):
    """Circular slot (for notches)"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.SlotCirc._comp_line_dict
    def _comp_line_dict(self):
        """Define a dictionnary of the lines to draw the slot
        If a line has begin==end, it is replaced by "None" (dict has always the same number of keys)

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        line_dict: dict
            Dictionnary of the slot lines (key: line name, value: line object)
        """

        point_dict = self._comp_point_coordinate()
        R0 = self._comp_R0()

        if self.H0 < self.W0 / 2:
            sign = -1
        else:
            sign = 1
        # Creation of curve
        if self.is_outwards():
            full_arc = Arc1(
                begin=point_dict["Z1"],
                end=point_dict["Z2"],
                radius=-R0 * sign,
                is_trigo_direction=True,
            )
        else:
            full_arc = Arc1(
                begin=point_dict["Z1"],
                end=point_dict["Z2"],
                radius=R0 * sign,
                is_trigo_direction=False,
            )

        line_dict = dict()
        line_dict["1-2"] = full_arc
        # Split arc to avoid angle > 180 deg (for FEMM)
        line_dict["1-M"] = full_arc.copy()
        line_dict["1-M"].split_half(is_begin=True)
        line_dict["M-2"] = full_arc.copy()
        line_dict["M-2"].split_half(is_begin=False)
        # Closing arc
        line_dict["2-1"] = Arc1(
            point_dict["Z2"],
            point_dict["Z1"],
            -self.get_Rbo(),
            is_trigo_direction=False,
        )

        return line_dict

    # cf Methods.Slot.SlotCirc._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value
        Rbo = self.get_Rbo()
        alpha = self.comp_angle_opening()

        Z1 = Rbo * np.exp(-1j * alpha / 2)
        Z2 = Rbo * np.exp(1j * alpha / 2)
        if self.is_H0_bore:
            if self.is_outwards():
                ZM = Rbo + self.H0
            else:
                ZM = Rbo - self.H0
            R0, _ = circle_from_3_points(Z1, Z2, ZM)
            ZH = Rbo
        else:
            if self.is_outwards():
                ZM = (Z1 + Z2) / 2 + self.H0
            else:
                ZM = (Z1 + Z2) / 2 - self.H0
            ZH = (Z1 + Z2) / 2
            R0 = None

        point_dict = dict()
        # symetry
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["ZM"] = ZM
        point_dict["ZH"] = ZH  # For H0 schematics
        # Store R0 for _comp_R0
        if R0 is not None:
            point_dict["R0"] = R0
        return point_dict

    # cf Methods.Slot.SlotCirc._comp_R0
    def _comp_R0(self):
        """Compute the radius of the circle

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        R0 : float
            Radius of the circle [m]
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value

        if self.is_H0_bore:
            return self._comp_point_coordinate()["R0"]
        else:
            # R0 is the radius of the circle
            # Pythagore in Triangle: Center, Z2, middle(Z1,Z2)
            # R0**2 = (W0/2)**2 + (H0-R0)**2

            return ((self.W0 / 2) ** 2 + self.H0**2) / (2 * self.H0)

    # cf Methods.Slot.SlotCirc.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        curve_list: list
            A list of one Arc
        """

        line_dict = self._comp_line_dict()

        curve_list = [
            line_dict["1-M"],
            line_dict["M-2"],
        ]
        return [line for line in curve_list if line is not None]

    # cf Methods.Slot.SlotCirc.check
    def check(self):
        """Check that the SlotCirc object is correct

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        None
        """
        pass

    # cf Methods.Slot.SlotCirc.comp_angle_opening
    def comp_angle_opening(self):
        """Compute the average opening angle of the Slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        alpha: float
            Average opening angle of the slot [rad]
        """

        Rbo = self.get_Rbo()

        return float(2 * np.arcsin(self.W0 / (2 * Rbo)))

    # cf Methods.Slot.SlotCirc.comp_height
    def comp_height(self):
        """Compute the height of the Slot.
        Caution, the top of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Htot: float
            Height of the slot [m]
        """

        return self.comp_height_active()

    # cf Methods.Slot.SlotCirc.comp_height_active
    def comp_height_active(self):
        """Compute the height of the winding area

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Hwind: float
            Height of the winding area [m]
        """

        if self.is_H0_bore is None:
            self.is_H0_bore = True  # Set default value

        if self.is_H0_bore:
            return self.H0
        else:
            point_dict = self._comp_point_coordinate()
            ZM = point_dict["ZM"]
            Rbo = self.get_Rbo()
            return abs(Rbo - abs(ZM))

    # cf Methods.Slot.SlotCirc.comp_surface
    def comp_surface(self):
        """Compute the Slot total surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        S: float
            Slot total surface [m**2]

        """

        return self.comp_surface_active()

    # cf Methods.Slot.SlotCirc.comp_surface_active
    def comp_surface_active(self):
        """Compute the Slot inner surface for winding (by analytical computation)

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        Swind: float
            Slot inner surface for winding [m**2]
        """

        R0 = self._comp_R0()
        alpha = float(2 * np.arcsin(self.W0 / (2 * R0)))
        # Area of the full circle
        S1 = np.pi * (R0**2)
        # Area of the top Arc
        S2 = (R0**2.0) / 2.0 * (alpha - np.sin(alpha))
        # Arc of the bore
        alpha_op = self.comp_angle_opening()
        S3 = (self.get_Rbo() ** 2.0) / 2.0 * (alpha_op - np.sin(alpha_op))

        if self.H0 < self.W0 / 2:
            # Center is in airgap
            if self.is_outwards():
                return S2 - S3
            else:
                return S2 + S3
        else:  # Center is in the Lamination
            if self.is_outwards():
                return S1 - S2 - S3
            else:
                return S1 - S2 + S3

    # cf Methods.Slot.SlotCirc.comp_surface_opening
    def comp_surface_opening(self):
        """Compute the Slot opening surface (by analytical computation).
        Caution, the bottom of the Slot is an Arc

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object

        Returns
        -------
        S: float
            Slot opening surface [m**2]

        """

        return 0

    # cf Methods.Slot.SlotCirc.convert_to_H0_bore
    def convert_to_H0_bore(self):
        """Convert the slot to the other definition of H0

        Parameters:
        -----------
        self : SlotCirc
            A SlotCirc objec with is_H0_bore==False
        """

        if self.is_H0_bore:
            raise Exception("Error, slot is already H0 bore type!")

        self.H0 = self.comp_height()
        self.is_H0_bore = True

    # cf Methods.Slot.SlotCirc.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full active surface

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Active Area
        """

        # Create curve list
        line_dict = self._comp_line_dict()
        curve_list = [
            line_dict["1-M"],
            line_dict["M-2"],
            line_dict["2-1"],
        ]
        curve_list = [line for line in curve_list if line is not None]

        # Only the closing arc (2-1) needs to be drawn (in FEMM)
        for curve in curve_list[:-1]:
            if curve.prop_dict is None:
                curve.prop_dict = dict()
            curve.prop_dict.update({DRAW_PROP_LAB: False})

        # Create surface
        ZM = line_dict["M-2"].get_begin()
        Zmid = (self.get_Rbo() + ZM) / 2
        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotCirc.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # No opening surface in SlotCirc
        return []

    # cf Methods.Slot.SlotCirc.plot_schematics
    def plot_schematics(
        self,
        is_default=False,
        is_return_default=False,
        is_enforce_default_H0_bore=None,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=0,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : SlotCirc
            A SlotCirc object
        is_default : int
            0: current slot values, 1: default internal rotor schematics, 2: default external stator schematics
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_enforce_default_H0_bore : bool
            To enforce is_H0_bore on default slot (is_default=True only), None use default value
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
            slot = type(self)(Zs=8, H0=10e-3, W0=45e-3, is_H0_bore=True)
            if is_enforce_default_H0_bore is not None:
                slot.is_H0_bore = is_enforce_default_H0_bore
            if is_default == 1:  # Internal rotor schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=True, is_stator=False, slot=slot
                )
                if is_return_default:
                    return lam
            else:  # External stator schematics
                lam = LamSlot(
                    Rint=0.1, Rext=0.135, is_internal=False, is_stator=True, slot=slot
                )
                if is_return_default:
                    return lam
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
                line = Segment(point_dict["Z1"], point_dict["Z2"])
                if self.is_outwards():
                    offset_label = -1 * self.H0 * 0.9 + 1j * 0.3 * self.W0
                else:
                    offset_label = self.H0 * 0.3 + 1j * 0.3 * self.W0
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=offset_label,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # H0
                line = Segment(point_dict["ZH"], point_dict["ZM"])
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="H0",
                    offset_label=1j * -0.15 * self.W0,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                # Top arc
                line = Arc1(
                    begin=point_dict["Z1"],
                    end=point_dict["Z2"],
                    radius=self.get_Rbo(),
                    is_trigo_direction=True,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # Zooming and cleaning
            W = self.W0 / 2 * 1.4
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
        W0=0.01,
        H0=0.03,
        is_H0_bore=True,
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
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "is_H0_bore" in list(init_dict.keys()):
                is_H0_bore = init_dict["is_H0_bore"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.H0 = H0
        self.is_H0_bore = is_H0_bore
        # Call Slot init
        super(SlotCirc, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotCirc_str = ""
        # Get the properties inherited from Slot
        SlotCirc_str += super(SlotCirc, self).__str__()
        SlotCirc_str += "W0 = " + str(self.W0) + linesep
        SlotCirc_str += "H0 = " + str(self.H0) + linesep
        SlotCirc_str += "is_H0_bore = " + str(self.is_H0_bore) + linesep
        return SlotCirc_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotCirc, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.H0 != self.H0:
            return False
        if other.is_H0_bore != self.is_H0_bore:
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
            super(SlotCirc, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
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
        if other._is_H0_bore != self._is_H0_bore:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_H0_bore)
                    + ", other="
                    + str(other._is_H0_bore)
                    + ")"
                )
                diff_list.append(name + ".is_H0_bore" + val_str)
            else:
                diff_list.append(name + ".is_H0_bore")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotCirc, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.H0)
        S += getsizeof(self.is_H0_bore)
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
        SlotCirc_dict = super(SlotCirc, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        SlotCirc_dict["W0"] = self.W0
        SlotCirc_dict["H0"] = self.H0
        SlotCirc_dict["is_H0_bore"] = self.is_H0_bore
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotCirc_dict["__class__"] = "SlotCirc"
        return SlotCirc_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        H0_val = self.H0
        is_H0_bore_val = self.is_H0_bore
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            H0=H0_val,
            is_H0_bore=is_H0_bore_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.H0 = None
        self.is_H0_bore = None
        # Set to None the properties inherited from Slot
        super(SlotCirc, self)._set_None()

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Slot isthmus width.

        :Type: float
        :min: 0
        """,
    )

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
        doc="""Slot height

        :Type: float
        :min: 0
        """,
    )

    def _get_is_H0_bore(self):
        """getter of is_H0_bore"""
        return self._is_H0_bore

    def _set_is_H0_bore(self, value):
        """setter of is_H0_bore"""
        check_var("is_H0_bore", value, "bool")
        self._is_H0_bore = value

    is_H0_bore = property(
        fget=_get_is_H0_bore,
        fset=_set_is_H0_bore,
        doc="""True to define H0 from top of arc to bore radius, False top arc to middle of W0 segment

        :Type: bool
        """,
    )
