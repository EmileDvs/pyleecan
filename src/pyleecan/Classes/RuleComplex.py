# File generated according to Generator/ClassesRef/Converter/RuleComplex.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Converter/RuleComplex"""

from os import linesep
from sys import getsizeof

from pyleecan.Classes.Rule import Rule
from pyleecan.Classes._check import check_var

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class RuleComplex(Rule):
    """complex rules"""

    VERSION = 1

    # cf Methods.Converter.RuleComplex._set_fct_name
    def _set_fct_name(self, value):
        """find the path of a function

        Parameters
        ----------
        self : RuleComplex
            A RuleComplex object
        value : str
            name of file for complex rule

        """

        # Check that value is a str
        check_var("_fct_name", value, "str")

        self._fct_name = value

        # Load the function
        if self._fct_name is not None:
            module = __import__(
                f"pyleecan.Functions.Converter.MotorCAD.{self.fct_name}",
                fromlist=(self.fct_name),
            )
            self.other_to_P = getattr(module, "other_to_P")
            self.P_to_other = getattr(module, "P_to_other")

    # cf Methods.Converter.RuleComplex.convert_to_other
    def convert_to_other(self, other_dict, machine, other_unit_dict):
        """Selects value in machine and implements it in other_dict

        Parameters
        ----------
        self : RulesComplex
            A RuleComplex object
        other_dict : dict
            dict created from the file to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """
        other_dict = self.P_to_other(self, machine, other_dict)

        return other_dict

    # cf Methods.Converter.RuleComplex.convert_to_P
    def convert_to_P(self, other_dict, machine, other_unit_dict):
        """Selects value in other_dict and implements it in machine

        Parameters
        ----------
        self : RulesComplex
            A RuleComplex object
        other_dict : dict
            dict created from the file to be converted
        machine : Machine
            A pyleecan machine
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        """
        machine = self.other_to_P(self, machine, other_dict, other_unit_dict)

        return machine

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        fct_name=None,
        folder=None,
        param_dict=-1,
        unit_type="m",
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
            if "fct_name" in list(init_dict.keys()):
                fct_name = init_dict["fct_name"]
            if "folder" in list(init_dict.keys()):
                folder = init_dict["folder"]
            if "param_dict" in list(init_dict.keys()):
                param_dict = init_dict["param_dict"]
            if "unit_type" in list(init_dict.keys()):
                unit_type = init_dict["unit_type"]
        # Set the properties (value check and convertion are done in setter)
        self.fct_name = fct_name
        self.folder = folder
        self.param_dict = param_dict
        # Call Rule init
        super(RuleComplex, self).__init__(unit_type=unit_type)
        # The class is frozen (in Rule init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        RuleComplex_str = ""
        # Get the properties inherited from Rule
        RuleComplex_str += super(RuleComplex, self).__str__()
        RuleComplex_str += 'fct_name = "' + str(self.fct_name) + '"' + linesep
        RuleComplex_str += 'folder = "' + str(self.folder) + '"' + linesep
        RuleComplex_str += "param_dict = " + str(self.param_dict) + linesep
        return RuleComplex_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Rule
        if not super(RuleComplex, self).__eq__(other):
            return False
        if other.fct_name != self.fct_name:
            return False
        if other.folder != self.folder:
            return False
        if other.param_dict != self.param_dict:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Rule
        diff_list.extend(
            super(RuleComplex, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._fct_name != self._fct_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._fct_name)
                    + ", other="
                    + str(other._fct_name)
                    + ")"
                )
                diff_list.append(name + ".fct_name" + val_str)
            else:
                diff_list.append(name + ".fct_name")
        if other._folder != self._folder:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._folder)
                    + ", other="
                    + str(other._folder)
                    + ")"
                )
                diff_list.append(name + ".folder" + val_str)
            else:
                diff_list.append(name + ".folder")
        if other._param_dict != self._param_dict:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._param_dict)
                    + ", other="
                    + str(other._param_dict)
                    + ")"
                )
                diff_list.append(name + ".param_dict" + val_str)
            else:
                diff_list.append(name + ".param_dict")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Rule
        S += super(RuleComplex, self).__sizeof__()
        S += getsizeof(self.fct_name)
        S += getsizeof(self.folder)
        if self.param_dict is not None:
            for key, value in self.param_dict.items():
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

        # Get the properties inherited from Rule
        RuleComplex_dict = super(RuleComplex, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        RuleComplex_dict["fct_name"] = self.fct_name
        RuleComplex_dict["folder"] = self.folder
        RuleComplex_dict["param_dict"] = (
            self.param_dict.copy() if self.param_dict is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        RuleComplex_dict["__class__"] = "RuleComplex"
        return RuleComplex_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        fct_name_val = self.fct_name
        folder_val = self.folder
        if self.param_dict is None:
            param_dict_val = None
        else:
            param_dict_val = self.param_dict.copy()
        unit_type_val = self.unit_type
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            fct_name=fct_name_val,
            folder=folder_val,
            param_dict=param_dict_val,
            unit_type=unit_type_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.fct_name = None
        self.folder = None
        self.param_dict = None
        # Set to None the properties inherited from Rule
        super(RuleComplex, self)._set_None()

    def _get_fct_name(self):
        """getter of fct_name"""
        return self._fct_name

    fct_name = property(
        fget=_get_fct_name,
        fset=_set_fct_name,
        doc="""fonction name to convert

        :Type: str
        """,
    )

    def _get_folder(self):
        """getter of folder"""
        return self._folder

    def _set_folder(self, value):
        """setter of folder"""
        check_var("folder", value, "str")
        self._folder = value

    folder = property(
        fget=_get_folder,
        fset=_set_folder,
        doc="""name source

        :Type: str
        """,
    )

    def _get_param_dict(self):
        """getter of param_dict"""
        return self._param_dict

    def _set_param_dict(self, value):
        """setter of param_dict"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("param_dict", value, "dict")
        self._param_dict = value

    param_dict = property(
        fget=_get_param_dict,
        fset=_set_param_dict,
        doc="""dict to pass param 

        :Type: dict
        """,
    )
