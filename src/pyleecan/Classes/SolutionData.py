# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Mesh/SolutionData.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Mesh/SolutionData
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
from .Solution import Solution

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from .Data1D import Data1D

from numpy import isnan
from ._check import InitUnKnowClassError


class SolutionData(Solution):
    """Define a Solution with SciDataTool objects."""

    VERSION = 1

    # cf Methods.Mesh.SolutionData.get_axes_list
    def get_axes_list(self, *args):
        """Get the axis of variables stored in Solution.

        Parameters
        ----------
        self : SolutionData
            an SolutionData object
        args : list
            list of SciDataTool arguments

        Returns
        -------
        field: array
            an array of field values

        """

        # Build axis list
        ax_name = list()
        ax_size = list()

        axes = self.field.get_axes()

        ax_name_orig = [axis.name for axis in axes]

        if len(args) == 0:
            for axis in axes:
                ax_name.append(axis.name)
                ax_size.append(axis.get_length())
        else:
            for arg in args:
                # TODO: fill missing SciDataTool syntax to return proper axis size
                if "[" in arg:
                    # Periodicities / slicing
                    arg_split = arg.split("[")
                    ax_name.append(arg_split[0])
                    ind_ax = ax_name_orig.index(ax_name[-1])
                    if "smallest" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_smallestperiod=True))
                    elif "one" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_oneperiod=True))
                    elif "anti" in arg_split[1]:
                        ax_size.append(axes[ind_ax].get_length(is_antiperiod=True))
                    else:
                        ax_size.append(len(eval(arg.split(ax_name[-1])[-1])))
                elif "=" in arg:
                    # ignore axis
                    pass
                elif "freqs" in arg and "time" in ax_name_orig:
                    # FFT
                    ax_name.append("freqs")
                    ind_ax = ax_name_orig.index("time")
                    Nt_per = axes[ind_ax].get_length(is_oneperiod=True)
                    if Nt_per % 2 == 0:
                        Nfreq = int(Nt_per / 2) + 1
                    else:
                        Nfreq = int((Nt_per - 1) / 2)
                    ax_size.append(Nfreq)
                else:
                    # No operation requested
                    ax_name.append(arg)
                    ind_ax = ax_name_orig.index(ax_name[-1])
                    ax_size.append(axes[ind_ax].get_length())

        return ax_name, ax_size

    # cf Methods.Mesh.SolutionData.get_field
    def get_field(self, *args, is_squeeze=False, node=None, is_rthetaz=False):
        """Get the value of variables stored in Solution.

        Parameters
        ----------
        self : SolutionData
            an SolutionData object
        *args: list of strings
            List of axes requested by the user, their units and values (optional)

        Returns
        -------
        field: array
            an array of field values

        """
        axname, _ = self.get_axes_list()
        symbol = self.field.symbol

        if len(args) == 0:
            field_dict = self.field.get_along(tuple(axname), is_squeeze=is_squeeze)
        else:
            field_dict = self.field.get_along(*args, is_squeeze=is_squeeze)

        field = field_dict[symbol]

        return field

    # cf Methods.Mesh.SolutionData.get_solution
    def get_solution(self, indice=None):
        """Return a copy of the solution with the option to only include specified indice.

        Parameters
        ----------
        self : SolutionData
            a SolutionData object
        indice : list
            list of indice, if list is empty or None all indice are included

        Returns
        -------
        solution: SolutionMat
            solution

        """
        logger = self.get_logger()

        # create copy to directly manipulate data
        solution = self.copy()

        if indice:
            axes = solution.field.axes
            axes_names = solution.get_axes_list()[0]
            ax_idx = axes_names.index("indice")

            org_indice = axes[ax_idx].get_values()

            if set(indice) - set(org_indice):
                logger.warning(
                    "At least one input indice is not part of the solution. "
                    + "Respective indice will be skipped."
                )

            # skip indice that are not part of the solution
            new_indice = [ii for ii in indice if ii in org_indice]

            # create requested axes list to get field values (see SciDataTool slicing ref.)
            args = [
                name + "[smallestperiod]" if name != "indice" else name
                for name in axes_names
            ]
            args[ax_idx] += "=axis_data"

            # get the field values
            field_dict = solution.field.get_along(
                *args, axis_data={"indice": new_indice}
            )

            # set new indice axis
            axes[ax_idx] = Data1D(
                values=new_indice,
                is_components=axes[ax_idx].is_components,
                symmetries=axes[ax_idx].symmetries,
                symbol=axes[ax_idx].symbol,
                name=axes[ax_idx].name,
                unit=axes[ax_idx].unit,
                normalizations=axes[ax_idx].normalizations,
            )

            # set new field data
            solution.field.values = field_dict[self.field.symbol]

        return solution

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        field=None,
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
        # Call Solution init
        super(SolutionData, self).__init__(
            type_element=type_element, label=label, dimension=dimension, unit=unit
        )
        # The class is frozen (in Solution init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        SolutionData_str = ""
        # Get the properties inherited from Solution
        SolutionData_str += super(SolutionData, self).__str__()
        if self.field is not None:
            tmp = self.field.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            SolutionData_str += "field = " + tmp
        else:
            SolutionData_str += "field = None" + linesep + linesep
        return SolutionData_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Solution
        if not super(SolutionData, self).__eq__(other):
            return False
        if other.field != self.field:
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
            super(SolutionData, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.field is None and self.field is not None) or (
            other.field is not None and self.field is None
        ):
            diff_list.append(name + ".field None mismatch")
        elif self.field is not None:
            diff_list.extend(
                self.field.compare(
                    other.field,
                    name=name + ".field",
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

        # Get size of the properties inherited from Solution
        S += super(SolutionData, self).__sizeof__()
        S += getsizeof(self.field)
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
        SolutionData_dict = super(SolutionData, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.field is None:
            SolutionData_dict["field"] = None
        else:
            SolutionData_dict["field"] = self.field.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        SolutionData_dict["__class__"] = "SolutionData"
        return SolutionData_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.field is None:
            field_val = None
        else:
            field_val = self.field.copy()
        type_element_val = self.type_element
        label_val = self.label
        dimension_val = self.dimension
        unit_val = self.unit
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            field=field_val,
            type_element=type_element_val,
            label=label_val,
            dimension=dimension_val,
            unit=unit_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.field is not None:
            self.field._set_None()
        # Set to None the properties inherited from Solution
        super(SolutionData, self)._set_None()

    def _get_field(self):
        """getter of field"""
        return self._field

    def _set_field(self, value):
        """setter of field"""
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
                "pyleecan.Classes", value.get("__class__"), "field"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            DataND = import_class("pyleecan.Classes", "DataND", "field")
            value = DataND()
        check_var("field", value, "DataND")
        self._field = value

        if self._field is not None:
            self._field.parent = self

    field = property(
        fget=_get_field,
        fset=_set_field,
        doc="""Data object containing the numerical values of a solution. One of the axis must be "Indices", a list of indices. If the solution is a vector, one of the axis must be "Direction", values ['x','y'] for example.

        :Type: DataND
        """,
    )
