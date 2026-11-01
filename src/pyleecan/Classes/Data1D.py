# File generated according to Generator/ClassesRef/SciDataTool/Data1D.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/Data1D"""

from importlib import import_module
from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.Norm_vector import Norm_vector

from pyleecan.Classes._check import check_var
from pyleecan.Classes.Data import Data
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save
from pyleecan.Functions.SciDataTool import AxisError, NormError
from pyleecan.Functions.SciDataTool.conversions import convert
from pyleecan.Functions.SciDataTool.symmetries import rebuild_symmetries_axis


class Data1D(Data):
    """Class for axes defined as vectors"""

    VERSION = 1

    # cf Methods.SciDataTool.Data1D.check_filter
    def check_filter(self):
        """Check if filter is correctly defined
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        keys: list
            list of filter keys in same order as in values
        """
        keys = []
        for i, value in enumerate(self.values):
            items = value.split(self.delimiter)
            if len(items) != len(self.filter.keys()):
                raise AxisError("Filter is not correctly defined")
            for item in items:
                is_match = False
                for key in self.filter:
                    if item in self.filter[key]:
                        is_match = True
                        if i == 0:
                            keys.append(key)
                if not is_match:
                    raise AxisError("Missing item in filter: " + item)

        return keys

    # cf Methods.SciDataTool.Data1D.get_axis_periodic
    def get_axis_periodic(self, Nper, is_aper=False):
        """Returns the vector 'axis' taking symmetries into account.

        Parameters
        ----------
        self: Data1D
            a Data1D object
        Nper: int
            number of periods
        is_aper: bool
            return values on a semi period (only for antiperiodic signals)

        Returns
        -------
        New_axis: Data1D
            Axis with requested (anti-)periodicities
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.Data1D", fromlist=["Data1D"])
        Data1D = module.Data1D

        try:
            # Reduce axis to the given periodicity
            Nper = Nper * 2 if is_aper else Nper
            values = self.values
            N = self.get_length()

            if N % Nper != 0:
                raise AxisError(
                    "length of axis is not divisible by the number of periods"
                )
            values_per = values[: int(N / Nper)]
            for norm in self.normalizations.values():
                if isinstance(norm, Norm_vector):
                    norm.vector = norm.vector[: int(N / Nper)]

            if is_aper:
                sym = "antiperiod"
            else:
                sym = "period"

            if Nper == 1 and sym == "period":
                symmetries = dict()
            else:
                symmetries = {sym: Nper}

            New_axis = Data1D(
                values=values_per,
                name=self.name,
                unit=self.unit,
                symmetries=symmetries,
                normalizations=self.normalizations,
                is_components=self.is_components,
                symbol=self.symbol,
            )

        except AxisError:
            # Periodicity cannot be applied, return full axis
            New_axis = self.copy()

        return New_axis

    # cf Methods.SciDataTool.Data1D.get_filter
    def get_filter(self, filter_dict):
        """Get filtering indices
        Parameters
        ----------
        self: Data1D
            a Data1D object
        filter_dict: dict
            a dict of the values to filter (keep values defined in filter_dict)
        Returns
        -------
        indices: list
            list of indices to use to get corresponding filter
        """

        # Check that keys in filter_dict are correctly defined in self.filter
        if len(filter_dict.keys()) != len(self.filter.keys()):
            raise AxisError("Filter key not defined in Data1D.filter")
        for key in filter_dict:
            if key not in self.filter:
                raise AxisError("Filter key not defined in Data1D.filter")

        # Prepare filtering keys in correct order
        keys = self.check_filter()

        indices = []
        for i, value in enumerate(self.values):
            items = value.split(self.delimiter)
            nb_match = 0
            for j, item in enumerate(items):
                if item in filter_dict[keys[j]]:
                    nb_match += 1
            if nb_match == len(keys):
                indices.append(i)

        return indices

    # cf Methods.SciDataTool.Data1D.get_length
    def get_length(
        self, is_oneperiod=False, is_antiperiod=False, is_smallestperiod=False
    ):
        """Returns the length of the axis taking symmetries into account.
        Parameters
        ----------
        self: Data1D
            a Data1D object
        is_oneperiod: bool
            return values on a single period
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)
        Returns
        -------
        Length of axis
        """
        N = len(self.values)
        # Rebuild symmetries
        if is_smallestperiod:
            return N
        elif is_antiperiod:
            if "antiperiod" in self.symmetries:
                return N
            else:
                raise AxisError("axis has no antiperiodicity")
        elif is_oneperiod:
            if "antiperiod" in self.symmetries:
                return N * 2
            elif "period" in self.symmetries:
                return N
            else:
                return N
        else:
            if "antiperiod" in self.symmetries:
                return N * self.symmetries["antiperiod"]
            elif "period" in self.symmetries:
                return N * self.symmetries["period"]
            else:
                return N

    # cf Methods.SciDataTool.Data1D.get_periodicity
    def get_periodicity(self):
        """Gives periodicity of the axis.
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        per, is_antiper
        """

        per = 1
        is_antiper = False

        if "antiperiod" in self.symmetries:
            if self.symmetries["antiperiod"] > 1:
                per = self.symmetries["antiperiod"]
                is_antiper = True
        elif "period" in self.symmetries:
            if self.symmetries["period"] > 1:
                per = self.symmetries["period"]

        return (per, is_antiper)

    # cf Methods.SciDataTool.Data1D.get_values
    def get_values(
        self,
        unit="SI",
        is_oneperiod=False,
        is_antiperiod=False,
        is_smallestperiod=False,
        normalization=None,
        operation=None,
        is_real=True,
        corr_unit=None,
        is_full=False,
    ):
        """Returns the vector 'axis' taking symmetries into account.
        Parameters
        ----------
        self: Data1D
            a Data1D object
        unit: str
            requested unit
        is_oneperiod: bool
            return values on a single period
        is_antiperiod: bool
            return values on a semi period (only for antiperiodic signals)
        is_smallestperiod: bool
            return values on smallest available period
        normalization: str
            name of normalization to use
        operation: str
            name of the operation (e.g. "freqs_to_time")

        Returns
        -------
        Vector of axis values
        """
        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.Norm_vector", fromlist=["Norm_vector"])
        Norm_vector = module.Norm_vector

        if unit != "SI" and unit != self.unit:
            if unit in self.normalizations and normalization is None:
                normalization = unit
                unit = "SI"

        values = self.values
        norm_vector = None

        # Ignore symmetries if fft axis
        if self.name == "freqs" or self.name == "wavenumber":
            is_smallestperiod = True

        # Rebuild symmetries
        if is_smallestperiod:
            pass
        elif is_antiperiod:
            if "antiperiod" in self.symmetries:
                pass
            else:
                raise AxisError("axis has no antiperiodicity")
        elif is_oneperiod:
            if "antiperiod" in self.symmetries:
                nper = self.symmetries["antiperiod"]
                self.symmetries["antiperiod"] = 2
                values = rebuild_symmetries_axis(values, self.symmetries)
                self.symmetries["antiperiod"] = nper
            elif "period" in self.symmetries:
                pass
            else:
                pass
        else:
            values = rebuild_symmetries_axis(values, self.symmetries)
            if (
                normalization is not None
                and normalization in self.normalizations
                and isinstance(self.normalizations[normalization], Norm_vector)
            ):
                norm_vector = self.normalizations[normalization].vector.copy()
                self.normalizations[normalization].vector = rebuild_symmetries_axis(
                    norm_vector, self.symmetries
                )

        # fft/ifft
        if operation is not None:
            module = import_module("pyleecan.Functions.SciDataTool.conversions")
            func = getattr(module, operation)  # Conversion function
            values = np.array(func(values, is_real=is_real))
            if is_full and (self.name == "freqs" or self.name == "wavenumber"):
                if "period" in self.symmetries:
                    if self.name != "time":
                        values = values * self.symmetries["period"]
                elif "antiperiod" in self.symmetries:
                    if self.name != "time":
                        values = values * self.symmetries["antiperiod"] / 2

        # Normalization
        if normalization is not None:
            if normalization in self.normalizations:
                if (
                    self.normalizations[normalization].unit == "SI"
                    or self.normalizations[normalization].unit == self.unit
                ):
                    # Axis is in the correct unit for the normalization
                    values = self.normalizations[normalization].normalize(values)
                else:
                    raise NormError("Normalization is not available in this unit")
            else:
                raise NormError("Normalization is not available")

        # Unit conversion
        if unit != "SI" and unit != self.unit:
            if corr_unit is not None:
                values = convert(values, corr_unit, unit)
            else:
                values = convert(values, self.unit, unit)

        if norm_vector is not None:
            self.normalizations[normalization].vector = norm_vector

        return values

    # cf Methods.SciDataTool.Data1D.has_period
    def has_period(self):
        """Indicates if an axis has symmetries.
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        Boolean
        """
        answer = False

        if "antiperiod" in self.symmetries:
            if self.symmetries["antiperiod"] > 1:
                answer = True
        elif "period" in self.symmetries:
            if self.symmetries["period"] > 1:
                answer = True

        return answer

    # cf Methods.SciDataTool.Data1D.to_linspace
    def to_linspace(self):
        """Tests if values are a linspace and returns a DataLinspace (or Data1D if not possible)
        Parameters
        ----------
        self: Data1D
            a Data1D object
        Returns
        -------
        DataLinspace or Data1D
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.DataLinspace", fromlist=["DataLinspace"])
        DataLinspace = module.DataLinspace

        values = self.values
        number = values.size

        if (
            number > 1
            and values.dtype.kind not in {"U", "S"}
            and np.allclose(
                values,
                np.linspace(values[0], values[-1], number, endpoint=True),
                rtol=1e-5,
                atol=1e-8,
                equal_nan=False,
            )
        ):
            New_axis = DataLinspace(
                initial=values[0],
                final=values[-1],
                number=number,
                include_endpoint=True,
                name=self.name,
                unit=self.unit,
                symmetries=self.symmetries,
                normalizations=self.normalizations.copy(),
                is_components=self.is_components,
                symbol=self.symbol,
            )
        else:
            New_axis = self.copy()

        return New_axis

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        values=None,
        is_components=False,
        symmetries=-1,
        is_overlay=False,
        delimiter=None,
        sort_indices=None,
        filter=None,
        char_to_rm=None,
        symbol="",
        name="",
        unit="",
        normalizations=-1,
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
            if "values" in list(init_dict.keys()):
                values = init_dict["values"]
            if "is_components" in list(init_dict.keys()):
                is_components = init_dict["is_components"]
            if "symmetries" in list(init_dict.keys()):
                symmetries = init_dict["symmetries"]
            if "is_overlay" in list(init_dict.keys()):
                is_overlay = init_dict["is_overlay"]
            if "delimiter" in list(init_dict.keys()):
                delimiter = init_dict["delimiter"]
            if "sort_indices" in list(init_dict.keys()):
                sort_indices = init_dict["sort_indices"]
            if "filter" in list(init_dict.keys()):
                filter = init_dict["filter"]
            if "char_to_rm" in list(init_dict.keys()):
                char_to_rm = init_dict["char_to_rm"]
            if "symbol" in list(init_dict.keys()):
                symbol = init_dict["symbol"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
            if "normalizations" in list(init_dict.keys()):
                normalizations = init_dict["normalizations"]
        # Set the properties (value check and convertion are done in setter)
        self.values = values
        self.is_components = is_components
        self.symmetries = symmetries
        self.is_overlay = is_overlay
        self.delimiter = delimiter
        self.sort_indices = sort_indices
        self.filter = filter
        self.char_to_rm = char_to_rm
        # Call Data init
        super(Data1D, self).__init__(
            symbol=symbol, name=name, unit=unit, normalizations=normalizations
        )
        # The class is frozen (in Data init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Data1D_str = ""
        # Get the properties inherited from Data
        Data1D_str += super(Data1D, self).__str__()
        Data1D_str += (
            "values = "
            + linesep
            + str(self.values).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        Data1D_str += "is_components = " + str(self.is_components) + linesep
        Data1D_str += "symmetries = " + str(self.symmetries) + linesep
        Data1D_str += "is_overlay = " + str(self.is_overlay) + linesep
        Data1D_str += 'delimiter = "' + str(self.delimiter) + '"' + linesep
        Data1D_str += (
            "sort_indices = "
            + linesep
            + str(self.sort_indices).replace(linesep, linesep + "\t")
            + linesep
        )
        Data1D_str += "filter = " + str(self.filter) + linesep
        Data1D_str += (
            "char_to_rm = "
            + linesep
            + str(self.char_to_rm).replace(linesep, linesep + "\t")
            + linesep
        )
        return Data1D_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Data
        if not super(Data1D, self).__eq__(other):
            return False
        if not np.array_equal(other.values, self.values):
            return False
        if other.is_components != self.is_components:
            return False
        if other.symmetries != self.symmetries:
            return False
        if other.is_overlay != self.is_overlay:
            return False
        if other.delimiter != self.delimiter:
            return False
        if other.sort_indices != self.sort_indices:
            return False
        if other.filter != self.filter:
            return False
        if other.char_to_rm != self.char_to_rm:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Data
        diff_list.extend(
            super(Data1D, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if not np.array_equal(other.values, self.values):
            diff_list.append(name + ".values")
        if other._is_components != self._is_components:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_components)
                    + ", other="
                    + str(other._is_components)
                    + ")"
                )
                diff_list.append(name + ".is_components" + val_str)
            else:
                diff_list.append(name + ".is_components")
        if other._symmetries != self._symmetries:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._symmetries)
                    + ", other="
                    + str(other._symmetries)
                    + ")"
                )
                diff_list.append(name + ".symmetries" + val_str)
            else:
                diff_list.append(name + ".symmetries")
        if other._is_overlay != self._is_overlay:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_overlay)
                    + ", other="
                    + str(other._is_overlay)
                    + ")"
                )
                diff_list.append(name + ".is_overlay" + val_str)
            else:
                diff_list.append(name + ".is_overlay")
        if other._delimiter != self._delimiter:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._delimiter)
                    + ", other="
                    + str(other._delimiter)
                    + ")"
                )
                diff_list.append(name + ".delimiter" + val_str)
            else:
                diff_list.append(name + ".delimiter")
        if other._sort_indices != self._sort_indices:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._sort_indices)
                    + ", other="
                    + str(other._sort_indices)
                    + ")"
                )
                diff_list.append(name + ".sort_indices" + val_str)
            else:
                diff_list.append(name + ".sort_indices")
        if other._filter != self._filter:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._filter)
                    + ", other="
                    + str(other._filter)
                    + ")"
                )
                diff_list.append(name + ".filter" + val_str)
            else:
                diff_list.append(name + ".filter")
        if other._char_to_rm != self._char_to_rm:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._char_to_rm)
                    + ", other="
                    + str(other._char_to_rm)
                    + ")"
                )
                diff_list.append(name + ".char_to_rm" + val_str)
            else:
                diff_list.append(name + ".char_to_rm")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Data
        S += super(Data1D, self).__sizeof__()
        S += getsizeof(self.values)
        S += getsizeof(self.is_components)
        if self.symmetries is not None:
            for key, value in self.symmetries.items():
                S += getsizeof(value) + getsizeof(key)
        S += getsizeof(self.is_overlay)
        S += getsizeof(self.delimiter)
        if self.sort_indices is not None:
            for value in self.sort_indices:
                S += getsizeof(value)
        if self.filter is not None:
            for key, value in self.filter.items():
                S += getsizeof(value) + getsizeof(key)
        if self.char_to_rm is not None:
            for value in self.char_to_rm:
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

        # Get the properties inherited from Data
        Data1D_dict = super(Data1D, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.values is None:
            Data1D_dict["values"] = None
        else:
            if type_handle_ndarray == 0:
                Data1D_dict["values"] = self.values.tolist()
            elif type_handle_ndarray == 1:
                Data1D_dict["values"] = self.values.copy()
            elif type_handle_ndarray == 2:
                Data1D_dict["values"] = self.values
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        Data1D_dict["is_components"] = self.is_components
        Data1D_dict["symmetries"] = (
            self.symmetries.copy() if self.symmetries is not None else None
        )
        Data1D_dict["is_overlay"] = self.is_overlay
        Data1D_dict["delimiter"] = self.delimiter
        Data1D_dict["sort_indices"] = (
            self.sort_indices.copy() if self.sort_indices is not None else None
        )
        Data1D_dict["filter"] = self.filter.copy() if self.filter is not None else None
        Data1D_dict["char_to_rm"] = (
            self.char_to_rm.copy() if self.char_to_rm is not None else None
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Data1D_dict["__class__"] = "Data1D"
        return Data1D_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.values is None:
            values_val = None
        else:
            values_val = self.values.copy()
        is_components_val = self.is_components
        if self.symmetries is None:
            symmetries_val = None
        else:
            symmetries_val = self.symmetries.copy()
        is_overlay_val = self.is_overlay
        delimiter_val = self.delimiter
        if self.sort_indices is None:
            sort_indices_val = None
        else:
            sort_indices_val = self.sort_indices.copy()
        if self.filter is None:
            filter_val = None
        else:
            filter_val = self.filter.copy()
        if self.char_to_rm is None:
            char_to_rm_val = None
        else:
            char_to_rm_val = self.char_to_rm.copy()
        symbol_val = self.symbol
        name_val = self.name
        unit_val = self.unit
        if self.normalizations is None:
            normalizations_val = None
        else:
            normalizations_val = dict()
            for key, obj in self.normalizations.items():
                normalizations_val[key] = obj.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            values=values_val,
            is_components=is_components_val,
            symmetries=symmetries_val,
            is_overlay=is_overlay_val,
            delimiter=delimiter_val,
            sort_indices=sort_indices_val,
            filter=filter_val,
            char_to_rm=char_to_rm_val,
            symbol=symbol_val,
            name=name_val,
            unit=unit_val,
            normalizations=normalizations_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.values = None
        self.is_components = None
        self.symmetries = None
        self.is_overlay = None
        self.delimiter = None
        self.sort_indices = None
        self.filter = None
        self.char_to_rm = None
        # Set to None the properties inherited from Data
        super(Data1D, self)._set_None()

    def _get_values(self):
        """getter of values"""
        return self._values

    def _set_values(self, value):
        """setter of values"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("values", value, "ndarray")
        self._values = value

    values = property(
        fget=_get_values,
        fset=_set_values,
        doc="""List or ndarray of the axis values

        :Type: ndarray
        """,
    )

    def _get_is_components(self):
        """getter of is_components"""
        return self._is_components

    def _set_is_components(self, value):
        """setter of is_components"""
        check_var("is_components", value, "bool")
        self._is_components = value

    is_components = property(
        fget=_get_is_components,
        fset=_set_is_components,
        doc="""True if the axis values are strings

        :Type: bool
        """,
    )

    def _get_symmetries(self):
        """getter of symmetries"""
        return self._symmetries

    def _set_symmetries(self, value):
        """setter of symmetries"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("symmetries", value, "dict")
        self._symmetries = value

    symmetries = property(
        fget=_get_symmetries,
        fset=_set_symmetries,
        doc="""Dictionary of the symmetries along each axis, used to reduce storage

        :Type: dict
        """,
    )

    def _get_is_overlay(self):
        """getter of is_overlay"""
        return self._is_overlay

    def _set_is_overlay(self, value):
        """setter of is_overlay"""
        check_var("is_overlay", value, "bool")
        self._is_overlay = value

    is_overlay = property(
        fget=_get_is_overlay,
        fset=_set_is_overlay,
        doc="""True if axis must be used to overlay curves in plots

        :Type: bool
        """,
    )

    def _get_delimiter(self):
        """getter of delimiter"""
        return self._delimiter

    def _set_delimiter(self, value):
        """setter of delimiter"""
        check_var("delimiter", value, "str")
        self._delimiter = value

    delimiter = property(
        fget=_get_delimiter,
        fset=_set_delimiter,
        doc="""Character used to separate attributes in string case (e.g. "r=0, stator, radial")

        :Type: str
        """,
    )

    def _get_sort_indices(self):
        """getter of sort_indices"""
        return self._sort_indices

    def _set_sort_indices(self, value):
        """setter of sort_indices"""
        if type(value) is int and value == -1:
            value = list()
        check_var("sort_indices", value, "list")
        self._sort_indices = value

    sort_indices = property(
        fget=_get_sort_indices,
        fset=_set_sort_indices,
        doc="""List of indices to use to sort axis

        :Type: list
        """,
    )

    def _get_filter(self):
        """getter of filter"""
        return self._filter

    def _set_filter(self, value):
        """setter of filter"""
        if type(value) is int and value == -1:
            value = dict()
        check_var("filter", value, "dict")
        self._filter = value

    filter = property(
        fget=_get_filter,
        fset=_set_filter,
        doc="""Dict of filter keys

        :Type: dict
        """,
    )

    def _get_char_to_rm(self):
        """getter of char_to_rm"""
        return self._char_to_rm

    def _set_char_to_rm(self, value):
        """setter of char_to_rm"""
        if type(value) is int and value == -1:
            value = list()
        check_var("char_to_rm", value, "list")
        self._char_to_rm = value

    char_to_rm = property(
        fget=_get_char_to_rm,
        fset=_set_char_to_rm,
        doc="""List of characters to remove in filter table

        :Type: list
        """,
    )
