# File generated according to Generator/ClassesRef/Machine/Notch.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Notch"""

from os import linesep
from sys import getsizeof

from pyleecan.Classes import ParentMissingError
from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass

from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Notch(FrozenClass):

    VERSION = 1

    # cf Methods.Machine.Notch.get_label
    def get_label(self, is_add_id=True):
        """Return the label of the lamination (Stator-0 for instance)

        Parameters
        ----------
        self : Notch
            a Notch object
        is_add_id : bool
            True to add the "-X" part

        Returns
        -------
        label : str
            Label of the lamination

        """

        if self.parent is not None:
            return self.parent.get_label()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # cf Methods.Machine.Notch.get_Rbo
    def get_Rbo(self):
        """Return the parent lamination bore radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        Rbo: float
            The parent lamination bore radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Rbo()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # cf Methods.Machine.Notch.get_Ryoke
    def get_Ryoke(self):
        """Return the parent lamination yoke radius
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        Ryoke: float
            The parent lamination yoke radius [m]

        """

        if self.parent is not None:
            return self.parent.get_Ryoke()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # cf Methods.Machine.Notch.has_key
    def has_key(self):
        """Check if a there is key in the notch

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        has_key : bool
            True if the notch has a key
        """

        return self.key_mat is not None

    # cf Methods.Machine.Notch.is_outwards
    def is_outwards(self):
        """Return if the notch is outwards (on an external lamination) or inwards
        (on an internal lamination).
        (to make lam.notch[ii].notch_shape match lam.slot parent)

        Parameters
        ----------
        self : Notch
            A Notch object

        Returns
        -------
        is_outwards: bool
            True if the Lamination is not internal and false if not. For yoke notch,
            result is negated.
        """
        if self.parent is not None:
            return self.parent.is_outwards()
        else:
            raise ParentMissingError("Error: The notch is not inside a Lamination")

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, key_mat=None, init_dict=None, init_str=None):
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
            if "key_mat" in list(init_dict.keys()):
                key_mat = init_dict["key_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.key_mat = key_mat

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Notch_str = ""
        if self.parent is None:
            Notch_str += "parent = None " + linesep
        else:
            Notch_str += "parent = " + str(type(self.parent)) + " object" + linesep
        if self.key_mat is not None:
            tmp = self.key_mat.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Notch_str += "key_mat = " + tmp
        else:
            Notch_str += "key_mat = None" + linesep + linesep
        return Notch_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.key_mat != self.key_mat:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (other.key_mat is None and self.key_mat is not None) or (
            other.key_mat is not None and self.key_mat is None
        ):
            diff_list.append(name + ".key_mat None mismatch")
        elif self.key_mat is not None:
            diff_list.extend(
                self.key_mat.compare(
                    other.key_mat,
                    name=name + ".key_mat",
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
        S += getsizeof(self.key_mat)
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

        Notch_dict = dict()
        if self.key_mat is None:
            Notch_dict["key_mat"] = None
        else:
            Notch_dict["key_mat"] = self.key_mat.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        Notch_dict["__class__"] = "Notch"
        return Notch_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.key_mat is None:
            key_mat_val = None
        else:
            key_mat_val = self.key_mat.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(key_mat=key_mat_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.key_mat is not None:
            self.key_mat._set_None()

    def _get_key_mat(self):
        """getter of key_mat"""
        return self._key_mat

    def _set_key_mat(self, value):
        """setter of key_mat"""
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
                "pyleecan.Classes", value.get("__class__"), "key_mat"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "key_mat")
            value = Material()
        check_var("key_mat", value, "Material")
        self._key_mat = value

        if self._key_mat is not None:
            self._key_mat.parent = self

    key_mat = property(
        fget=_get_key_mat,
        fset=_set_key_mat,
        doc="""The material of the key (if None, no key to add)

        :Type: Material
        """,
    )
