# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/Hole.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/Hole
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - plot: import name 'ParentMissingError' refers to different sources (..Methods.ParentMissingError and ..Methods.Slot.Hole.plot.ParentMissingError)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from ._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.Hole.plot import plot
from numpy import pi, abs as np_abs
from ..Functions.Load.import_class import import_class
from ..Methods import ParentMissingError
from ..Methods.Slot.Hole import MagnetIndexError
from ..Functions.labels import HOLEV_LAB, VENT_LAB

from numpy import isnan
from ._check import InitUnKnowClassError


class Hole(FrozenClass):
    """Holes for lamination (abstract)"""

    VERSION = 1

    # cf Methods.Slot.Hole.comp_height
    def comp_height(self):
        """Compute the height of the Hole (Rmax-Rmin)

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        H : float
            Height of the hole

        """

        (Rmin, Rmax) = self.comp_radius()
        return Rmax - Rmin

    # cf Methods.Slot.Hole.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : Hole
            a Hole object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        if self.magnetization_dict_offset is not None:
            mag_dict = self.magnetization_dict_offset.copy()
            if not is_north:
                for key in mag_dict.keys():
                    mag_dict[key] += pi
            return mag_dict
        else:
            return dict()

    # cf Methods.Slot.Hole.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the hole

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the hole

        """

        surf_list = self.build_geometry()
        point_list = list()
        for surf in surf_list:
            for curve in surf.get_lines():
                point_list.extend(curve.discretize())

        abs_list = [np_abs(point) for point in point_list]
        Rmax = max(abs_list)
        Rmin = min(abs_list)
        return (Rmin, Rmax)

    # cf Methods.Slot.Hole.comp_surface
    def comp_surface(self):
        """Compute the Hole total surface (by numerical computation).

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        S : float
            Slot total surface [m**2]

        """

        surf_list = self.build_geometry()
        S = 0
        for surf in surf_list:
            S += surf.comp_surface()

        return S

    # cf Methods.Slot.Hole.convert_to_UD
    def convert_to_UD(self):
        """Convert the hole to HoleUD"""
        HoleUD = import_class("pyleecan.Classes", "HoleUD")
        surf_list = self.build_geometry()
        magnet_dict = self.get_magnet_dict()
        magnetization_dict = self.comp_magnetization_dict()

        return HoleUD(
            surf_list=surf_list,
            magnet_dict=magnet_dict,
            Zh=self.Zh,
            mat_void=self.mat_void,
            magnetization_dict_offset=magnetization_dict,
        )

    # cf Methods.Slot.Hole.get_is_stator
    def get_is_stator(self):
        """Return True if the parent lamination is stator and False if is a rotor

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        is_stator: bool
            True if the Lamination is a stator and False if not
        """

        if self.parent is not None:
            return self.parent.is_stator
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # cf Methods.Slot.Hole.get_magnet_by_id
    def get_magnet_by_id(self, index):
        """Return the magnet at the corresponding index
        returns None is the magnet is None
        Raise error if the hole doesn't have a magnet for the corresponding index

        Parameters
        ----------
        self : Hole
            A Hole object
        index : int
            Index of the magnet to return
        Returns
        -------
        magnet : Magnet
            Magnet object (or None)
        """

        label = "magnet_" + str(index)
        if hasattr(self, label):
            return getattr(self, label)
        elif hasattr(self, "magnet_dict") and label in self.magnet_dict:
            return self.magnet_dict[label]
        else:
            raise MagnetIndexError(
                "Hole of type " + str(type(self)) + " has no magnet " + label
            )

    # cf Methods.Slot.Hole.get_magnet_dict
    def get_magnet_dict(self):
        """Return a dictionary with all the magnets of the Hole

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        magnet_dict : {Magnet}
            Dictionary of magnet (key = magnet_X, value= Magnet or None)
        """

        if hasattr(self, "magnet_dict"):
            return self.magnet_dict
        else:
            ii = 0
            magnet_dict = dict()
            while hasattr(self, "magnet_" + str(ii)):
                magnet_dict["magnet_" + str(ii)] = getattr(self, "magnet_" + str(ii))
                ii += 1
            return magnet_dict

    # cf Methods.Slot.Hole.get_R_id
    def get_R_id(self):
        """Return the "Radial" index for label (index in lam.hole or lam.axial_vent)

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        R_id : int
            "Radial" index of the hole in the lamination
        surf_type : str
            Label to use for the surface type (HoleV or Vent)
        """

        if self.parent is None:  # Compatibility For plotting
            return (0, HOLEV_LAB)
        elif (
            hasattr(self.parent, "get_hole_list")
            and self in self.parent.get_hole_list()
        ):
            return (self.parent.get_hole_list().index(self), HOLEV_LAB)
        elif self.parent.axial_vent is not None and self in self.parent.axial_vent:
            return (self.parent.axial_vent.index(self), VENT_LAB)
        else:
            raise Exception("Error, impossible to get Hole R-id")

    # cf Methods.Slot.Hole.get_Rbo
    def get_Rbo(self):
        """Return the parent lamination bore radius

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # cf Methods.Slot.Hole.get_Rext
    def get_Rext(self):
        """Return the parent lamination exterior radius

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        Rext: float
            The parent lamination exterior radius [m]

        """

        if self.parent is not None:
            return self.parent.Rext
        else:
            raise ParentMissingError("Error: The hole is not inside a Lamination")

    # cf Methods.Slot.Hole.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : Hole
            A Hole object

        Returns
        -------
        has_magnet : bool
            False

        """

        return False

    # cf Methods.Slot.Hole.plot
    plot = plot

    # cf Methods.Slot.Hole.set_magnet_by_id
    def set_magnet_by_id(self, index, magnet):
        """Set the magnet at the corresponding index
        Raise error if the hole doesn't have a magnet for the corresponding index

        Parameters
        ----------
        self : Hole
            A Hole object
        index : int
            Index of the magnet to return
        magnet : Magnet
            Magnet object to set (or None)
        """

        label = "magnet_" + str(index)
        if hasattr(self, label):
            setattr(self, label, magnet)
        elif hasattr(self, "magnet_dict") and label in self.magnet_dict:
            self.magnet_dict[label] = magnet
        else:
            raise MagnetIndexError(
                "Hole of type " + str(type(self)) + " has no magnet " + label
            )

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
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
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.Zh = Zh
        self.mat_void = mat_void
        self.magnetization_dict_offset = magnetization_dict_offset
        self.Alpha0 = Alpha0

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Hole_str = ""
        if self.parent is None:
            Hole_str += "parent = None " + linesep
        else:
            Hole_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Hole_str += "Zh = " + str(self.Zh) + linesep
        if self.mat_void is not None:
            tmp = self.mat_void.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Hole_str += "mat_void = " + tmp
        else:
            Hole_str += "mat_void = None" + linesep + linesep
        Hole_str += (
            "magnetization_dict_offset = "
            + str(self.magnetization_dict_offset)
            + linesep
        )
        Hole_str += "Alpha0 = " + str(self.Alpha0) + linesep
        return Hole_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.Zh != self.Zh:
            return False
        if other.mat_void != self.mat_void:
            return False
        if other.magnetization_dict_offset != self.magnetization_dict_offset:
            return False
        if other.Alpha0 != self.Alpha0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._Zh != self._Zh:
            if is_add_value:
                val_str = " (self=" + str(self._Zh) + ", other=" + str(other._Zh) + ")"
                diff_list.append(name + ".Zh" + val_str)
            else:
                diff_list.append(name + ".Zh")
        if (other.mat_void is None and self.mat_void is not None) or (
            other.mat_void is not None and self.mat_void is None
        ):
            diff_list.append(name + ".mat_void None mismatch")
        elif self.mat_void is not None:
            diff_list.extend(
                self.mat_void.compare(
                    other.mat_void,
                    name=name + ".mat_void",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._magnetization_dict_offset != self._magnetization_dict_offset:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._magnetization_dict_offset)
                    + ", other="
                    + str(other._magnetization_dict_offset)
                    + ")"
                )
                diff_list.append(name + ".magnetization_dict_offset" + val_str)
            else:
                diff_list.append(name + ".magnetization_dict_offset")
        if (
            other._Alpha0 is not None
            and self._Alpha0 is not None
            and isnan(other._Alpha0)
            and isnan(self._Alpha0)
        ):
            pass
        elif other._Alpha0 != self._Alpha0:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Alpha0)
                    + ", other="
                    + str(other._Alpha0)
                    + ")"
                )
                diff_list.append(name + ".Alpha0" + val_str)
            else:
                diff_list.append(name + ".Alpha0")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.Zh)
        S += getsizeof(self.mat_void)
        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.Alpha0)
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

        Hole_dict = dict()
        Hole_dict["Zh"] = self.Zh
        if self.mat_void is None:
            Hole_dict["mat_void"] = None
        else:
            Hole_dict["mat_void"] = self.mat_void.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Hole_dict["magnetization_dict_offset"] = (
            self.magnetization_dict_offset.copy()
            if self.magnetization_dict_offset is not None
            else None
        )
        Hole_dict["Alpha0"] = self.Alpha0
        # The class name is added to the dict for deserialisation purpose
        Hole_dict["__class__"] = "Hole"
        return Hole_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.Zh = None
        if self.mat_void is not None:
            self.mat_void._set_None()
        self.magnetization_dict_offset = None
        self.Alpha0 = None

    def _get_Zh(self):
        """getter of Zh"""
        return self._Zh

    def _set_Zh(self, value):
        """setter of Zh"""
        check_var("Zh", value, "int", Vmin=0)
        self._Zh = value

    Zh = property(
        fget=_get_Zh,
        fset=_set_Zh,
        doc="""Number of Hole around the circumference

        :Type: int
        :min: 0
        """,
    )

    def _get_mat_void(self):
        """getter of mat_void"""
        return self._mat_void

    def _set_mat_void(self, value):
        """setter of mat_void"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "mat_void"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "mat_void")
            value = Material()
        check_var("mat_void", value, "Material")
        self._mat_void = value

        if self._mat_void is not None:
            self._mat_void.parent = self

    mat_void = property(
        fget=_get_mat_void,
        fset=_set_mat_void,
        doc="""Material of the void part of the hole (Air in general)

        :Type: Material
        """,
    )

    def _get_magnetization_dict_offset(self):
        """getter of magnetization_dict_offset"""
        return self._magnetization_dict_offset

    def _set_magnetization_dict_offset(self, value):
        """setter of magnetization_dict_offset"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("magnetization_dict_offset", value, "dict")
        self._magnetization_dict_offset = value

    magnetization_dict_offset = property(
        fget=_get_magnetization_dict_offset,
        fset=_set_magnetization_dict_offset,
        doc="""Dictionary add an offset to the magnetization direction of the magnets (key=magnet_X, value=angle[rad])

        :Type: dict
        """,
    )

    def _get_Alpha0(self):
        """getter of Alpha0"""
        return self._Alpha0

    def _set_Alpha0(self, value):
        """setter of Alpha0"""
        check_var("Alpha0", value, "float", Vmin=0, Vmax=6.29)
        self._Alpha0 = value

    Alpha0 = property(
        fget=_get_Alpha0,
        fset=_set_Alpha0,
        doc="""Shift angle of the holes around circumference

        :Type: float
        :min: 0
        :max: 6.29
        """,
    )
