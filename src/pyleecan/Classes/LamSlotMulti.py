# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/LamSlotMulti.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/LamSlotMulti
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import set_array, check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Lamination import Lamination

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Machine.LamSlotMulti import LamSlotMultiAlphaError
import numpy as np
from pyleecan.Classes.Lamination import Lamination
from matplotlib.patches import Patch
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.Plot.get_color_legend_from_surface import (
    get_color_legend_from_surface,
)


from pyleecan.Classes._check import InitUnKnowClassError


class LamSlotMulti(Lamination):
    """Lamination with list of Slot"""

    VERSION = 1

    # cf Methods.Machine.LamSlotMulti.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        None
        """

        super(type(self), self).check()

        # Check all the slots
        for slot in self.slot_list:
            slot.check()

        #
        if len(self.alpha.shape) > 1:
            raise LamSlotMultiAlphaError("Alpha should have be a vector (1D array)")
        if len(self.alpha) != len(self.slot_list):
            raise LamSlotMultiAlphaError(
                "Alpha should have the same length as slot_list"
            )
        if self.alpha[0] < 0:
            raise LamSlotMultiAlphaError(
                "Alpha should be an ordered array with values between 0 and 2*pi"
            )
        for ii in range(len(self.alpha) - 1):
            if self.alpha[ii] > self.alpha[ii + 1]:
                raise LamSlotMultiAlphaError(
                    "Alpha should be an ordered array with values between 0 and 2*pi"
                )
        if self.alpha[-1] > 2 * np.pi:
            raise LamSlotMultiAlphaError(
                "Alpha should be an ordered array with values between 0 and 2*pi"
            )

    # cf Methods.Machine.LamSlotMulti.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        H = 0
        for slot in self.slot_list:
            H = max(H, slot.comp_height())
        return self.Rext - self.Rint - H

    # cf Methods.Machine.LamSlotMulti.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if self.sym_dict_enforced is not None:
            self.get_logger().debug("Enforcing symmetry for LamSlotMulti")
            return (
                self.sym_dict_enforced["per_a"],
                self.sym_dict_enforced["is_antiper_a"],
            )
        else:
            # Zs = self.get_Zs()
            is_aper = False
            # TODO compute it
            self.get_logger().debug("Symmetry not available yet for LamSlotMulti")
            return 1, is_aper

    # cf Methods.Machine.LamSlotMulti.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surfaces (Lamination, Ventilation, Slot).

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Sslot) [m**2]

        """

        S_dict = Lamination.comp_surfaces(self)
        Sslot = 0
        for slot in self.slot_list:
            Sslot += slot.comp_surface()

        S_dict["Sslot"] = Sslot
        S_dict["Slam"] -= Sslot
        return S_dict

    # cf Methods.Machine.LamSlotMulti.get_pole_pair_number
    def get_pole_pair_number(self):
        """Return the number of pair of pole of the Lamination

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object

        Returns
        -------
        p: int
            Number of pair of pole

        """

        return self.get_Zs() // 2

    # cf Methods.Machine.LamSlotMulti.get_slot_desc_list
    def get_slot_desc_list(self, sym=1, is_bore=True):
        """Returns an ordered description of the slot

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
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

        slot_list = list()
        for ii in range(len(self.slot_list) // sym):
            if self.slot_list[ii].is_bore == is_bore:
                slot = self.slot_list[ii]
                op = slot.comp_angle_opening()
                lines = slot.build_geometry()
                # Apply rotation
                for line in lines:
                    line.rotate(self.alpha[ii])
                bore_dict = dict()
                bore_dict["begin_angle"] = self.alpha[ii] - op / 2
                bore_dict["end_angle"] = self.alpha[ii] + op / 2
                bore_dict["obj"] = slot
                bore_dict["lines"] = lines
                bore_dict["label"] = "Slot"
                slot_list.append(bore_dict)

        return slot_list

    # cf Methods.Machine.LamSlotMulti.get_Zs
    def get_Zs(self):
        """Return the number of Slot of the Lamination

        Parameters
        ----------
        self : LamSlotMulti
            a LamSlotMulti object

        Returns
        -------
        Zs : float
            Number of Slot

        """

        return len(self.slot_list)

    # cf Methods.Machine.LamSlotMulti.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : LamSlotMulti
            A LamSlotMulti object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        if self.slot_list is None or len(self.slot_list) == 0:
            return False

        # notch_shape.is_bore = None => Default is True
        if is_bore:
            return any([slot.is_bore in [None, True] for slot in self.slot_list])
        else:
            return any([slot.is_bore == False for slot in self.slot_list])

    # cf Methods.Machine.LamSlotMulti.plot
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
        is_clean_plot=False,
        is_winding_connection=False,
    ):
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
        is_clean_plot : bool
            True to remove title, legend, axis (only machine on plot with white background)
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
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
            (fig, ax, patch_leg, label_leg) = init_fig(fig)
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
                if self.is_stator:
                    ax.set_title("Stator with empty slot")
                else:
                    ax.set_title("Rotor with empty slot")

                ax.legend(patch_leg, label_leg)
            # Clean figure
            if is_clean_plot:
                ax.set_axis_off()
                ax.axis("equal")
                if ax.get_legend() is not None:
                    ax.get_legend().remove()
                ax.set_title("")
            if is_show_fig:
                fig.show()
            return fig, ax
        else:
            return patches

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        slot_list=-1,
        alpha=None,
        sym_dict_enforced=None,
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
            if "slot_list" in list(init_dict.keys()):
                slot_list = init_dict["slot_list"]
            if "alpha" in list(init_dict.keys()):
                alpha = init_dict["alpha"]
            if "sym_dict_enforced" in list(init_dict.keys()):
                sym_dict_enforced = init_dict["sym_dict_enforced"]
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
        self.slot_list = slot_list
        self.alpha = alpha
        self.sym_dict_enforced = sym_dict_enforced
        # Call Lamination init
        super(LamSlotMulti, self).__init__(
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

        LamSlotMulti_str = ""
        # Get the properties inherited from Lamination
        LamSlotMulti_str += super(LamSlotMulti, self).__str__()
        if len(self.slot_list) == 0:
            LamSlotMulti_str += "slot_list = []" + linesep
        for ii in range(len(self.slot_list)):
            tmp = (
                self.slot_list[ii].__str__().replace(linesep, linesep + "\t") + linesep
            )
            LamSlotMulti_str += "slot_list[" + str(ii) + "] =" + tmp + linesep + linesep
        LamSlotMulti_str += (
            "alpha = "
            + linesep
            + str(self.alpha).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        LamSlotMulti_str += (
            "sym_dict_enforced = " + str(self.sym_dict_enforced) + linesep
        )
        return LamSlotMulti_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Lamination
        if not super(LamSlotMulti, self).__eq__(other):
            return False
        if other.slot_list != self.slot_list:
            return False
        if not np.array_equal(other.alpha, self.alpha):
            return False
        if other.sym_dict_enforced != self.sym_dict_enforced:
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
            super(LamSlotMulti, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.slot_list is None and self.slot_list is not None) or (
            other.slot_list is not None and self.slot_list is None
        ):
            diff_list.append(name + ".slot_list None mismatch")
        elif self.slot_list is None:
            pass
        elif len(other.slot_list) != len(self.slot_list):
            diff_list.append("len(" + name + ".slot_list)")
        else:
            for ii in range(len(other.slot_list)):
                diff_list.extend(
                    self.slot_list[ii].compare(
                        other.slot_list[ii],
                        name=name + ".slot_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if not np.array_equal(other.alpha, self.alpha):
            diff_list.append(name + ".alpha")
        if other._sym_dict_enforced != self._sym_dict_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._sym_dict_enforced)
                    + ", other="
                    + str(other._sym_dict_enforced)
                    + ")"
                )
                diff_list.append(name + ".sym_dict_enforced" + val_str)
            else:
                diff_list.append(name + ".sym_dict_enforced")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Lamination
        S += super(LamSlotMulti, self).__sizeof__()
        if self.slot_list is not None:
            for value in self.slot_list:
                S += getsizeof(value)
        S += getsizeof(self.alpha)
        if self.sym_dict_enforced is not None:
            for key, value in self.sym_dict_enforced.items():
                S += getsizeof(value) + getsizeof(key)
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
        LamSlotMulti_dict = super(LamSlotMulti, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.slot_list is None:
            LamSlotMulti_dict["slot_list"] = None
        else:
            LamSlotMulti_dict["slot_list"] = list()
            for obj in self.slot_list:
                if obj is not None:
                    LamSlotMulti_dict["slot_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    LamSlotMulti_dict["slot_list"].append(None)
        if self.alpha is None:
            LamSlotMulti_dict["alpha"] = None
        else:
            if type_handle_ndarray == 0:
                LamSlotMulti_dict["alpha"] = self.alpha.tolist()
            elif type_handle_ndarray == 1:
                LamSlotMulti_dict["alpha"] = self.alpha.copy()
            elif type_handle_ndarray == 2:
                LamSlotMulti_dict["alpha"] = self.alpha
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        LamSlotMulti_dict["sym_dict_enforced"] = (
            self.sym_dict_enforced.copy()
            if self.sym_dict_enforced is not None
            else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        LamSlotMulti_dict["__class__"] = "LamSlotMulti"
        return LamSlotMulti_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.slot_list is None:
            slot_list_val = None
        else:
            slot_list_val = list()
            for obj in self.slot_list:
                slot_list_val.append(obj.copy())
        if self.alpha is None:
            alpha_val = None
        else:
            alpha_val = self.alpha.copy()
        if self.sym_dict_enforced is None:
            sym_dict_enforced_val = None
        else:
            sym_dict_enforced_val = self.sym_dict_enforced.copy()
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
            slot_list=slot_list_val,
            alpha=alpha_val,
            sym_dict_enforced=sym_dict_enforced_val,
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

        self.slot_list = None
        self.alpha = None
        self.sym_dict_enforced = None
        # Set to None the properties inherited from Lamination
        super(LamSlotMulti, self)._set_None()

    def _get_slot_list(self):
        """getter of slot_list"""
        if self._slot_list is not None:
            for obj in self._slot_list:
                if obj is not None:
                    obj.parent = self
        return self._slot_list

    def _set_slot_list(self, value):
        """setter of slot_list"""
        if type(value) is list:
            for ii, obj in enumerate(value):
                if isinstance(obj, str):  # Load from file
                    try:
                        obj = load_init_dict(obj)[1]
                    except Exception as e:
                        self.get_logger().error(
                            "Error while loading " + obj + ", setting None instead"
                        )
                        obj = None
                        value[ii] = None
                if type(obj) is dict:
                    class_obj = import_class(
                        "pyleecan.Classes", obj.get("__class__"), "slot_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("slot_list", value, "[Slot]")
        self._slot_list = value

    slot_list = property(
        fget=_get_slot_list,
        fset=_set_slot_list,
        doc="""List of lamination Slot

        :Type: [Slot]
        """,
    )

    def _get_alpha(self):
        """getter of alpha"""
        return self._alpha

    def _set_alpha(self, value):
        """setter of alpha"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("alpha", value, "ndarray")
        self._alpha = value

    alpha = property(
        fget=_get_alpha,
        fset=_set_alpha,
        doc="""Angular position of the Slots

        :Type: ndarray
        """,
    )

    def _get_sym_dict_enforced(self):
        """getter of sym_dict_enforced"""
        return self._sym_dict_enforced

    def _set_sym_dict_enforced(self, value):
        """setter of sym_dict_enforced"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("sym_dict_enforced", value, "dict")
        self._sym_dict_enforced = value

    sym_dict_enforced = property(
        fget=_get_sym_dict_enforced,
        fset=_set_sym_dict_enforced,
        doc="""Dictionary to enforce the lamination symmetry

        :Type: dict
        """,
    )
