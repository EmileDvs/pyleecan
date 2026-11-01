# File generated according to Generator/ClassesRef/SciDataTool/Norm_vector.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/Norm_vector"""

from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.Normalization import Normalization
from pyleecan.Classes._check import check_var

from pyleecan.Functions.SciDataTool import NormError
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Norm_vector(Normalization):
    """Normalization by a given vector"""

    VERSION = 1

    # cf Methods.SciDataTool.Norm_vector.normalize
    def normalize(
        self,
        values,
    ):
        """Normalizes axis values
        Parameters
        ----------
        self: Norm_vector
            a Norm_vector object
        values: ndarray
            axis values
        Returns
        -------
        Vector of axis values
        """
        if len(values) != len(self.vector):
            raise NormError(
                "Normalization vector is not the same length as axis, cannot normalize"
            )
        else:
            return self.vector

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, vector=None, unit="SI", init_dict=None, init_str=None):
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
            if "vector" in list(init_dict.keys()):
                vector = init_dict["vector"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
        # Set the properties (value check and convertion are done in setter)
        self.vector = vector
        # Call Normalization init
        super(Norm_vector, self).__init__(unit=unit)
        # The class is frozen (in Normalization init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Norm_vector_str = ""
        # Get the properties inherited from Normalization
        Norm_vector_str += super(Norm_vector, self).__str__()
        Norm_vector_str += (
            "vector = "
            + linesep
            + str(self.vector).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        return Norm_vector_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Normalization
        if not super(Norm_vector, self).__eq__(other):
            return False
        if not np.array_equal(other.vector, self.vector):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Normalization
        diff_list.extend(
            super(Norm_vector, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if not np.array_equal(other.vector, self.vector):
            diff_list.append(name + ".vector")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Normalization
        S += super(Norm_vector, self).__sizeof__()
        S += getsizeof(self.vector)
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

        # Get the properties inherited from Normalization
        Norm_vector_dict = super(Norm_vector, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.vector is None:
            Norm_vector_dict["vector"] = None
        else:
            if type_handle_ndarray == 0:
                Norm_vector_dict["vector"] = self.vector.tolist()
            elif type_handle_ndarray == 1:
                Norm_vector_dict["vector"] = self.vector.copy()
            elif type_handle_ndarray == 2:
                Norm_vector_dict["vector"] = self.vector
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Norm_vector_dict["__class__"] = "Norm_vector"
        return Norm_vector_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.vector is None:
            vector_val = None
        else:
            vector_val = self.vector.copy()
        unit_val = self.unit
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(vector=vector_val, unit=unit_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.vector = None
        # Set to None the properties inherited from Normalization
        super(Norm_vector, self)._set_None()

    def _get_vector(self):
        """getter of vector"""
        return self._vector

    def _set_vector(self, value):
        """setter of vector"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("vector", value, "ndarray")
        self._vector = value

    vector = property(
        fget=_get_vector,
        fset=_set_vector,
        doc="""vector to replace axis values

        :Type: ndarray
        """,
    )
