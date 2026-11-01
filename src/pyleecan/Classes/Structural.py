# File generated according to Generator/ClassesRef/Simulation/Structural.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/Structural"""

from os import linesep
from sys import getsizeof

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Classes.OutStruct import OutStruct
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Structural(FrozenClass):
    """Structural module abstract object"""

    VERSION = 1

    # cf Methods.Simulation.Structural.comp_axes
    def comp_axes(self, output):
        """Compute axes used for the Structural module

        Parameters
        ----------
        self : Structural
            a Structural object
        output : Output
            an Output object (to update)
        """
        if self.parent is None:
            raise InputError(
                "The Structural object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")

        # setup OutStruct if None
        if self.parent.parent.struct is None:
            self.parent.parent.struct = OutStruct()

        output.struct.axes_dict = dict()

        for key, val in output.geo.axes_dict.items():
            output.struct.axes_dict[key] = val

    # cf Methods.Simulation.Structural.run
    def run(self):
        """Run the Structural module"""
        if self.parent is None:
            raise InputError(
                "ERROR: The Structural object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError(
                "ERROR: The Simulation object must be in an Output object to run"
            )

        output = self.parent.parent

        self.comp_axes(output)

        group = self.force.group  # Magnetic force target

        # Init model, generate or import mechanical mesh
        self.init_mechanical_model(output, group)

        # Compute the magnetic force according to the Force model
        self.force.comp_force(output)

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self, logger_name="Pyleecan.Structural", init_dict=None, init_str=None
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
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.logger_name = logger_name

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Structural_str = ""
        if self.parent is None:
            Structural_str += "parent = None " + linesep
        else:
            Structural_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Structural_str += 'logger_name = "' + str(self.logger_name) + '"' + linesep
        return Structural_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.logger_name != self.logger_name:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._logger_name != self._logger_name:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._logger_name)
                    + ", other="
                    + str(other._logger_name)
                    + ")"
                )
                diff_list.append(name + ".logger_name" + val_str)
            else:
                diff_list.append(name + ".logger_name")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.logger_name)
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

        Structural_dict = dict()
        Structural_dict["logger_name"] = self.logger_name
        # The class name is added to the dict for deserialisation purpose
        Structural_dict["__class__"] = "Structural"
        return Structural_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        logger_name_val = self.logger_name
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(logger_name=logger_name_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.logger_name = None

    def _get_logger_name(self):
        """getter of logger_name"""
        return self._logger_name

    def _set_logger_name(self, value):
        """setter of logger_name"""
        check_var("logger_name", value, "str")
        self._logger_name = value

    logger_name = property(
        fget=_get_logger_name,
        fset=_set_logger_name,
        doc="""Name of the logger to use

        :Type: str
        """,
    )

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""

        pass


InputError = Structural.InputError
