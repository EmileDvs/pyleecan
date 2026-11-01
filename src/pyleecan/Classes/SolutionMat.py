# File generated according to Generator/ClassesRef/Mesh/SolutionMat.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/SolutionMat"""

from os import linesep
from sys import getsizeof

import numpy as np

from pyleecan.Classes.Solution import Solution
from pyleecan.Classes._check import check_var

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class SolutionMat(Solution):
    """Define a Solution with ndarray object."""

    VERSION = 1

    # cf Methods.Mesh.SolutionMat.get_axes_list
    def get_axes_list(self, *args):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : SolutionMat
            an SolutionMat object

        Returns
        -------
        axis_dict: list
            a list of axis names containing axis sizes

        """

        if self.axis_name is not None:
            axis_name = self.axis_name.copy()
        else:
            axis_name = None

        if self.axis_size is not None:
            axis_size = self.axis_size.copy()
        else:
            axis_size = None

        return axis_name, axis_size

    # cf Methods.Mesh.SolutionMat.get_field
    def get_field(self, *args, is_squeeze=False, node=None, is_rthetaz=False):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : Solution
            an Solution object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)
        is_squeeze : boolean
            To numpy.squeeze the output ndarray

        Returns
        -------
        field_new: ndarray
            an ndarray of field values sliced according to args.

        """
        if args is None:
            args = dict()
        else:
            if len(args) == 1 and type(args[0]) == tuple:
                args = args[0]

        field_new = self.field.copy()

        if len(args) > 0:
            if self.axis_name is not None:
                nb_axis = len(self.axis_name)
                for i in range(nb_axis):
                    # ax = np.where(np.array(field.shape) == self.axis_size[i])[0][0]
                    ax_name = self.axis_name[i]
                    is_found = False
                    for axis_str in args:
                        if ax_name in axis_str:
                            is_found = True
                            if "[" in axis_str:
                                elems = axis_str.split("[")
                                ind_str = elems[1].strip("]")

                                # Range of indices
                                if ":" in ind_str:
                                    elems2 = ind_str.split(":")
                                    indices = [
                                        i
                                        for i in range(
                                            int(elems2[0]), int(elems2[1]) + 1
                                        )
                                    ]
                                # List of indices
                                elif "," in ind_str:
                                    indices = [int(x) for x in ind_str.split(",")]
                                # Single index
                                else:
                                    indices = [int(ind_str)]

                                field_new = np.take(field_new, indices=indices, axis=i)

                    if not is_found:
                        field_new = np.take(field_new, indices=0, axis=i)
                        field_new = np.expand_dims(field_new, i)

        if is_squeeze:
            field_new = np.squeeze(field_new)

        return field_new

    # cf Methods.Mesh.SolutionMat.get_solution
    def get_solution(self, indice=None):
        """Return a copy of the solution with the option to only include specified indices.

        Parameters
        ----------
        self : SolutionMat
            a SolutionMat object
        indices : list
            list of indices, if list is empty or None all indices are included

        Returns
        -------
        solution: SolutionMat
            solution

        """
        logger = self.get_logger()

        field_sol = self.get_field()
        axis_name, axis_size = self.get_axes_list()
        s_indice = self.indice

        Iindice = axis_name.index("indice")

        # create indices of solution if None
        if s_indice is None:
            s_indice = [i for i in range(field_sol.shape[Iindice])]

        # check input indices
        if not indice:
            indice = s_indice

        if set(indice) - set(s_indice):
            logger.warning(
                "At least one input indice is not part of the solution. "
                + "Respective indice will be skipped."
            )

        # skip indice that are not part of the solution
        new_indice = [ii for ii in indice if ii in s_indice]

        # get array index of new_indice
        array_indice = [np.where(np.array(s_indice) == ii)[0][0] for ii in new_indice]

        # setup requested solution
        axis_size[Iindice] = len(new_indice)
        new_field_sol = np.take(field_sol, array_indice, axis=Iindice)

        solution = type(self)(
            label=self.label,
            type_element=self.type_element,
            field=new_field_sol,
            indice=indice,
            axis_name=axis_name,
            axis_size=axis_size,
            dimension=self.dimension,
        )

        return solution

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        field=None,
        indice=None,
        axis_name=None,
        axis_size=None,
        type_element="triangle",
        label=None,
        dimension=2,
        unit="",
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
            if "field" in list(init_dict.keys()):
                field = init_dict["field"]
            if "indice" in list(init_dict.keys()):
                indice = init_dict["indice"]
            if "axis_name" in list(init_dict.keys()):
                axis_name = init_dict["axis_name"]
            if "axis_size" in list(init_dict.keys()):
                axis_size = init_dict["axis_size"]
            if "type_element" in list(init_dict.keys()):
                type_element = init_dict["type_element"]
            if "label" in list(init_dict.keys()):
                label = init_dict["label"]
            if "dimension" in list(init_dict.keys()):
                dimension = init_dict["dimension"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
        # Set the properties (value check and convertion are done in setter)
        self.field = field
        self.indice = indice
        self.axis_name = axis_name
        self.axis_size = axis_size
        # Call Solution init
        super(SolutionMat, self).__init__(
            type_element=type_element, label=label, dimension=dimension, unit=unit
        )
        # The class is frozen (in Solution init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SolutionMat_str = ""
        # Get the properties inherited from Solution
        SolutionMat_str += super(SolutionMat, self).__str__()
        SolutionMat_str += (
            "field = "
            + linesep
            + str(self.field).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        SolutionMat_str += (
            "indice = "
            + linesep
            + str(self.indice).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        SolutionMat_str += (
            "axis_name = "
            + linesep
            + str(self.axis_name).replace(linesep, linesep + "\t")
            + linesep
        )
        SolutionMat_str += (
            "axis_size = "
            + linesep
            + str(self.axis_size).replace(linesep, linesep + "\t")
            + linesep
        )
        return SolutionMat_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Solution
        if not super(SolutionMat, self).__eq__(other):
            return False
        if not np.array_equal(other.field, self.field):
            return False
        if not np.array_equal(other.indice, self.indice):
            return False
        if other.axis_name != self.axis_name:
            return False
        if other.axis_size != self.axis_size:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Solution
        diff_list.extend(
            super(SolutionMat, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if not np.array_equal(other.field, self.field):
            diff_list.append(name + ".field")
        if not np.array_equal(other.indice, self.indice):
            diff_list.append(name + ".indice")
        if other._axis_name != self._axis_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._axis_name)
                    + ", other="
                    + str(other._axis_name)
                    + ")"
                )
                diff_list.append(name + ".axis_name" + val_str)
            else:
                diff_list.append(name + ".axis_name")
        if other._axis_size != self._axis_size:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._axis_size)
                    + ", other="
                    + str(other._axis_size)
                    + ")"
                )
                diff_list.append(name + ".axis_size" + val_str)
            else:
                diff_list.append(name + ".axis_size")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Solution
        S += super(SolutionMat, self).__sizeof__()
        S += getsizeof(self.field)
        S += getsizeof(self.indice)
        if self.axis_name is not None:
            for value in self.axis_name:
                S += getsizeof(value)
        if self.axis_size is not None:
            for value in self.axis_size:
                S += getsizeof(value)
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

        # Get the properties inherited from Solution
        SolutionMat_dict = super(SolutionMat, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.field is None:
            SolutionMat_dict["field"] = None
        else:
            if type_handle_ndarray == 0:
                SolutionMat_dict["field"] = self.field.tolist()
            elif type_handle_ndarray == 1:
                SolutionMat_dict["field"] = self.field.copy()
            elif type_handle_ndarray == 2:
                SolutionMat_dict["field"] = self.field
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        if self.indice is None:
            SolutionMat_dict["indice"] = None
        else:
            if type_handle_ndarray == 0:
                SolutionMat_dict["indice"] = self.indice.tolist()
            elif type_handle_ndarray == 1:
                SolutionMat_dict["indice"] = self.indice.copy()
            elif type_handle_ndarray == 2:
                SolutionMat_dict["indice"] = self.indice
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        SolutionMat_dict["axis_name"] = (
            self.axis_name.copy() if self.axis_name is not None else None
        )
        SolutionMat_dict["axis_size"] = (
            self.axis_size.copy() if self.axis_size is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SolutionMat_dict["__class__"] = "SolutionMat"
        return SolutionMat_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.field is None:
            field_val = None
        else:
            field_val = self.field.copy()
        if self.indice is None:
            indice_val = None
        else:
            indice_val = self.indice.copy()
        if self.axis_name is None:
            axis_name_val = None
        else:
            axis_name_val = self.axis_name.copy()
        if self.axis_size is None:
            axis_size_val = None
        else:
            axis_size_val = self.axis_size.copy()
        type_element_val = self.type_element
        label_val = self.label
        dimension_val = self.dimension
        unit_val = self.unit
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            field=field_val,
            indice=indice_val,
            axis_name=axis_name_val,
            axis_size=axis_size_val,
            type_element=type_element_val,
            label=label_val,
            dimension=dimension_val,
            unit=unit_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.field = None
        self.indice = None
        self.axis_name = None
        self.axis_size = None
        # Set to None the properties inherited from Solution
        super(SolutionMat, self)._set_None()

    def _get_field(self):
        """getter of field"""
        return self._field

    def _set_field(self, value):
        """setter of field"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("field", value, "ndarray")
        self._field = value

    field = property(
        fget=_get_field,
        fset=_set_field,
        doc="""Matrix/Vector of the numerical values of the solutions.

        :Type: ndarray
        """,
    )

    def _get_indice(self):
        """getter of indice"""
        return self._indice

    def _set_indice(self, value):
        """setter of indice"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("indice", value, "ndarray")
        self._indice = value

    indice = property(
        fget=_get_indice,
        fset=_set_indice,
        doc="""Indices of loaded elements. Set to None if all elements are loaded

        :Type: ndarray
        """,
    )

    def _get_axis_name(self):
        """getter of axis_name"""
        return self._axis_name

    def _set_axis_name(self, value):
        """setter of axis_name"""
        if type(value) is int and value == -1:
            value = list()
        check_var("axis_name", value, "list")
        self._axis_name = value

    axis_name = property(
        fget=_get_axis_name,
        fset=_set_axis_name,
        doc="""List of axis names (e.g. "time", "direction")

        :Type: list
        """,
    )

    def _get_axis_size(self):
        """getter of axis_size"""
        return self._axis_size

    def _set_axis_size(self, value):
        """setter of axis_size"""
        if type(value) is int and value == -1:
            value = list()
        check_var("axis_size", value, "list")
        self._axis_size = value

    axis_size = property(
        fget=_get_axis_size,
        fset=_set_axis_size,
        doc="""List of axis sizes

        :Type: list
        """,
    )
