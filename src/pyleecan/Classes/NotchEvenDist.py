# File generated according to Generator/ClassesRef/Machine/NotchEvenDist.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/NotchEvenDist"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes._check import check_var
from pyleecan.Classes.Notch import Notch
from pyleecan.Functions.Geometry.transform_hole_surf import transform_hole_surf
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import KEY_LAB, YSNL_LAB, YSNR_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save


class NotchEvenDist(Notch):
    """Class for evenly distributed notches (according to Zs)"""

    VERSION = 1

    # cf Methods.Machine.NotchEvenDist.build_geometry_key
    def build_geometry_key(self, index=0, sym=1, alpha=0, delta=0):
        """Build the geometry of the keys inside the notch

        Parameters
        ----------
        self : NotchEvenDist
            The NotchEvenDist to build the key surfaces from
        index : int
            Index of the Notch in the list
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation

        Returns
        -------
        surf_list : list
            list of surfaces needed to draw the keys

        """

        surf_list = list()

        # Get the original surface
        Nsurf = self.notch_shape.get_surface_active()
        Nsurf.label = self.get_label() + "_" + KEY_LAB + "_R" + str(index) + "-T0-S0"
        Nsurf.rotate(angle=self.alpha)
        # Label definition
        BC_prop_right = self.get_label() + "_" + YSNR_LAB
        BC_prop_left = self.get_label() + "_" + YSNL_LAB
        # Generate all the surfaces (handle cut on sym axis)
        surf_list.extend(
            transform_hole_surf(
                hole_surf_list=[Nsurf],
                Zh=self.notch_shape.Zs,
                sym=sym,
                alpha=0,
                delta=0,
                is_split=True,
                BC_prop_right=BC_prop_right,
                BC_prop_left=BC_prop_left,
            )
        )

        # apply the transformation
        for surf in surf_list:
            if alpha != 0:
                surf.rotate(alpha)
            if delta != 0:
                surf.translate(delta)

        return surf_list

    # cf Methods.Machine.NotchEvenDist.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the notch

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the notch
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.notch_shape.Zs, False

    # cf Methods.Machine.NotchEvenDist.comp_surface
    def comp_surface(self):
        """Compute the surface of ALL THE NOTCHES

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        Snotch : float
            surface of ALL THE NOTCHES
        """

        return self.notch_shape.Zs * self.notch_shape.comp_surface()

    # cf Methods.Machine.NotchEvenDist.get_key_Ox_radius
    def get_key_Ox_radius(self):
        """Return the Key max/min radius on Ox to close the sliding band in FEMM

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object

        Returns
        -------
        ROx : Float
            Radius to use to close  the sliding band [m] (None=no intersection)
        """

        # Get all surfaces
        surf_list = self.build_geometry_key(sym=1)

        # Cut to find a surface on Ox
        Z_list = list()
        for surf in surf_list:
            Z_list.extend(surf.intersect_line(0, 100))

        # No intersection => Return default radius
        if len(Z_list) == 0:
            return None

        # Get the min/max intersection on the right of Ox only
        Rright = [Z.real for Z in Z_list if Z.real > 0]
        if len(Rright) == 0:
            return None
        elif self.is_outwards():  # Outer lamination
            return min(Rright)
        else:
            return max(Rright)

    # cf Methods.Machine.NotchEvenDist.get_notch_desc_list
    def get_notch_desc_list(self, sym=1):
        """Returns an ordered description of the notches

        Parameters
        ----------
        self : NotchEvenDist
            A NotchEvenDist object
        sym: int
            Number of symmetry

        Returns
        -------
        notch_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot (for notch_shape) / None for Radius
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        notch_list = list()
        op = self.notch_shape.comp_angle_opening()
        Zs = self.notch_shape.Zs
        # No need to rotate more than a notch pitch
        alpha = self.alpha % (2 * np.pi / Zs)

        for ii in range(Zs // sym):
            notch_dict = dict()
            notch_dict["begin_angle"] = 2 * np.pi / Zs * ii + alpha - op / 2
            notch_dict["end_angle"] = 2 * np.pi / Zs * ii + alpha + op / 2
            notch_dict["obj"] = self.notch_shape
            notch_dict["lines"] = self.notch_shape.build_geometry()
            # Apply rotation
            for line in notch_dict["lines"]:
                line.rotate((notch_dict["begin_angle"] + notch_dict["end_angle"]) / 2)
            notch_dict["label"] = "Notch"
            notch_list.append(notch_dict)

        # If first notch is on Ox, then sym+1 notch are required (half on both yoke side)
        if notch_list[0]["begin_angle"] < 0 and sym != 1:
            notch_dict = dict()
            notch_dict["begin_angle"] = 2 * np.pi / Zs * (ii + 1) + alpha - op / 2
            notch_dict["end_angle"] = 2 * np.pi / Zs * (ii + 1) + alpha + op / 2
            notch_dict["obj"] = self.notch_shape
            notch_dict["lines"] = self.notch_shape.build_geometry()
            # Apply rotation
            for line in notch_dict["lines"]:
                line.rotate((notch_dict["begin_angle"] + notch_dict["end_angle"]) / 2)
            notch_dict["label"] = "Notch"
            notch_list.append(notch_dict)

        return notch_list

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, alpha=0, notch_shape=-1, key_mat=None, init_dict=None, init_str=None
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
            if "alpha" in list(init_dict.keys()):
                alpha = init_dict["alpha"]
            if "notch_shape" in list(init_dict.keys()):
                notch_shape = init_dict["notch_shape"]
            if "key_mat" in list(init_dict.keys()):
                key_mat = init_dict["key_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.alpha = alpha
        self.notch_shape = notch_shape
        # Call Notch init
        super(NotchEvenDist, self).__init__(key_mat=key_mat)
        # The class is frozen (in Notch init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        NotchEvenDist_str = ""
        # Get the properties inherited from Notch
        NotchEvenDist_str += super(NotchEvenDist, self).__str__()
        NotchEvenDist_str += "alpha = " + str(self.alpha) + linesep
        if self.notch_shape is not None:
            tmp = (
                self.notch_shape.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            NotchEvenDist_str += "notch_shape = " + tmp
        else:
            NotchEvenDist_str += "notch_shape = None" + linesep + linesep
        return NotchEvenDist_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Notch
        if not super(NotchEvenDist, self).__eq__(other):
            return False
        if other.alpha != self.alpha:
            return False
        if other.notch_shape != self.notch_shape:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Notch
        diff_list.extend(
            super(NotchEvenDist, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._alpha is not None
            and self._alpha is not None
            and np.isnan(other._alpha)
            and np.isnan(self._alpha)
        ):
            pass
        elif other._alpha != self._alpha:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._alpha) + ", other=" + str(other._alpha) + ")"
                )
                diff_list.append(name + ".alpha" + val_str)
            else:
                diff_list.append(name + ".alpha")
        if (other.notch_shape is None and self.notch_shape is not None) or (
            other.notch_shape is not None and self.notch_shape is None
        ):
            diff_list.append(name + ".notch_shape None mismatch")
        elif self.notch_shape is not None:
            diff_list.extend(
                self.notch_shape.compare(
                    other.notch_shape,
                    name=name + ".notch_shape",
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

        # Get size of the properties inherited from Notch
        S += super(NotchEvenDist, self).__sizeof__()
        S += getsizeof(self.alpha)
        S += getsizeof(self.notch_shape)
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

        # Get the properties inherited from Notch
        NotchEvenDist_dict = super(NotchEvenDist, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        NotchEvenDist_dict["alpha"] = self.alpha
        if self.notch_shape is None:
            NotchEvenDist_dict["notch_shape"] = None
        else:
            NotchEvenDist_dict["notch_shape"] = self.notch_shape.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        NotchEvenDist_dict["__class__"] = "NotchEvenDist"
        return NotchEvenDist_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        alpha_val = self.alpha
        if self.notch_shape is None:
            notch_shape_val = None
        else:
            notch_shape_val = self.notch_shape.copy()
        if self.key_mat is None:
            key_mat_val = None
        else:
            key_mat_val = self.key_mat.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            alpha=alpha_val, notch_shape=notch_shape_val, key_mat=key_mat_val
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.alpha = None
        if self.notch_shape is not None:
            self.notch_shape._set_None()
        # Set to None the properties inherited from Notch
        super(NotchEvenDist, self)._set_None()

    def _get_alpha(self):
        """getter of alpha"""
        return self._alpha

    def _set_alpha(self, value):
        """setter of alpha"""
        check_var("alpha", value, "float")
        self._alpha = value

    alpha = property(
        fget=_get_alpha,
        fset=_set_alpha,
        doc="""angular positon of the first notch (0 is middle of first tooth)

        :Type: float
        """,
    )

    def _get_notch_shape(self):
        """getter of notch_shape"""
        return self._notch_shape

    def _set_notch_shape(self, value):
        """setter of notch_shape"""
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
                "pyleecan.Classes", value.get("__class__"), "notch_shape"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Slot = import_class("pyleecan.Classes", "Slot", "notch_shape")
            value = Slot()
        check_var("notch_shape", value, "Slot")
        self._notch_shape = value

        if self._notch_shape is not None:
            self._notch_shape.parent = self

    notch_shape = property(
        fget=_get_notch_shape,
        fset=_set_notch_shape,
        doc="""Shape of the Notch

        :Type: Slot
        """,
    )
