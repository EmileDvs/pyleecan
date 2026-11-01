# File generated according to Generator/ClassesRef/Slot/SlotUD2.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/SlotUD2"""

from os import linesep
from sys import getsizeof

from pyleecan.Classes.Slot import Slot
from pyleecan.Classes._check import check_var
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SlotUD2(Slot):
    """ "User defined" Slot from a line list and a surface"""

    VERSION = 1

    # cf Methods.Slot.SlotUD2._set_split_active_surf_dict
    def _set_split_active_surf_dict(self, value):
        """setter of split_active_surf_dict"""
        if type(value) is dict:
            for key, obj_list in value.items():
                if type(obj_list) is list:
                    for ii, obj in enumerate(obj_list):
                        if type(obj) is dict and "__class__" in obj:
                            class_obj = import_class(
                                "pyleecan.Classes",
                                obj["__class__"],
                                "split_active_surf_dict",
                            )
                            value[key][ii] = class_obj(init_dict=obj)
        if value == -1:
            value = dict()
        check_var("split_active_surf_dict", value, "dict")
        self._split_active_surf_dict = value

    # cf Methods.Slot.SlotUD2.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object

        Returns
        -------
        curve_list: list
            A list of Segments

        """

        return [line.copy() for line in self.line_list]

    # cf Methods.Slot.SlotUD2.build_geometry_active
    def build_geometry_active(self, Nrad, Ntan, is_simplified=False, alpha=0, delta=0):
        """Split the slot active area in several zone
        This method assume that the active area is centered on X axis and symetrical
        Otherwise a dedicated build_geometry_active method must be provided

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        Nrad : int
            Number of radial layer
        Ntan : int
            Number of tangentiel layer
        is_simplified : bool
            boolean to specify if coincident lines are considered as one or different lines (Default value = False)
        alpha : float
            Angle for rotation (Default value = 0) [rad]
        delta : Complex
            complex for translation (Default value = 0)

        Returns
        -------
        surf_list:
            List of surface delimiting the active zone
        """

        Slot = import_class("pyleecan.Classes", "Slot")

        key = "Nrad=" + str(Nrad) + ", Ntan=" + str(Ntan)

        if (
            self.split_active_surf_dict is not None
            and key in self.split_active_surf_dict
        ):
            surf_list = [surf.copy() for surf in self.split_active_surf_dict[key]]
            self.set_label(surf_list, Nrad, Ntan, self.get_name_lam())
            return surf_list
        else:
            return Slot.build_geometry_active(
                self,
                Nrad=Nrad,
                Ntan=Ntan,
                is_simplified=is_simplified,
                alpha=alpha,
                delta=delta,
            )

    # cf Methods.Slot.SlotUD2.check
    def check(self):
        """Check that the SlotUD2 is correctly defined"""

        if self.line_list is None:
            self.line_list = list()

        if len(self.line_list) == 0:
            raise SlotCheckError("SlotUD2 must have at least one line")

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

    # cf Methods.Slot.SlotUD2.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotUD2
            A SlotUD2 object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """
        st = self.get_name_lam()
        surface = self.active_surf.copy()

        surface.label = "Wind_" + st + "_R0_T0_S0"

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        line_list=-1,
        active_surf=-1,
        split_active_surf_dict=None,
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
            if "active_surf" in list(init_dict.keys()):
                active_surf = init_dict["active_surf"]
            if "split_active_surf_dict" in list(init_dict.keys()):
                split_active_surf_dict = init_dict["split_active_surf_dict"]
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
        self.active_surf = active_surf
        self.split_active_surf_dict = split_active_surf_dict
        self.name = name
        # Call Slot init
        super(SlotUD2, self).__init__(Zs=Zs, wedge_mat=wedge_mat, is_bore=is_bore)
        # The class is frozen (in Slot init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SlotUD2_str = ""
        # Get the properties inherited from Slot
        SlotUD2_str += super(SlotUD2, self).__str__()
        if len(self.line_list) == 0:
            SlotUD2_str += "line_list = []" + linesep
        for ii in range(len(self.line_list)):
            tmp = (
                self.line_list[ii].__str__().replace(linesep, linesep + "\t") + linesep
            )
            SlotUD2_str += "line_list[" + str(ii) + "] =" + tmp + linesep + linesep
        if self.active_surf is not None:
            tmp = (
                self.active_surf.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            )
            SlotUD2_str += "active_surf = " + tmp
        else:
            SlotUD2_str += "active_surf = None" + linesep + linesep
        SlotUD2_str += (
            "split_active_surf_dict = " + str(self.split_active_surf_dict) + linesep
        )
        SlotUD2_str += 'name = "' + str(self.name) + '"' + linesep
        return SlotUD2_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Slot
        if not super(SlotUD2, self).__eq__(other):
            return False
        if other.line_list != self.line_list:
            return False
        if other.active_surf != self.active_surf:
            return False
        if other.split_active_surf_dict != self.split_active_surf_dict:
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
            super(SlotUD2, self).compare(
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
        if (other.active_surf is None and self.active_surf is not None) or (
            other.active_surf is not None and self.active_surf is None
        ):
            diff_list.append(name + ".active_surf None mismatch")
        elif self.active_surf is not None:
            diff_list.extend(
                self.active_surf.compare(
                    other.active_surf,
                    name=name + ".active_surf",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._split_active_surf_dict != self._split_active_surf_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._split_active_surf_dict)
                    + ", other="
                    + str(other._split_active_surf_dict)
                    + ")"
                )
                diff_list.append(name + ".split_active_surf_dict" + val_str)
            else:
                diff_list.append(name + ".split_active_surf_dict")
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
        S += super(SlotUD2, self).__sizeof__()
        if self.line_list is not None:
            for value in self.line_list:
                S += getsizeof(value)
        S += getsizeof(self.active_surf)
        if self.split_active_surf_dict is not None:
            for key, value in self.split_active_surf_dict.items():
                S += getsizeof(value) + getsizeof(key)
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
        SlotUD2_dict = super(SlotUD2, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.line_list is None:
            SlotUD2_dict["line_list"] = None
        else:
            SlotUD2_dict["line_list"] = list()
            for obj in self.line_list:
                if obj is not None:
                    SlotUD2_dict["line_list"].append(
                        obj.as_dict(
                            type_handle_ndarray=type_handle_ndarray,
                            keep_function=keep_function,
                            **kwargs
                        )
                    )
                else:
                    SlotUD2_dict["line_list"].append(None)
        if self.active_surf is None:
            SlotUD2_dict["active_surf"] = None
        else:
            SlotUD2_dict["active_surf"] = self.active_surf.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        SlotUD2_dict["split_active_surf_dict"] = (
            self.split_active_surf_dict.copy()
            if self.split_active_surf_dict is not None
            else None
        )
        SlotUD2_dict["name"] = self.name
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SlotUD2_dict["__class__"] = "SlotUD2"
        return SlotUD2_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.line_list is None:
            line_list_val = None
        else:
            line_list_val = list()
            for obj in self.line_list:
                line_list_val.append(obj.copy())
        if self.active_surf is None:
            active_surf_val = None
        else:
            active_surf_val = self.active_surf.copy()
        if self.split_active_surf_dict is None:
            split_active_surf_dict_val = None
        else:
            split_active_surf_dict_val = self.split_active_surf_dict.copy()
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
            active_surf=active_surf_val,
            split_active_surf_dict=split_active_surf_dict_val,
            name=name_val,
            Zs=Zs_val,
            wedge_mat=wedge_mat_val,
            is_bore=is_bore_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.line_list = None
        if self.active_surf is not None:
            self.active_surf._set_None()
        self.split_active_surf_dict = None
        self.name = None
        # Set to None the properties inherited from Slot
        super(SlotUD2, self)._set_None()

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

    def _get_active_surf(self):
        """getter of active_surf"""
        return self._active_surf

    def _set_active_surf(self, value):
        """setter of active_surf"""
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
                "pyleecan.Classes", value.get("__class__"), "active_surf"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Surface = import_class("pyleecan.Classes", "Surface", "active_surf")
            value = Surface()
        check_var("active_surf", value, "Surface")
        self._active_surf = value

        if self._active_surf is not None:
            self._active_surf.parent = self

    active_surf = property(
        fget=_get_active_surf,
        fset=_set_active_surf,
        doc="""Active surface of the Slot

        :Type: Surface
        """,
    )

    def _get_split_active_surf_dict(self):
        """getter of split_active_surf_dict"""
        return self._split_active_surf_dict

    split_active_surf_dict = property(
        fget=_get_split_active_surf_dict,
        fset=_set_split_active_surf_dict,
        doc="""Dictionary to enforced the split active surface (key="Nrad=1, Ntan=2"). Labels set according to list order (loop on Nrad then Ntan)

        :Type: dict
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

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass


MachineCheckError = SlotUD2.MachineCheckError

LaminationCheckError = SlotUD2.LaminationCheckError

SlotCheckError = SlotUD2.SlotCheckError
