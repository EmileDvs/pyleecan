# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/Bore.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Bore
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
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Methods import ParentMissingError
from numpy import pi, exp
from pyleecan.Functions.Geometry.cut_lines_between_angle import cut_lines_between_angles
from pyleecan.Classes.Segment import Segment
from pyleecan.Methods.Machine.Bore.plot import ROTOR_COLOR, STATOR_COLOR
from pyleecan.Functions.init_fig import init_fig

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class Bore(FrozenClass):
    """Abstract class for Bore shape"""

    VERSION = 1

    # cf Methods.Machine.Bore.comp_Rmax
    def comp_Rmax(self):
        """Compute the maximum radius of the Bore shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Rmax : float
            Maximum radius of the Bore shape [m]
        """

        line_list = self.get_bore_line()
        point_list = list()

        for line in line_list:
            point_list.extend(line.discretize(100))

        return np.max(np.abs(np.array(point_list)))

    # cf Methods.Machine.Bore.comp_Rmin
    def comp_Rmin(self):
        """Compute the minimum radius of the Bore shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Rmin : float
            Minimum radius of the Bore shape
        """

        line_list = self.get_bore_line()
        point_list = list()

        for line in line_list:
            point_list.extend(line.discretize(100))

        return np.min(np.abs(np.array(point_list)))

    # cf Methods.Machine.Bore.comp_surface
    def comp_surface(self):
        """Returns the area of the shape

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Sbore : float
            Area of the bore
        """

        return self.get_surface().comp_surface()

    # cf Methods.Machine.Bore.get_surface
    def get_surface(self):
        """Returns the bore shape as a Surface object

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        Sbore : Surface
            Surface object to draw the bore
        """

        line_list = self.get_bore_line()

        return SurfLine(line_list=line_list, point_ref=0, label="Bore")

    # cf Methods.Machine.Bore.is_yoke
    def is_yoke(self):
        """Return if the Shape is for the Bore or Yoke radius

        Parameters
        ----------
        self : Bore
            A Bore object

        Returns
        -------
        is_yoke : bool
            True if the shape is on the yoke
        """

        if self.parent is not None:
            return self is self.parent.yoke
        else:
            raise ParentMissingError(
                "Error: The Bore object is not inside a Lamination"
            )

    # cf Methods.Machine.Bore.merge_slot
    def merge_slot(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """
        if self.type_merge_slot == 0:
            return self.merge_slot_connect(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        if self.type_merge_slot == 1:
            return self.merge_slot_intersect(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        if self.type_merge_slot == 2:
            return self.merge_slot_translate(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )
        else:
            raise Exception("Not implemented yet")

    # cf Methods.Machine.Bore.merge_slot_connect
    def merge_slot_connect(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Connect method: Add lines between radius and notch/slot
        (To use when the radius shape have circular part matchine the radius
        or when radius lines are bellow normal radius)

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        # Get all Radius lines (0 to 2*pi)
        radius_lines = self.get_bore_line()

        # Update begin and end angle if Radius (next step already cut lines)
        if sym != 1 and radius_desc_list[0]["label"] == "Radius":
            radius_desc_list[0]["begin_angle"] = 0
        if sym != 1 and radius_desc_list[-1]["label"] == "Radius":
            radius_desc_list[-1]["end_angle"] = 2 * pi / sym

        # Replace Arc radius from desc by lines from shape
        for desc_dict in radius_desc_list:
            if desc_dict["label"] == "Radius":
                desc_dict["lines"] = cut_lines_between_angles(
                    radius_lines, desc_dict["begin_angle"], desc_dict["end_angle"]
                )

        # If slot/notch are coliding with sym lines => Cut
        if sym != 1:
            # Cut first desc (if needed)
            if radius_desc_list[0]["begin_angle"] < 0:
                lines = list()
                for line in radius_desc_list[0]["lines"]:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_desc_list[0]["begin_angle"] = 0
                radius_desc_list[0]["lines"] = lines
            # Cut last desc (if needed)
            if radius_desc_list[-1]["end_angle"] > 2 * pi / sym:
                lines = list()
                for line in radius_desc_list[-1]["lines"]:
                    _, bot_split_list = line.split_line(0, exp(1j * 2 * pi / sym))
                    lines.extend(bot_split_list)
                radius_desc_list[-1]["end_angle"] = 2 * pi / sym
                radius_desc_list[-1]["lines"] = lines

        # Apply merge strategy on slot/notch
        line_list = list()
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                # Add prop_dict on all the Radius Lines
                if prop_dict is not None:
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = dict()
                        line.prop_dict.update(prop_dict)
                line_list.extend(desc_dict["lines"])
            else:  # Connect and add notch lines
                if len(line_list) > 0:
                    # Connect Radius to slot/notch by Segment (if needed)
                    if (
                        abs(line_list[-1].get_end() - desc_dict["lines"][0].get_begin())
                        > 1e-6
                    ):
                        line_list.append(
                            Segment(
                                line_list[-1].get_end(),
                                desc_dict["lines"][0].get_begin(),
                            )
                        )
                line_list.extend(desc_dict["lines"])
                # Connect slot/notch to next radius
                if (
                    abs(
                        radius_desc_list[ii + 1]["lines"][0].get_begin()
                        - desc_dict["lines"][-1].get_end()
                    )
                    > 1e-6
                ):
                    line_list.append(
                        Segment(
                            desc_dict["lines"][-1].get_end(),
                            radius_desc_list[ii + 1]["lines"][0].get_begin(),
                        )
                    )
        return line_list

    # cf Methods.Machine.Bore.merge_slot_intersect
    def merge_slot_intersect(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Intersect method: cut lines of notch/slot to make the radius end match notch/slot begin
        technically reduice slot/notch height without changing yoke height

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        # Get all Radius lines (0 to 2*pi)
        radius_lines = self.get_bore_line()

        # Update begin and end angle if Radius (next step already cut lines)
        if sym != 1 and radius_desc_list[0]["label"] == "Radius":
            radius_desc_list[0]["begin_angle"] = 0
        if sym != 1 and radius_desc_list[-1]["label"] == "Radius":
            radius_desc_list[-1]["end_angle"] = 2 * pi / sym

        # Replace Arc radius from desc by lines from shape
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                desc_dict["lines"] = cut_lines_between_angles(
                    radius_lines, desc_dict["begin_angle"], desc_dict["end_angle"]
                )

        # # Check that the Radius lines are correct
        # for ii, desc_dict in enumerate(radius_desc_list):
        #     if desc_dict["label"] == "Radius":
        #         print(ii)
        #         print(
        #             str(desc_dict["begin_angle"])
        #             + " and "
        #             + str(angle(desc_dict["lines"][0].get_begin()) % (2 * pi))
        #         )
        #         print(
        #             str(desc_dict["end_angle"])
        #             + " and "
        #             + str(angle(desc_dict["lines"][-1].get_end()) % (2 * pi))
        #         )

        # If slot/notch are coliding with sym lines => Cut
        if sym != 1:
            # Cut first desc (if needed)
            if radius_desc_list[0]["begin_angle"] < 0:
                lines = list()
                for line in radius_desc_list[0]["lines"]:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_desc_list[0]["begin_angle"] = 0
                radius_desc_list[0]["lines"] = lines
            # Cut last desc (if needed)
            if radius_desc_list[-1]["end_angle"] > 2 * pi / sym:
                lines = list()
                for line in radius_desc_list[-1]["lines"]:
                    _, bot_split_list = line.split_line(0, exp(1j * 2 * pi / sym))
                    lines.extend(bot_split_list)
                radius_desc_list[-1]["end_angle"] = 2 * pi / sym
                radius_desc_list[-1]["lines"] = lines

        # Apply merge strategy on slot/notch
        line_list = list()
        for ii, desc_dict in enumerate(radius_desc_list):
            if desc_dict["label"] == "Radius":
                # Add prop_dict on all the Radius Lines
                if prop_dict is not None:
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = dict()
                        line.prop_dict.update(prop_dict)
                line_list.extend(desc_dict["lines"])
            else:  # Intersect and add slot/notch lines
                # Define First cutting line
                # rad_line = radius_desc_list[ii - 1]["lines"][-1]
                op = desc_dict["end_angle"] - desc_dict["begin_angle"]
                if not (ii == 0 and sym != 1):  # No first cut for first notch on Ox
                    rad_line_list = cut_lines_between_angles(
                        radius_lines,
                        desc_dict["begin_angle"] - op / 4,
                        desc_dict["begin_angle"] + op / 4,
                    )
                    # Find first line to intersect with cutting line
                    for jj in range(len(desc_dict["lines"])):
                        inter_list = desc_dict["lines"][jj].intersect_obj(
                            rad_line_list[-1], is_on_line=True
                        )
                        if len(inter_list) > 0:
                            break
                    if jj < len(desc_dict["lines"]) - 1:
                        # Slot/notch was cut => Replace lines by cut ones
                        desc_dict["lines"] = desc_dict["lines"][
                            jj:
                        ]  # Keep all lines after cut
                        # Update lines to start/end at cutting point
                        desc_dict["lines"][0].split_point(inter_list[0], is_begin=False)
                        if len(line_list) == 0:  # Slot/notch on Ox
                            radius_desc_list[-1]["lines"][-1].split_point(
                                inter_list[0], is_begin=True
                            )
                        else:
                            line_list[-1].split_point(inter_list[0], is_begin=True)
                    else:  # The slot is above the shape => Use shape lines
                        desc_dict["lines"] = cut_lines_between_angles(
                            radius_lines,
                            desc_dict["begin_angle"],
                            desc_dict["end_angle"],
                        )
                        # Add prop_dict on all the Radius Lines
                        if prop_dict is not None:
                            for line in desc_dict["lines"]:
                                if line.prop_dict is None:
                                    line.prop_dict = dict()
                                line.prop_dict.update(prop_dict)
                        line_list.extend(desc_dict["lines"])
                        continue  # No need to cut the other side
                # Second cut
                if not (ii == len(radius_desc_list) - 1 and sym != 1):
                    # No second cut for notch on sym line
                    rad_line_list = cut_lines_between_angles(
                        radius_lines,
                        desc_dict["end_angle"] - op / 4,
                        desc_dict["end_angle"] + op / 4,
                    )
                    for jj in range(len(desc_dict["lines"])):
                        inter_list = desc_dict["lines"][-(jj + 1)].intersect_obj(
                            rad_line_list[0], is_on_line=True
                        )
                        if len(inter_list) > 0:
                            break
                    if jj < len(desc_dict["lines"]):
                        # Slot/notch was cut => Replace lines by cut ones
                        if jj != 0:  # Keep all the lines if last line is cut
                            desc_dict["lines"] = desc_dict["lines"][
                                :-jj
                            ]  # Keep all lines before cut
                        # Update lines to start/end at cutting point
                        desc_dict["lines"][-1].split_point(inter_list[0], is_begin=True)
                        radius_desc_list[ii + 1]["lines"][0].split_point(
                            inter_list[0], is_begin=False
                        )
                # Add slot/notch lines to final list
                line_list.extend(desc_dict["lines"])
        return line_list

    # cf Methods.Machine.Bore.merge_slot_translate
    def merge_slot_translate(self, radius_desc_list, prop_dict, sym):
        """Merge the Bore shape with notches/slot on the bore/yoke
        Translate method: Translate lines of notch/slot to match the radius of the shape
        technically Keep the slot/notch height by reduicing the yoke height

        Parameters
        ----------
        radius_desc_list : list
            List of dict to describe the bore/yoke radius
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        line_list : list
            List of lines needed to draw the radius
        """

        raise Exception("Not Implemented Yet")

    # cf Methods.Machine.Bore.plot
    def plot(self, fig=None, ax=None):
        """Plot the Bore in a matplotlib fig

        Parameters
        ----------
        self : Bore
            A Bore object
        fig :
            if None, open a new fig and plot, else add to the current
            one (Default value = None)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        surf = self.get_surface()

        # Display the result
        (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Bore")

        # Add the Bore to the fig
        if self.get_is_stator:
            patches = surf.get_patches(color=STATOR_COLOR)
        else:
            patches = surf.get_patch(color=ROTOR_COLOR)
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")
        fig.show()
        return fig, ax

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, type_merge_slot=1, alpha=0, init_dict=None, init_str=None):
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
            if "type_merge_slot" in list(init_dict.keys()):
                type_merge_slot = init_dict["type_merge_slot"]
            if "alpha" in list(init_dict.keys()):
                alpha = init_dict["alpha"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.type_merge_slot = type_merge_slot
        self.alpha = alpha

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Bore_str = ""
        if self.parent is None:
            Bore_str += "parent = None " + linesep
        else:
            Bore_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Bore_str += "type_merge_slot = " + str(self.type_merge_slot) + linesep
        Bore_str += "alpha = " + str(self.alpha) + linesep
        return Bore_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.type_merge_slot != self.type_merge_slot:
            return False
        if other.alpha != self.alpha:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._type_merge_slot != self._type_merge_slot:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_merge_slot)
                    + ", other="
                    + str(other._type_merge_slot)
                    + ")"
                )
                diff_list.append(name + ".type_merge_slot" + val_str)
            else:
                diff_list.append(name + ".type_merge_slot")
        if (
            other._alpha is not None
            and self._alpha is not None
            and isnan(other._alpha)
            and isnan(self._alpha)
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
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.type_merge_slot)
        S += getsizeof(self.alpha)
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

        Bore_dict = dict()
        Bore_dict["type_merge_slot"] = self.type_merge_slot
        Bore_dict["alpha"] = self.alpha
        # The class name is added to the dict for deserialisation purpose
        Bore_dict["__class__"] = "Bore"
        return Bore_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        type_merge_slot_val = self.type_merge_slot
        alpha_val = self.alpha
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(type_merge_slot=type_merge_slot_val, alpha=alpha_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.type_merge_slot = None
        self.alpha = None

    def _get_type_merge_slot(self):
        """getter of type_merge_slot"""
        return self._type_merge_slot

    def _set_type_merge_slot(self, value):
        """setter of type_merge_slot"""
        check_var("type_merge_slot", value, "int", Vmin=0, Vmax=2)
        self._type_merge_slot = value

    type_merge_slot = property(
        fget=_get_type_merge_slot,
        fset=_set_type_merge_slot,
        doc="""how to merge slot/notch into the bore radius (0: connect the dot, 1: intersection, 2: translate)

        :Type: int
        :min: 0
        :max: 2
        """,
    )

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
        doc="""Angular offset for the bore shape

        :Type: float
        """,
    )
