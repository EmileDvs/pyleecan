# File generated according to Generator/ClassesRef/Converter/Rule.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Converter/Rule"""

from os import linesep
from sys import getsizeof

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Rule(FrozenClass):
    """abstract class for rules"""

    VERSION = 1

    # cf Methods.Converter.Rule.get_name
    def get_name(self):
        """Return the name of file or function

        Parameters
        ----------
        self : Rule
            A Rule object
        """
        if self.__class__.__name__ == "RuleComplex":
            return self.fct_name
        else:
            return self.file_name

    # cf Methods.Converter.Rule.get_other
    def get_other(self, other_dict, other_path_list, other_unit_dict):
        """Select value in other_dict and change the value to be in SI

        Parameters
        ----------
        self : Rule
            A Rule object
        other_dict : dict
            dict with all other param
        other_path_list : list
            list with path to set value ( ["[Dimensions]", "Pole_Arc"])
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)

        Return
        ----------
        other_value
        """

        unit = other_unit_dict[self.unit_type]

        try:
            # selection correct value in other_dict
            for temp in other_path_list:
                other_dict = other_dict[temp]
        except AttributeError:
            raise ValueError(
                f"Value equivalent at {other_path_list} isn't found in other_dict"
            )

        other_value = other_dict * unit

        return other_value  # return in SI

    # cf Methods.Converter.Rule.get_P
    def get_P(self, path_machine, machine):
        """Select value in machine

        Parameters
        ----------
        self : Rule
            A Rule object
        machine : Machine
            A obj machine
        path_machine : str
            str with the path in obj machine

        Return
        ----------
        P_value
        """
        # select value in object machine
        value_split = path_machine.split(".")

        path = ".".join(value_split[:-1])
        # value_split[-1] is the attribut that we want to retrieve ("W1")
        # path is the attribut chain to get the attribut ("machine.stator.slot")

        try:
            P_value = getattr(
                eval(path),
                value_split[-1],
            )
        except AttributeError:
            raise ValueError(
                f"Value equivalent at {path_machine} isn't found in obj machine"
            )

        return P_value

    # cf Methods.Converter.Rule.set_other
    def set_other(self, other_dict, P_value, other_unit_dict, path_list):
        """Set P_value value in other_dict

        Parameters
        ----------
        self : Rule
            A Rule object
        other_dict : dict
            dict created from the file to be converted
        P_value :
            value to set in other_dict
        other_unit_dict : dict
            dict with unit to make conversion (key: unit family, value: factor)
        path_list : list
            list with path to set the value


        Return
        ----------
        other_dict
        """
        unit = other_unit_dict[self.unit_type]

        P_value = P_value / unit  # set in correct unit

        # Make sure that all the sub-keys exist
        dict_temp = other_dict
        for key in path_list[:-1]:
            if key not in dict_temp:
                dict_temp[key] = dict()
            dict_temp = dict_temp[key]

        # Set the value
        last_key = path_list[-1]
        dict_temp[last_key] = P_value

        return other_dict

    # cf Methods.Converter.Rule.set_P
    def set_P(self, machine, other_value, path):
        """Set value in machine

        Parameters
        ----------
        self : Rule
            A Rule object
        machine : Machine
            A pyleecan machine
        other_value :
            value to set in other_dict
        path : str
            path to set the value


        Return
        ----------
        machine
        """
        # set value in object machine
        value_split = path.split(".")

        # value_split[-1] is the attribut that we want to set ("W1")
        # path is the attribut chain to set the attribut ("machine.stator.slot")
        path = ".".join(value_split[:-1])

        setattr(
            eval(path),
            value_split[-1],
            other_value,
        )
        return machine

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, unit_type="m", init_dict=None, init_str=None):
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
            if "unit_type" in list(init_dict.keys()):
                unit_type = init_dict["unit_type"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.unit_type = unit_type

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Rule_str = ""
        if self.parent is None:
            Rule_str += "parent = None " + linesep
        else:
            Rule_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Rule_str += 'unit_type = "' + str(self.unit_type) + '"' + linesep
        return Rule_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.unit_type != self.unit_type:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._unit_type != self._unit_type:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._unit_type)
                    + ", other="
                    + str(other._unit_type)
                    + ")"
                )
                diff_list.append(name + ".unit_type" + val_str)
            else:
                diff_list.append(name + ".unit_type")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.unit_type)
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

        Rule_dict = dict()
        Rule_dict["unit_type"] = self.unit_type
        # The class name is added to the dict for deserialisation purpose
        Rule_dict["__class__"] = "Rule"
        return Rule_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        unit_type_val = self.unit_type
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(unit_type=unit_type_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.unit_type = None

    def _get_unit_type(self):
        """getter of unit_type"""
        return self._unit_type

    def _set_unit_type(self, value):
        """setter of unit_type"""
        check_var("unit_type", value, "str")
        self._unit_type = value

    unit_type = property(
        fget=_get_unit_type,
        fset=_set_unit_type,
        doc="""unit

        :Type: str
        """,
    )
