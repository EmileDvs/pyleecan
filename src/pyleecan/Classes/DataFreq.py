# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/SciDataTool/DataFreq.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/DataFreq
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import set_array, check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.DataND import DataND

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from numpy import any as np_any, inf
from pyleecan.Functions.SciDataTool.sum_convolution import (
    get_conv_amplitudes,
    get_conv_indices,
    get_sum_amplitudes,
    get_sum_indices,
)
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Functions.SciDataTool import AxisError

from numpy import array, array_equal
from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class DataFreq(DataND):
    """Class for fields defined in Fourier space"""

    VERSION = 1

    # cf Methods.SciDataTool.DataFreq.conv
    def conv(
        self,
        other,
        f_min=None,
        f_max=inf,
        tol_freq=1e-4,
        name=None,
        symbol=None,
        unit=None,
        normalizations=None,
    ):
        """Convolution of two DataFreq objects

        Parameters
        ----------
        self : DataFreq
            A DataFreq object
        other : DataFreq
            Another DataFreq object
        f_min: float
            Minimum frequency of convolved spectrum [Hz]
        f_max: float
            Maximum frequency of convolved spectrum [Hz]
        tol_freq: float
            Absolute tolerance value to filter harmonic orders by their frequency value
        name: str
            name
        symbol: str
            symbol
        unit: str
            unit
        normalizations: {Normalization}
            Dict of normalization objects

        Returns
        -------
        result : DataFreq
            DataFreq object resulting from convolution of both DataFreq objects
        """

        if not isinstance(other, type(self)):
            raise Exception("other is not a DataFreq object")

        if len(self.axes) > 1:
            raise Exception("self contains more than one axis")

        if len(other.axes) > 1:
            raise Exception("other contains more than one axis")

        if self.axes[0].name != "freqs":
            raise Exception("self axis is not frequency axis")
        else:
            freqs1 = self.axes[0].get_values()
            if np_any(freqs1) < 0:
                raise Exception("self contains negative frequency values")

        if other.axes[0].name != "freqs":
            raise Exception("other axis is not frequency axis")
        else:
            freqs2 = other.axes[0].get_values()
            if np_any(freqs2) < 0:
                raise Exception("other contains negative frequency values")

        # Fill metadata
        if name is None:
            name = self.name
        if symbol is None:
            symbol = self.symbol
        if unit is None:
            unit = self.unit
        if normalizations is None:
            normalizations = self.normalizations

        # Compute spectrum orders resulting from convolution
        freqs_un, I0a, I0b, I1, I2 = get_conv_indices(
            freqs1, freqs2, f_min, f_max, tol_freq
        )

        # Compute spectrum amplitudes resulting from convolution
        amp = get_conv_amplitudes(self.values, other.values, I0a, I0b, I1, I2)

        # Create Frequency axis
        Freqs = self.axes[0].copy()
        Freqs.values = freqs_un

        # Create DataFreq resulting from convolution
        result = type(self)(
            name=name,
            unit=unit,
            symbol=symbol,
            axes=[Freqs],
            values=amp,
            normalizations=normalizations,
        )

        return result

    # cf Methods.SciDataTool.DataFreq.freq_to_time
    def freq_to_time(self):
        """Performs the inverse Fourier Transform and stores the resulting field in a DataTime object.
        Parameters
        ----------
        self : DataFreq
            a DataFreq object
        Returns
        -------
        a DataTime object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.DataTime", fromlist=["DataTime"])
        DataTime = module.DataTime
        module = __import__("pyleecan.Classes.DataPattern", fromlist=["DataPattern"])
        DataPattern = module.DataPattern

        axes_str = []
        for i, axis in enumerate(self.axes):
            if axis.is_components:
                axis_str = axis.name + str(list(range(len(axis.values))))
            elif axis.name == "freqs":
                axis_str = "time[smallestperiod]"
            elif axis.name == "wavenumber":
                axis_str = "angle[smallestperiod]"
            elif isinstance(axis, DataPattern):
                axis_str = axis.name + "[pattern]"
            else:
                axis_str = axis.name + "[smallestperiod]"
            axes_str.append(axis_str)
        if axes_str == [axis.name for axis in self.axes]:
            raise AxisError(
                "No available axis is compatible with fft (should be time or angle)"
            )
        else:
            results = self.get_along(*axes_str)
            values = results.pop(self.symbol)
            Axes = []
            for axis in self.axes:
                if axis.name == "freqs":
                    axis_new = Data1D(
                        name="time",
                        is_components=False,
                        values=results["time"],
                        unit="s",
                        symmetries=axis.symmetries.copy(),
                        normalizations=axis.normalizations.copy(),
                    )
                elif axis.name == "wavenumber":
                    axis_new = Data1D(
                        name="angle",
                        is_components=False,
                        values=results["angle"],
                        unit="rad",
                        symmetries=axis.symmetries.copy(),
                        normalizations=axis.normalizations.copy(),
                    )
                else:
                    axis_new = axis.copy()
                Axes.append(axis_new)

            return DataTime(
                name=self.name,
                unit=self.unit,
                symbol=self.symbol,
                axes=Axes,
                values=values,
                is_real=self.is_real,
                normalizations=self.normalizations.copy(),
            )

    # cf Methods.SciDataTool.DataFreq.sum
    def sum(
        self,
        other,
        tol_freq=1e-4,
        name=None,
        symbol=None,
        unit=None,
        normalizations=None,
    ):
        """Merge two DataFreq objects

        Parameters
        ----------
        self : DataFreq
            A DataFreq object
        other : DataFreq
            Another DataFreq object
        tol_freq: float
            Absolute tolerance value to filter harmonic orders by their frequency value
        name: str
            name
        symbol: str
            symbol
        unit: str
            unit
        normalizations: {Normalization}
            Dict of normalization objects

        Returns
        -------
        result : Spectrum
            DataFreq object resulting from summing both DataFreq objects
        """

        if not isinstance(other, type(self)):
            raise Exception("other is not a DataFreq object")

        if len(self.axes) > 1:
            raise Exception("self contains more than one axis")

        if len(other.axes) > 1:
            raise Exception("other contains more than one axis")

        if self.axes[0].name != "freqs":
            raise Exception("self axis is not frequency axis")
        else:
            freqs1 = self.axes[0].get_values()
            if np_any(freqs1) < 0:
                raise Exception("self contains negative frequency values")

        if other.axes[0].name != "freqs":
            raise Exception("other axis is not frequency axis")
        else:
            freqs2 = other.axes[0].get_values()
            if np_any(freqs2) < 0:
                raise Exception("other contains negative frequency values")

        # Fill metadata
        if name is None:
            name = self.name
        if symbol is None:
            symbol = self.symbol
        if unit is None:
            unit = self.unit
        if normalizations is None:
            normalizations = self.normalizations

        # Compute spectrum orders resulting from convolution
        freqs_un, I0b = get_sum_indices(freqs1, freqs2, tol_freq)

        # Compute spectrum amplitudes resulting from convolution
        amp = get_sum_amplitudes(self.values, other.values, I0b)

        # Create Frequency axis
        Freqs = self.axes[0].copy()
        Freqs.values = freqs_un

        # Create DataFreq resulting from convolution
        result = type(self)(
            name=name,
            unit=unit,
            symbol=symbol,
            axes=[Freqs],
            values=amp,
            normalizations=normalizations,
        )

        return result

    # cf Methods.SciDataTool.DataFreq.to_datadual
    def to_datadual(self, datatime=None):
        """Creates a DataDual object.
        Parameters
        ----------
        self : DataFreq
            a DataFreq object
        datatime : DataTime
            a DataTime object
        Returns
        -------
        a DataDual object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.DataDual", fromlist=["DataDual"])
        DataDual = module.DataDual

        # Fill DataDual object with fourier data
        datadual = DataDual(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations.copy(),
            axes_df=self.axes,
            values_df=self.values,
        )

        # Add time/space data (from input or using ifft)
        if datatime is None:
            datatime = self.freq_to_time()
        datadual.axes_dt = datatime.axes
        datadual.values_dt = datatime.values

        return datadual

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        axes=None,
        FTparameters=-1,
        values=None,
        is_real=True,
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
            if "axes" in list(init_dict.keys()):
                axes = init_dict["axes"]
            if "FTparameters" in list(init_dict.keys()):
                FTparameters = init_dict["FTparameters"]
            if "values" in list(init_dict.keys()):
                values = init_dict["values"]
            if "is_real" in list(init_dict.keys()):
                is_real = init_dict["is_real"]
            if "symbol" in list(init_dict.keys()):
                symbol = init_dict["symbol"]
            if "name" in list(init_dict.keys()):
                name = init_dict["name"]
            if "unit" in list(init_dict.keys()):
                unit = init_dict["unit"]
            if "normalizations" in list(init_dict.keys()):
                normalizations = init_dict["normalizations"]
        # Set the properties (value check and convertion are done in setter)
        # Call DataND init
        super(DataFreq, self).__init__(
            axes=axes,
            FTparameters=FTparameters,
            values=values,
            is_real=is_real,
            symbol=symbol,
            name=name,
            unit=unit,
            normalizations=normalizations,
        )
        # The class is frozen (in DataND init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        DataFreq_str = ""
        # Get the properties inherited from DataND
        DataFreq_str += super(DataFreq, self).__str__()
        return DataFreq_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from DataND
        if not super(DataFreq, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from DataND
        diff_list.extend(
            super(DataFreq, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from DataND
        S += super(DataFreq, self).__sizeof__()
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

        # Get the properties inherited from DataND
        DataFreq_dict = super(DataFreq, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        DataFreq_dict["__class__"] = "DataFreq"
        return DataFreq_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.axes is None:
            axes_val = None
        else:
            axes_val = list()
            for obj in self.axes:
                axes_val.append(obj.copy())
        if self.FTparameters is None:
            FTparameters_val = None
        else:
            FTparameters_val = self.FTparameters.copy()
        if self.values is None:
            values_val = None
        else:
            values_val = self.values.copy()
        is_real_val = self.is_real
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
            axes=axes_val,
            FTparameters=FTparameters_val,
            values=values_val,
            is_real=is_real_val,
            symbol=symbol_val,
            name=name_val,
            unit=unit_val,
            normalizations=normalizations_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from DataND
        super(DataFreq, self)._set_None()
