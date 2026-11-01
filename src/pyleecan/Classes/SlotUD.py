# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Slot/SlotUD.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotUD
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Slot import Slot

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Slot.Slot import SlotCheckError
from ..Functions.labels import WIND_LAB, SOP_LAB
from .Segment import Segment
from .Arc1 import Arc1
from .SurfLine import SurfLine

from numpy import isnan
from ._check import InitUnKnowClassError


class SlotUD(Slot):
    """ "User defined" Slot from a line list."""

    VERSION = 1

    # cf Methods.Slot.SlotUD.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotUD
            A SlotUD object

        Returns
        -------
        curve_list: list
            A list of Segments

        """

        return [line.copy() for line in self.line_list]

    # cf Methods.Slot.SlotUD.check
    def check(self):
        """Check that the SlotUD is correctly defined"""

        if self.line_list is None:
            self.line_list = list()

        if len(self.line_list) == 0:
            raise SlotCheckError("SlotUD must have at least one line")

        for ii in range(len(self.line_list) - 1):
            if (
                abs(self.line_list[ii].get_end() - self.line_list[ii + 1].get_begin())
                > 1e-6
            ):
                raise SlotCheckError(
                    "SlotUD line "
                    + str(ii)
                    + " and line "
                    + str(ii + 1)
                    + " doesn't match"
                )

        begin_id = self.wind_begin_index
        end_id = self.wind_end_index
        if begin_id is not None and end_id is not None:
            if begin_id > len(self.line_list):
                raise SlotCheckError(
                    "SlotUD wind_begin_index is greater than line_list length"
                )
            if end_id > len(self.line_list):
                raise SlotCheckError(
                    "SlotUD wind_end_index is greater than line_list length"
                )
            if begin_id > end_id:
                raise SlotCheckError(
                    "SlotUD wind_begin_index is greater than wind_end_index"
                )

    # cf Methods.Slot.SlotUD.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """
        # get curve_list
        type_line_wind = self.type_line_wind
        if self.wind_begin_index is None and self.wind_end_index is None:
            # Winding not define, use complete surface
            line_list = self.build_geometry()
            type_line_wind = 1  # Enforce Arc1
        else:
            line_list = self.build_geometry()[
                self.wind_begin_index : self.wind_end_index
            ]

        # Add closing line
        if type_line_wind == 0:
            line_list.append(
                Segment(begin=line_list[-1].get_end(), end=line_list[0].get_begin())
            )
        else:
            line_list.append(
                Arc1(
                    begin=line_list[-1].get_end(),
                    end=line_list[0].get_begin(),
                    radius=-abs(line_list[-1].get_end()),
                    is_trigo_direction=False,
                )
            )

        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=line_list, label=label)
        surface.comp_point_ref(is_set=True)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # cf Methods.Slot.SlotUD.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # get curve_list
        line_list = self.build_geometry()
        curve_list_start = line_list[: self.wind_begin_index]
        curve_list_end = line_list[self.wind_end_index :]
        # Active Line
        Zb = curve_list_start[-1].get_end()
        Ze = curve_list_end[0].get_begin()
        if self.type_line_wind == 0:
            act_line = Segment(begin=Zb, end=Ze)
        else:
            act_line = Arc1(
                begin=Zb,
                end=Ze,
                radius=abs(Zb),
                is_trigo_direction=True,
            )
        bot_line = Arc1(
            curve_list_end[-1].get_end(),
            curve_list_start[0].get_begin(),
            -self.get_Rbo(),
            is_trigo_direction=False,
        )

        curve_list = curve_list_start + [act_line] + curve_list_end + [bot_line]
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label)
        surface.comp_point_ref(is_set=True)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # cf Methods.Slot.SlotUD.set_from_point_list
    def set_from_point_list(self, point_list, is_sym=False):
        """Set the line_list from a point list (connected by Segments)

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        point_list : [complex]
            List of complex coordinates
        is_sym : bool
            True to duplicate the point by symmetries
        """

        # Apply symmetry if needed
        Z_list = point_list.copy()
        if is_sym:
            for point in point_list[::-1]:
                Z_list.append(point.conjugate())

        # Creation of curve
        line_list = list()
        for ii in range(len(Z_list) - 1):
            line_list.append(Segment(Z_list[ii], Z_list[ii + 1]))

        self.line_list = line_list

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        line_list=-1,
        wind_begin_index=None,
        wind_end_index=None,
        type_line_wind=0,
        name="",
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
            if "line_list" in list(init_dict.keys()):
                line_list = init_dict["line_list"]
            if "wind_begin_index" in list(init_dict.keys()):
                wind_begin_index = init_dict["wind_begin_index"]
            if "wind_end_index" in list(init_dict.keys()):
                wind_end_index = init_dict["wind_end_index"]
            if "type_line_wind" in list(init_dict.keys()):
                type_line_wind = init_dict["type_line_wind"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "Zs" in list(init_dict.keys()):
                Zs = init_dict["Zs"]
            if "wedge_mat" in list(init_dict.keys()):
                wedge_mat = init_dict["wedge_mat"]
            if "is_bore" in list(init_dict.keys()):
                is_bore = init_dict["is_bore"]
        # Set the properties (value check and convertion are done in setter)
        self.line_list = line_list
        self.wind_begin_index = wind_begin_index
        self.wind_end_index = wind_end_index
        self.type_line_wind = type_line_wind
        self.name = name
        # Call Slot init
        super(SlotUD, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotUD_str = ""
        # Get the properties inherited from Slot
        SlotUD_str += super(SlotUD, self).__str__()
        if len(self.line_list) == 0:
            SlotUD_str += "line_list = []" + linesep
        for ii in range(len(self.line_list)):
            tmp = (
                self.line_list[ii].__str__().replace(linesep, linesep + "\t") + linesep
            )
            SlotUD_str += "line_list[" + str(ii) + "] =" + tmp + linesep + linesep
        SlotUD_str += "wind_begin_index = " + str(self.wind_begin_index) + linesep
        SlotUD_str += "wind_end_index = " + str(self.wind_end_index) + linesep
        SlotUD_str += "type_line_wind = " + str(self.type_line_wind) + linesep
        SlotUD_str += 'name = "' + str(self.name) + '"' + linesep
        return SlotUD_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotUD, self).__eq__(other):
            return False
        if other.line_list != self.line_list:
            return False
        if other.wind_begin_index != self.wind_begin_index:
            return False
        if other.wind_end_index != self.wind_end_index:
            return False
        if other.type_line_wind != self.type_line_wind:
            return False
        if other.name != self.name:
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
            super(SlotUD, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.line_list is None and self.line_list is not None) or (
            other.line_list is not None and self.line_list is None
        ):
            diff_list.append(name + ".line_list None mismatch")
        elif self.line_list is None:
            pass
        elif len(other.line_list) != len(self.line_list):
            diff_list.append("len(" + name + ".line_list)")
        else:
            for ii in range(len(other.line_list)):
                diff_list.extend(
                    self.line_list[ii].compare(
                        other.line_list[ii],
                        name=name + ".line_list[" + str(ii) + "]",
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
        if other._wind_begin_index != self._wind_begin_index:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._wind_begin_index)
                    + ", other="
                    + str(other._wind_begin_index)
                    + ")"
                )
                diff_list.append(name + ".wind_begin_index" + val_str)
            else:
                diff_list.append(name + ".wind_begin_index")
        if other._wind_end_index != self._wind_end_index:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._wind_end_index)
                    + ", other="
                    + str(other._wind_end_index)
                    + ")"
                )
                diff_list.append(name + ".wind_end_index" + val_str)
            else:
                diff_list.append(name + ".wind_end_index")
        if other._type_line_wind != self._type_line_wind:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_line_wind)
                    + ", other="
                    + str(other._type_line_wind)
                    + ")"
                )
                diff_list.append(name + ".type_line_wind" + val_str)
            else:
                diff_list.append(name + ".type_line_wind")
        if other._name != self._name:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._name) + ", other=" + str(other._name) + ")"
                )
                diff_list.append(name + ".name" + val_str)
            else:
                diff_list.append(name + ".name")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Slot
        S += super(SlotUD, self).__sizeof__()
        if self.line_list is not None:
            for value in self.line_list:
                S += getsizeof(value)
        S += getsizeof(self.wind_begin_index)
        S += getsizeof(self.wind_end_index)
        S += getsizeof(self.type_line_wind)
        S += getsizeof(self.name)
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
        SlotUD_dict = super(SlotUD, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.line_list is None:
            SlotUD_dict["line_list"] = None
        else:
            SlotUD_dict["line_list"] = list()
            for obj in self.line_list:
                if obj is not None:
                    SlotUD_dict["line_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    SlotUD_dict["line_list"].append(None)
        SlotUD_dict["wind_begin_index"] = self.wind_begin_index
        SlotUD_dict["wind_end_index"] = self.wind_end_index
        SlotUD_dict["type_line_wind"] = self.type_line_wind
        SlotUD_dict["name"] = self.name
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotUD_dict["__class__"] = "SlotUD"
        return SlotUD_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.line_list is None:
            line_list_val = None
        else:
            line_list_val = list()
            for obj in self.line_list:
                line_list_val.append(obj.copy())
        wind_begin_index_val = self.wind_begin_index
        wind_end_index_val = self.wind_end_index
        type_line_wind_val = self.type_line_wind
        name_val = self.name
        Zs_val = self.Zs
        if self.wedge_mat is None:
            wedge_mat_val = None
        else:
            wedge_mat_val = self.wedge_mat.copy()
        is_bore_val = self.is_bore
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            line_list=line_list_val,
            wind_begin_index=wind_begin_index_val,
            wind_end_index=wind_end_index_val,
            type_line_wind=type_line_wind_val,
            name=name_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.line_list = None
        self.wind_begin_index = None
        self.wind_end_index = None
        self.type_line_wind = None
        self.name = None
        # Set to None the properties inherited from Slot
        super(SlotUD, self)._set_None()

    def _get_line_list(self):
        """getter of line_list"""
        if self._line_list is not None:
            for obj in self._line_list:
                if obj is not None:
                    obj.parent = self
        return self._line_list

    def _set_line_list(self, value):
        """setter of line_list"""
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
                        "pyleecan.Classes", obj.get("__class__"), "line_list"
                    )
                    value[ii] = class_obj(init_dict=obj)
                if value[ii] is not None:
                    value[ii].parent = self
        if value == -1:
            value = list()
        check_var("line_list", value, "[Line]")
        self._line_list = value

    line_list = property(
        fget=_get_line_list,
        fset=_set_line_list,
        doc="""list of line to draw the edges of the slot

        :Type: [Line]
        """,
    )

    def _get_wind_begin_index(self):
        """getter of wind_begin_index"""
        return self._wind_begin_index

    def _set_wind_begin_index(self, value):
        """setter of wind_begin_index"""
        check_var("wind_begin_index", value, "int")
        self._wind_begin_index = value

    wind_begin_index = property(
        fget=_get_wind_begin_index,
        fset=_set_wind_begin_index,
        doc="""Index of the first line to include in the winding

        :Type: int
        """,
    )

    def _get_wind_end_index(self):
        """getter of wind_end_index"""
        return self._wind_end_index

    def _set_wind_end_index(self, value):
        """setter of wind_end_index"""
        check_var("wind_end_index", value, "int")
        self._wind_end_index = value

    wind_end_index = property(
        fget=_get_wind_end_index,
        fset=_set_wind_end_index,
        doc="""Index of the last line to include in the winding

        :Type: int
        """,
    )

    def _get_type_line_wind(self):
        """getter of type_line_wind"""
        return self._type_line_wind

    def _set_type_line_wind(self, value):
        """setter of type_line_wind"""
        check_var("type_line_wind", value, "int", Vmin=0, Vmax=1)
        self._type_line_wind = value

    type_line_wind = property(
        fget=_get_type_line_wind,
        fset=_set_type_line_wind,
        doc="""0 to close winding with Segment, 1 for Arc1

        :Type: int
        :min: 0
        :max: 1
        """,
    )

    def _get_name(self):
        """getter of name"""
        return self._name

    def _set_name(self, value):
        """setter of name"""
        check_var("name", value, "str")
        self._name = value

    name = property(
        fget=_get_name,
        fset=_set_name,
        doc="""Name of the slot (for save)

        :Type: str
        """,
    )
