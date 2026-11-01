# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/LamSlot.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSlot
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
from pyleecan.Classes.Lamination import Lamination

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.LamSlot import LSC_SlotTooLong
import numpy as np
from pyleecan.Classes.Lamination import Lamination
from pyleecan.Functions.labels import update_RTS_index
from matplotlib.patches import Patch
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)


from pyleecan.Classes._check import InitUnKnowClassError


class LamSlot(Lamination):
    """Lamination with empty Slot"""

    VERSION = 1

    # cf Methods.Machine.LamSlot.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        None

        Raises
        _______
        LSC_SlotTooLong
            The Slot is too long for the lamination (HYoke <0)

        LSC_OverlappingSlot
            The Lamination has overlapping slot

        """

        super(type(self), self).check()

        self.slot.check()

        if self.comp_height_yoke() < 0:
            raise LSC_SlotTooLong(
                "The Slot is too long for the lamination " "(HYoke <0)"
            )

        """
        Wt = self.slot.comp_tooth_widths()["WTooth_min"]

        if Wt < 0:
            raise LSC_OverlappingSlot("The Lamination has overlapping slot")
        """

    # cf Methods.Machine.LamSlot.comp_angle_d_axis
    def comp_angle_d_axis(self):
        """Compute the angle between the X axis and the first d+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        return 0

    # cf Methods.Machine.LamSlot.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        if self.slot is not None and self.slot.Zs > 0:
            return self.Rext - self.Rint - self.slot.comp_height()
        else:
            return self.Rext - self.Rint

    # cf Methods.Machine.LamSlot.comp_radius_mec
    def comp_radius_mec(self):
        """Compute the mechanical radius of the Lamination [m]

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        Rmec: float
            Mechanical radius [m]
        """

        Rmec = self.get_Rbo()
        if self.slot.is_airgap_active():
            # Part of the active surface is in the airgap
            # => Reduce mechanical airgap
            (Rmin, Rmax) = self.slot.comp_radius()
            if self.is_internal:  # inward Slot
                # Top radius of the magnet
                Rmec = max(Rmec, Rmax)
            else:
                Rmec = min(Rmec, Rmin)

        # Handles key in the airgap
        if self.notch is not None:
            for notch in self.notch:
                if notch.has_key():
                    (Rmin, Rmax) = notch.notch_shape.comp_radius()
                    if self.is_internal:  # inward Slot
                        Rmec = max(Rmec, Rmax)
                    else:
                        Rmec = min(Rmec, Rmin)
        return Rmec

    # cf Methods.Machine.LamSlot.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Lamination, Ventilation, Slot).

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot, Syoke, Steeth) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)
        if self.slot is None:
            Sslot = 0
        else:
            Sslot = self.get_Zs() * self.slot.comp_surface()

        Ryoke = self.get_Ryoke()
        Hyoke = self.comp_height_yoke()
        if self.is_internal:
            S_dict["Syoke"] = (
                np.pi * ((Ryoke + Hyoke) ** 2 - Ryoke**2) - S_dict["Svent"]
            )
        else:
            S_dict["Syoke"] = (
                np.pi * (Ryoke**2 - (Ryoke - Hyoke) ** 2) - S_dict["Svent"]
            )

        S_dict["Sslot"] = Sslot
        S_dict["Slam"] -= Sslot
        S_dict["Steeth"] = S_dict["Slam"] - S_dict["Syoke"]
        return S_dict

    # cf Methods.Machine.LamSlot.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.slot.Zs // 2

    # cf Methods.Machine.LamSlot.get_slot_desc_list
    def get_slot_desc_list(self, sym=1, is_bore=True):
        """Returns an ordered description of the slot

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        sym: int
            Number of symmetry
        is_bore : bool
            True generate desc of bore, else yoke

        Returns
        -------
        slot_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot / None for Radius
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        if self.slot.is_bore != is_bore:
            return list()

        slot_list = list()
        op = self.slot.comp_angle_opening()
        Zs = self.slot.Zs

        for ii in range(Zs // sym):
            slot_dict = dict()
            slot_dict["begin_angle"] = 2 * np.pi / Zs * ii - op / 2 + np.pi / Zs
            slot_dict["end_angle"] = 2 * np.pi / Zs * ii + op / 2 + np.pi / Zs
            slot_dict["obj"] = self.slot
            slot_dict["lines"] = self.slot.build_geometry()
            # Apply rotation
            for line in slot_dict["lines"]:
                line.rotate((slot_dict["begin_angle"] + slot_dict["end_angle"]) / 2)
            slot_dict["label"] = "slot"
            slot_list.append(slot_dict)

        return slot_list

    # cf Methods.Machine.LamSlot.get_surfaces_closing
    def get_surfaces_closing(self, sym=1):
        """Return the surfaces needed to close the radii of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        surf_list : list
            List of the closing surfaces
        """

        # Get notches closing surfaces
        close_list = Lamination.get_surfaces_closing(self=self, sym=sym)
        if not hasattr(self.slot, "get_surface_opening"):
            return close_list
        else:  # Get slot closing surfaces (no surface if wedges)
            slot_pitch = 2 * np.pi / self.slot.Zs
            # for slot to draw
            for ii in range(self.slot.Zs // sym):
                slot_surf = self.slot.get_surface_opening(
                    alpha=slot_pitch * ii + slot_pitch * 0.5
                )
                for jj, surf in enumerate(slot_surf):
                    # Adapt the label
                    surf.label = update_RTS_index(
                        label=surf.label, R_id=None, T_id=jj, S_id=ii
                    )
                    close_list.append(surf)

            return close_list

    # cf Methods.Machine.LamSlot.get_Zs
    def get_Zs(self):
        """Return the number of Slot of the Lamination

        Parameters
        ----------
        self : LamSlot
            a LamSlot object

        Returns
        -------
        Zs : float
            Number of Slot
        """

        if self.slot is None:
            return 0
        else:
            return self.slot.Zs

    # cf Methods.Machine.LamSlot.has_magnet
    def has_magnet(self):
        """Return if LamSlot has magnets

        Parameters
        ----------
        self : LamSlot
            A LamSlot object

        Returns
        -------
        has_magnet : bool
            True if LamSlot has magnets
        """

        return (
            hasattr(self, "magnet")
            or hasattr(self, "magnet_north")
            or hasattr(self, "magnet_south")
        )

    # cf Methods.Machine.LamSlot.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        if self.slot is None:
            return False
        if self.slot.is_bore is None:
            self.slot.is_bore = True  # Default value
        return self.slot.Zs != 0 and self.slot.is_bore == is_bore

    # cf Methods.Machine.LamSlot.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_lam_only=False,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        is_display=True,
        is_show_fig=True,
        is_winding_connection=False,
    ):
        """Plot the Lamination with empty Slots in a matplotlib fig

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (No effect for LamSlot)
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

        Returns
        -------
        patches : list
            List of Patches

        or

        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = list()
        for surf in surf_list:
            color, legend = get_color_legend_from_surface(surf, is_lam_only)

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
            ax.set_xlabel("(m)")
            ax.set_ylabel("(m)")
            for patch in patches:
                ax.add_patch(patch)

            # Axis Setup
            ax.axis("equal")

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.5
            ax.set_xlim(-Lim, Lim)
            ax.set_ylim(-Lim, Lim)

            # Add the legend
            if not is_edge_only:
                if self.is_stator and "Stator" not in label_leg:
                    ax.set_title("Stator with empty slot")
                elif not self.is_stator and "Rotor" not in label_leg:
                    ax.set_title("Rotor with empty slot")

                ax.legend(patch_leg, label_leg)
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # cf Methods.Machine.LamSlot.set_pole_pair_number
    def set_pole_pair_number(self, p):
        """Set the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlot
            A LamSlot object
        p: int
            Number of pair of pole

        """

        self.slot.Zs = 2 * p

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        slot=-1,
        L1=0.35,
        mat_type=-1,
        Nrvd=0,
        Wrvd=0,
        Kf1=0.95,
        is_internal=True,
        Rint=0,
        Rext=1,
        is_stator=True,
        axial_vent=-1,
        notch=-1,
        skew=None,
        bore=None,
        yoke=None,
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
            if "slot" in list(init_dict.keys()):
                slot = init_dict["slot"]
            if "L1" in list(init_dict.keys()):
                L1 = init_dict["L1"]
            if "mat_type" in list(init_dict.keys()):
                mat_type = init_dict["mat_type"]
            if "Nrvd" in list(init_dict.keys()):
                Nrvd = init_dict["Nrvd"]
            if "Wrvd" in list(init_dict.keys()):
                Wrvd = init_dict["Wrvd"]
            if "Kf1" in list(init_dict.keys()):
                Kf1 = init_dict["Kf1"]
            if "is_internal" in list(init_dict.keys()):
                is_internal = init_dict["is_internal"]
            if "Rint" in list(init_dict.keys()):
                Rint = init_dict["Rint"]
            if "Rext" in list(init_dict.keys()):
                Rext = init_dict["Rext"]
            if "is_stator" in list(init_dict.keys()):
                is_stator = init_dict["is_stator"]
            if "axial_vent" in list(init_dict.keys()):
                axial_vent = init_dict["axial_vent"]
            if "notch" in list(init_dict.keys()):
                notch = init_dict["notch"]
            if "skew" in list(init_dict.keys()):
                skew = init_dict["skew"]
            if "bore" in list(init_dict.keys()):
                bore = init_dict["bore"]
            if "yoke" in list(init_dict.keys()):
                yoke = init_dict["yoke"]
        # Set the properties (value check and convertion are done in setter)
        self.slot = slot
        # Call Lamination init
        super(LamSlot, self).__init__(
            L1=L1,
            mat_type=mat_type,
            Nrvd=Nrvd,
            Wrvd=Wrvd,
            Kf1=Kf1,
            is_internal=is_internal,
            Rint=Rint,
            Rext=Rext,
            is_stator=is_stator,
            axial_vent=axial_vent,
            notch=notch,
            skew=skew,
            bore=bore,
            yoke=yoke,
        )
        # The class is frozen (in Lamination init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        LamSlot_str = ""
        # Get the properties inherited from Lamination
        LamSlot_str += super(LamSlot, self).__str__()
        if self.slot is not None:
            tmp = self.slot.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            LamSlot_str += "slot = " + tmp
        else:
            LamSlot_str += "slot = None" + linesep + linesep
        return LamSlot_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Lamination
        if not super(LamSlot, self).__eq__(other):
            return False
        if other.slot != self.slot:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Lamination
        diff_list.extend(
            super(LamSlot, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.slot is None and self.slot is not None) or (
            other.slot is not None and self.slot is None
        ):
            diff_list.append(name + ".slot None mismatch")
        elif self.slot is not None:
            diff_list.extend(
                self.slot.compare(
                    other.slot,
                    name=name + ".slot",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Lamination
        S += super(LamSlot, self).__sizeof__()
        S += getsizeof(self.slot)
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

        # Get the properties inherited from Lamination
        LamSlot_dict = super(LamSlot, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.slot is None:
            LamSlot_dict["slot"] = None
        else:
            LamSlot_dict["slot"] = self.slot.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSlot_dict["__class__"] = "LamSlot"
        return LamSlot_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.slot is None:
            slot_val = None
        else:
            slot_val = self.slot.copy()
        L1_val = self.L1
        if self.mat_type is None:
            mat_type_val = None
        else:
            mat_type_val = self.mat_type.copy()
        Nrvd_val = self.Nrvd
        Wrvd_val = self.Wrvd
        Kf1_val = self.Kf1
        is_internal_val = self.is_internal
        Rint_val = self.Rint
        Rext_val = self.Rext
        is_stator_val = self.is_stator
        if self.axial_vent is None:
            axial_vent_val = None
        else:
            axial_vent_val = list()
            for obj in self.axial_vent:
                axial_vent_val.append(obj.copy())
        if self.notch is None:
            notch_val = None
        else:
            notch_val = list()
            for obj in self.notch:
                notch_val.append(obj.copy())
        if self.skew is None:
            skew_val = None
        else:
            skew_val = self.skew.copy()
        if self.bore is None:
            bore_val = None
        else:
            bore_val = self.bore.copy()
        if self.yoke is None:
            yoke_val = None
        else:
            yoke_val = self.yoke.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            slot=slot_val,
            L1=L1_val,
            mat_type=mat_type_val,
            Nrvd=Nrvd_val,
            Wrvd=Wrvd_val,
            Kf1=Kf1_val,
            is_internal=is_internal_val,
            Rint=Rint_val,
            Rext=Rext_val,
            is_stator=is_stator_val,
            axial_vent=axial_vent_val,
            notch=notch_val,
            skew=skew_val,
            bore=bore_val,
            yoke=yoke_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.slot is not None:
            self.slot._set_None()
        # Set to None the properties inherited from Lamination
        super(LamSlot, self)._set_None()

    def _get_slot(self):
        """getter of slot"""
        return self._slot

    def _set_slot(self, value):
        """setter of slot"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "slot")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Slot = import_class("pyleecan.Classes", "Slot", "slot")
            value = Slot()
        check_var("slot", value, "Slot")
        self._slot = value

        if self._slot is not None:
            self._slot.parent = self

    slot = property(
        fget=_get_slot,
        fset=_set_slot,
        doc="""lamination Slot

        :Type: Slot
        """,
    )
