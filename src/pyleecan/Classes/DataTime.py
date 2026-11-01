# File generated according to Generator/ClassesRef/SciDataTool/DataTime.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/SciDataTool/DataTime"""

from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataND import DataND
from pyleecan.Functions.SciDataTool import AxisError
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class DataTime(DataND):
    """Class for fields defined in time space"""

    VERSION = 1

    # cf Methods.SciDataTool.DataTime.time_to_freq
    def time_to_freq(self):
        """Performs the Fourier Transform and stores the resulting field in a DataFreq object.
        Parameters
        ----------
        self : DataTime
            a DataTime object
        Returns
        -------
        a DataFreq object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.DataFreq", fromlist=["DataFreq"])
        DataFreq = module.DataFreq
        module = __import__("pyleecan.Classes.DataPattern", fromlist=["DataPattern"])
        DataPattern = module.DataPattern

        axes_str = []
        for i, axis in enumerate(self.axes):
            if axis.is_components:
                axis_str = axis.name + str(list(range(len(axis.values))))
            elif axis.name == "time":
                axis_str = "freqs"
            elif axis.name == "angle":
                axis_str = "wavenumber"
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
                if axis.name == "time":
                    if "antiperiod" in axis.symmetries:
                        symmetries = {"period": int(axis.symmetries["antiperiod"] / 2)}
                    else:
                        symmetries = axis.symmetries.copy()
                    axis_new = Data1D(
                        name="freqs",
                        is_components=False,
                        values=results["freqs"],
                        unit="Hz",
                        symmetries=symmetries,
                        normalizations=axis.normalizations.copy(),
                    ).to_linspace()
                elif axis.name == "angle":
                    if "antiperiod" in axis.symmetries:
                        symmetries = {"period": int(axis.symmetries["antiperiod"] / 2)}
                    else:
                        symmetries = axis.symmetries.copy()
                    axis_new = Data1D(
                        name="wavenumber",
                        is_components=False,
                        values=results["wavenumber"],
                        unit="dimless",
                        symmetries=symmetries,
                        normalizations=axis.normalizations.copy(),
                    ).to_linspace()
                else:
                    axis_new = axis.copy()
                Axes.append(axis_new)
            return DataFreq(
                name=self.name,
                unit=self.unit,
                symbol=self.symbol,
                axes=Axes,
                values=values,
                is_real=self.is_real,
                normalizations=self.normalizations.copy(),
            )

    # cf Methods.SciDataTool.DataTime.to_datadual
    def to_datadual(self, datafreq=None):
        """Creates a DataDual object.
        Parameters
        ----------
        self : DataTime
            a DataTime object
        datafreq : DataFreq
            a DataFreq object
        Returns
        -------
        a DataDual object
        """

        # Dynamic import to avoid loop
        module = __import__("pyleecan.Classes.DataDual", fromlist=["DataDual"])
        DataDual = module.DataDual

        # Fill DataDual object with time/space data
        datadual = DataDual(
            name=self.name,
            symbol=self.symbol,
            unit=self.unit,
            normalizations=self.normalizations.copy(),
            axes_dt=self.axes,
            values_dt=self.values,
        )

        # Add fourier data (from input or using fft)
        if datafreq is None:
            datafreq = self.time_to_freq()
        datadual.axes_df = datafreq.axes
        datadual.values_df = datafreq.values

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
        super(DataTime, self).__init__(
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

        DataTime_str = ""
        # Get the properties inherited from DataND
        DataTime_str += super(DataTime, self).__str__()
        return DataTime_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from DataND
        if not super(DataTime, self).__eq__(other):
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
            super(DataTime, self).compare(
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
        S += super(DataTime, self).__sizeof__()
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
        DataTime_dict = super(DataTime, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        DataTime_dict["__class__"] = "DataTime"
        return DataTime_dict

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
        super(DataTime, self)._set_None()
