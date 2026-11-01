# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/OP.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/OP
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
from ._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from numpy import zeros
from ..Methods.Simulation.OPMatrix import OPMatrixException

from numpy import isnan
from ._check import InitUnKnowClassError


class OP(FrozenClass):
    """Define the Operating Point of the simulation"""

    VERSION = 1

    # cf Methods.Simulation.OP.get_machine_from_parent
    def get_machine_from_parent(self):
        """Search in the parent to find the machine

        Parameters
        ----------
        self : OP
            An OP object

        Returns
        -------
        machine : Machine
            Machine from the parent (or None)
        """

        parent = self.parent
        while parent is not None and not hasattr(parent, "machine"):
            parent = parent.parent

        if parent is not None:
            return parent.machine
        else:
            # Try to import machine from simu object
            parent = self.parent
            while parent is not None and not hasattr(parent, "simu"):
                parent = parent.parent
            if parent is not None:
                return parent.simu.machine
            else:
                return None

    # cf Methods.Simulation.OP.get_OP_array
    def get_OP_array(self, *arg_list):
        """get the OP_matrix by identifying the columns
        Ex: get_OP_array("N0", "Iq", "Iq", "Tem")
        get_OP_array(OP_matrix) calls get_OP_array("N0", "Id", "Iq", "Tem", "Pem")

        Parameters
        ----------
        self : OP
            Operating Point object to convert to a matrix
        *arg_list : list of str
            arguments to specify the OP_matrix columns name

        Returns
        -------
        OP_matrix: ndarray
            Single line OP_matrix with the selected columns
        """

        # Extract arg_list it the function called from another script with *arg_list
        if len(arg_list) == 1 and type(arg_list[0]) == tuple:
            arg_list = arg_list[0]

        # Init OP_matrix
        OP_matrix = zeros((1, len(arg_list)))

        # Setup default argument (N0, Id, Iq, Tem, Pem)
        Idq_dict = self.get_Id_Iq()
        if len(arg_list) == 0:
            if self.N0 is not None:
                arg_list.append("N0")
            if Idq_dict["Id"] is not None:
                arg_list.append("Id")
            if Idq_dict["Iq"] is not None:
                arg_list.append("Iq")
            if self.Tem_av_ref is not None:
                arg_list.append("Tem")
            if self.Pem_av_ref is not None:
                arg_list.append("Pem")

        # Set column by column according to arg_list
        I0_dict = self.get_I0_Phi0()
        Udq_dict = self.get_Ud_Uq()
        U0_dict = self.get_U0_UPhi0()
        for ii in range(len(arg_list)):
            # N0
            if arg_list[ii].lower() in ["n0", "no", "0n", "on"]:
                OP_matrix[0, ii] = self.N0
            # Id/Iq
            elif arg_list[ii].lower() in ["id", "di", "id_ref"]:
                OP_matrix[0, ii] = Idq_dict["Id"]
            elif arg_list[ii].lower() in ["iq", "qi", "iq_ref"]:
                OP_matrix[0, ii] = Idq_dict["Iq"]
            # I0/Phi0
            elif arg_list[ii].lower() in ["i0", "0i", "i0_ref"]:
                OP_matrix[0, ii] = I0_dict["I0"]
            elif arg_list[ii].lower() in ["iphi0", "phi0", "phio"]:
                OP_matrix[0, ii] = I0_dict["Phi0"]
            # Tem
            elif arg_list[ii].lower() in ["tem", "t", "tem_av", "tem_av_ref"]:
                OP_matrix[0, ii] = self.Tem_av_ref
            # Pem
            elif arg_list[ii].lower() in ["pem", "p", "pem_av", "pem_av_ref"]:
                OP_matrix[0, ii] = self.Pem_av_ref
            # Ud/Uq
            elif arg_list[ii].lower() in ["ud", "du", "ud_ref"]:
                OP_matrix[0, ii] = Udq_dict["Ud"]
            elif arg_list[ii].lower() in ["uq", "qu", "uq_ref"]:
                OP_matrix[0, ii] = Udq_dict["Uq"]
            # U0/UPhi0
            elif arg_list[ii].lower() in ["u0", "0u", "u0_ref"]:
                OP_matrix[0, ii] = U0_dict["U0"]
            elif arg_list[ii].lower() in ["uphi0", "uphio"]:
                OP_matrix[0, ii] = U0_dict["UPhi0"]
            # If
            elif arg_list[ii].lower() in ["if", "fi"]:
                OP_matrix[0, ii] = self.If_ref
            else:
                raise OPMatrixException(
                    "Error in OP_matrix.get_OP_array, unknow column name for index "
                    + str(ii)
                    + " in "
                    + str(arg_list)
                )

        return OP_matrix

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        N0=None,
        felec=None,
        Tem_av_ref=None,
        Pem_av_ref=None,
        Pem_av_in=None,
        efficiency=None,
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
            if "N0" in list(init_dict.keys()):
                N0 = init_dict["N0"]
            if "felec" in list(init_dict.keys()):
                felec = init_dict["felec"]
            if "Tem_av_ref" in list(init_dict.keys()):
                Tem_av_ref = init_dict["Tem_av_ref"]
            if "Pem_av_ref" in list(init_dict.keys()):
                Pem_av_ref = init_dict["Pem_av_ref"]
            if "Pem_av_in" in list(init_dict.keys()):
                Pem_av_in = init_dict["Pem_av_in"]
            if "efficiency" in list(init_dict.keys()):
                efficiency = init_dict["efficiency"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.N0 = N0
        self.felec = felec
        self.Tem_av_ref = Tem_av_ref
        self.Pem_av_ref = Pem_av_ref
        self.Pem_av_in = Pem_av_in
        self.efficiency = efficiency

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        OP_str = ""
        if self.parent is None:
            OP_str += "parent = None " + linesep
        else:
            OP_str += "parent = " + str(type(self.parent)) + " object" + linesep
        OP_str += "N0 = " + str(self.N0) + linesep
        OP_str += "felec = " + str(self.felec) + linesep
        OP_str += "Tem_av_ref = " + str(self.Tem_av_ref) + linesep
        OP_str += "Pem_av_ref = " + str(self.Pem_av_ref) + linesep
        OP_str += "Pem_av_in = " + str(self.Pem_av_in) + linesep
        OP_str += "efficiency = " + str(self.efficiency) + linesep
        return OP_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.N0 != self.N0:
            return False
        if other.felec != self.felec:
            return False
        if other.Tem_av_ref != self.Tem_av_ref:
            return False
        if other.Pem_av_ref != self.Pem_av_ref:
            return False
        if other.Pem_av_in != self.Pem_av_in:
            return False
        if other.efficiency != self.efficiency:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (
            other._N0 is not None
            and self._N0 is not None
            and isnan(other._N0)
            and isnan(self._N0)
        ):
            pass
        elif other._N0 != self._N0:
            if is_add_value:
                val_str = " (self=" + str(self._N0) + ", other=" + str(other._N0) + ")"
                diff_list.append(name + ".N0" + val_str)
            else:
                diff_list.append(name + ".N0")
        if (
            other._felec is not None
            and self._felec is not None
            and isnan(other._felec)
            and isnan(self._felec)
        ):
            pass
        elif other._felec != self._felec:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._felec) + ", other=" + str(other._felec) + ")"
                )
                diff_list.append(name + ".felec" + val_str)
            else:
                diff_list.append(name + ".felec")
        if (
            other._Tem_av_ref is not None
            and self._Tem_av_ref is not None
            and isnan(other._Tem_av_ref)
            and isnan(self._Tem_av_ref)
        ):
            pass
        elif other._Tem_av_ref != self._Tem_av_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Tem_av_ref)
                    + ", other="
                    + str(other._Tem_av_ref)
                    + ")"
                )
                diff_list.append(name + ".Tem_av_ref" + val_str)
            else:
                diff_list.append(name + ".Tem_av_ref")
        if (
            other._Pem_av_ref is not None
            and self._Pem_av_ref is not None
            and isnan(other._Pem_av_ref)
            and isnan(self._Pem_av_ref)
        ):
            pass
        elif other._Pem_av_ref != self._Pem_av_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Pem_av_ref)
                    + ", other="
                    + str(other._Pem_av_ref)
                    + ")"
                )
                diff_list.append(name + ".Pem_av_ref" + val_str)
            else:
                diff_list.append(name + ".Pem_av_ref")
        if (
            other._Pem_av_in is not None
            and self._Pem_av_in is not None
            and isnan(other._Pem_av_in)
            and isnan(self._Pem_av_in)
        ):
            pass
        elif other._Pem_av_in != self._Pem_av_in:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Pem_av_in)
                    + ", other="
                    + str(other._Pem_av_in)
                    + ")"
                )
                diff_list.append(name + ".Pem_av_in" + val_str)
            else:
                diff_list.append(name + ".Pem_av_in")
        if (
            other._efficiency is not None
            and self._efficiency is not None
            and isnan(other._efficiency)
            and isnan(self._efficiency)
        ):
            pass
        elif other._efficiency != self._efficiency:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._efficiency)
                    + ", other="
                    + str(other._efficiency)
                    + ")"
                )
                diff_list.append(name + ".efficiency" + val_str)
            else:
                diff_list.append(name + ".efficiency")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.N0)
        S += getsizeof(self.felec)
        S += getsizeof(self.Tem_av_ref)
        S += getsizeof(self.Pem_av_ref)
        S += getsizeof(self.Pem_av_in)
        S += getsizeof(self.efficiency)
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

        OP_dict = dict()
        OP_dict["N0"] = self.N0
        OP_dict["felec"] = self.felec
        OP_dict["Tem_av_ref"] = self.Tem_av_ref
        OP_dict["Pem_av_ref"] = self.Pem_av_ref
        OP_dict["Pem_av_in"] = self.Pem_av_in
        OP_dict["efficiency"] = self.efficiency
        # The class name is added to the dict for deserialisation purpose
        OP_dict["__class__"] = "OP"
        return OP_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        N0_val = self.N0
        felec_val = self.felec
        Tem_av_ref_val = self.Tem_av_ref
        Pem_av_ref_val = self.Pem_av_ref
        Pem_av_in_val = self.Pem_av_in
        efficiency_val = self.efficiency
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            N0=N0_val,
            felec=felec_val,
            Tem_av_ref=Tem_av_ref_val,
            Pem_av_ref=Pem_av_ref_val,
            Pem_av_in=Pem_av_in_val,
            efficiency=efficiency_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.N0 = None
        self.felec = None
        self.Tem_av_ref = None
        self.Pem_av_ref = None
        self.Pem_av_in = None
        self.efficiency = None

    def _get_N0(self):
        """getter of N0"""
        return self._N0

    def _set_N0(self, value):
        """setter of N0"""
        check_var("N0", value, "float")
        self._N0 = value

    N0 = property(
        fget=_get_N0,
        fset=_set_N0,
        doc="""Rotor speed

        :Type: float
        """,
    )

    def _get_felec(self):
        """getter of felec"""
        return self._felec

    def _set_felec(self, value):
        """setter of felec"""
        check_var("felec", value, "float")
        self._felec = value

    felec = property(
        fget=_get_felec,
        fset=_set_felec,
        doc="""Electrical Frequency

        :Type: float
        """,
    )

    def _get_Tem_av_ref(self):
        """getter of Tem_av_ref"""
        return self._Tem_av_ref

    def _set_Tem_av_ref(self, value):
        """setter of Tem_av_ref"""
        check_var("Tem_av_ref", value, "float")
        self._Tem_av_ref = value

    Tem_av_ref = property(
        fget=_get_Tem_av_ref,
        fset=_set_Tem_av_ref,
        doc="""Output average electromagnetic torque

        :Type: float
        """,
    )

    def _get_Pem_av_ref(self):
        """getter of Pem_av_ref"""
        return self._Pem_av_ref

    def _set_Pem_av_ref(self, value):
        """setter of Pem_av_ref"""
        check_var("Pem_av_ref", value, "float")
        self._Pem_av_ref = value

    Pem_av_ref = property(
        fget=_get_Pem_av_ref,
        fset=_set_Pem_av_ref,
        doc="""Output average Electromagnetic Power

        :Type: float
        """,
    )

    def _get_Pem_av_in(self):
        """getter of Pem_av_in"""
        return self._Pem_av_in

    def _set_Pem_av_in(self, value):
        """setter of Pem_av_in"""
        check_var("Pem_av_in", value, "float")
        self._Pem_av_in = value

    Pem_av_in = property(
        fget=_get_Pem_av_in,
        fset=_set_Pem_av_in,
        doc="""Input average power (e.g. for generator mode)

        :Type: float
        """,
    )

    def _get_efficiency(self):
        """getter of efficiency"""
        return self._efficiency

    def _set_efficiency(self, value):
        """setter of efficiency"""
        check_var("efficiency", value, "float")
        self._efficiency = value

    efficiency = property(
        fget=_get_efficiency,
        fset=_set_efficiency,
        doc="""Efficiency

        :Type: float
        """,
    )
