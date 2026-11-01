# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/OPdq.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/OPdq
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.OP import OP

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Simulation.Input import InputError
from numpy import angle, pi, exp

from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class OPdq(OP):
    """Operating Point defined in DQH frame"""

    VERSION = 1

    # cf Methods.Simulation.OPdq.get_felec
    def get_felec(self, p=None):
        """Returns the electrical frequency

        Parameters
        ----------
        self : OPdq
            An OPdq object
        p: int
            pole pair number

        Returns
        -------
        felec : float
            Electrical Frequency [Hz]
        """

        if self.felec is not None:
            return self.felec

        # Compute felec if possible
        if self.N0 is None:
            raise InputError("OPdq object can't have felec and N0 both None")

        if p is None:
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError(
                    "OPdq object can't find machine parent to compute felec"
                )

            p = machine.get_pole_pair_number()

        self.felec = self.N0 * p / 60

        return self.felec

    # cf Methods.Simulation.OPdq.get_I0_Phi0
    def get_I0_Phi0(self):
        """Return I0 and Phi0

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        I_dict : dict
            Dict with key "I0", "Phi0"
        """
        if self.Id_ref is None or self.Iq_ref is None:
            return {"I0": None, "Phi0": None}
        else:
            Z = self.Id_ref + 1j * self.Iq_ref
            return {"I0": abs(Z), "Phi0": angle(Z) % (2 * pi)}

    # cf Methods.Simulation.OPdq.get_Id_Iq
    def get_Id_Iq(self):
        """Return Id and Iq

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        I_dict : dict
            Dict with key "Id", "Iq"
        """

        return {"Id": self.Id_ref, "Iq": self.Iq_ref}

    # cf Methods.Simulation.OPdq.get_N0
    def get_N0(self, p=None):
        """Returns the Rotor speed

        Parameters
        ----------
        self : OPdq
            An OPdq object
        p: int
            pole pair number

        Returns
        -------
        N0 : float
            Rotor speed [rpm]
        """

        if self.N0 is not None:
            return self.N0

        # Compute N0 if possible
        if self.felec is None:
            raise InputError("OPdq object can't have felec and N0 both None")

        if p is None:
            machine = self.get_machine_from_parent()
            if machine is None:
                raise InputError("OPdq object can't find machine parent to compute N0")
            p = machine.get_pole_pair_number()

        self.N0 = self.felec * 60 / p

        return self.N0

    # cf Methods.Simulation.OPdq.get_slip
    def get_slip(self):
        """Returns the Rotor mechanical slip

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        slip : float
            Rotor mechanical slip (0 for synchronous machines)
        """

        return 0

    # cf Methods.Simulation.OPdq.get_U0_UPhi0
    def get_U0_UPhi0(self):
        """Return U0 and UPhi0
        Parameters
        ----------
        self : OPdq
            An OPdq object
        Returns
        -------
        U_dict : dict
            Dict with key "U0", "UPhi0"
        """

        if self.Ud_ref is None or self.Uq_ref is None:
            return {"U0": None, "UPhi0": None}

        else:
            Z = self.Ud_ref + 1j * self.Uq_ref
            return {"U0": abs(Z), "UPhi0": angle(Z) % (2 * pi)}

    # cf Methods.Simulation.OPdq.get_Ud_Uq
    def get_Ud_Uq(self):
        """Return Ud and Uq

        Parameters
        ----------
        self : OPdq
            An OPdq object

        Returns
        -------
        U_dict : dict
            Dict with key "Ud", "Uq"
        """

        return {"Ud": self.Ud_ref, "Uq": self.Uq_ref}

    # cf Methods.Simulation.OPdq.set_I0_Phi0
    def set_I0_Phi0(self, I0, Phi0):
        """Set the value for I0 and IPhi0

        Parameters
        ----------
        self : OPdq
            An OPdq object
        I0 : float
            I0 value to set [Arms]
        Phi0 : float
            IPhi0 value to set [rad]
        """

        if I0 == 0:
            self.Id_ref = 0
            self.Iq_ref = 0
        else:
            Z = I0 * exp(1j * Phi0)
            self.Id_ref = Z.real
            self.Iq_ref = Z.imag

    # cf Methods.Simulation.OPdq.set_Id_Iq
    def set_Id_Iq(self, Id, Iq):
        """Set the value for Id and Iq

        Parameters
        ----------
        self : OPdq
            An OPdq object
        Id : float
            Id value to set [Arms]
        Iq : float
            Iq value to set [Arms]
        """

        self.Id_ref = Id
        self.Iq_ref = Iq

    # cf Methods.Simulation.OPdq.set_U0_UPhi0
    def set_U0_UPhi0(self, U0, UPhi0):
        """Set the value for U0 and UPhi0
        Parameters
        ----------
        self : OPdq
            An OPdq object
        U0 : float
            U0 value to set [Arms]
        UPhi0 : float
            UPhi0 value to set [rad]
        """

        if U0 == 0:
            self.Ud_ref = 0
            self.Uq_ref = 0
        else:
            Z = U0 * exp(1j * UPhi0)
            self.Ud_ref = Z.real
            self.Uq_ref = Z.imag

    # cf Methods.Simulation.OPdq.set_Ud_Uq
    def set_Ud_Uq(self, Ud, Uq):
        """Set the value for Ud and Uq

        Parameters
        ----------
        self : OPdq
            An OPdq object
        Ud : float
            Ud value to set [Vrms]
        Uq : float
            Uq value to set [Vrms]
        """

        self.Ud_ref = Ud
        self.Uq_ref = Uq

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Id_ref=None,
        Iq_ref=None,
        Ud_ref=None,
        Uq_ref=None,
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
            if "Id_ref" in list(init_dict.keys()):
                Id_ref = init_dict["Id_ref"]
            if "Iq_ref" in list(init_dict.keys()):
                Iq_ref = init_dict["Iq_ref"]
            if "Ud_ref" in list(init_dict.keys()):
                Ud_ref = init_dict["Ud_ref"]
            if "Uq_ref" in list(init_dict.keys()):
                Uq_ref = init_dict["Uq_ref"]
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
        self.Id_ref = Id_ref
        self.Iq_ref = Iq_ref
        self.Ud_ref = Ud_ref
        self.Uq_ref = Uq_ref
        # Call OP init
        super(OPdq, self).__init__(
            N0=N0,
            felec=felec,
            Tem_av_ref=Tem_av_ref,
            Pem_av_ref=Pem_av_ref,
            Pem_av_in=Pem_av_in,
            efficiency=efficiency,
        )
        # The class is frozen (in OP init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        OPdq_str = ""
        # Get the properties inherited from OP
        OPdq_str += super(OPdq, self).__str__()
        OPdq_str += "Id_ref = " + str(self.Id_ref) + linesep
        OPdq_str += "Iq_ref = " + str(self.Iq_ref) + linesep
        OPdq_str += "Ud_ref = " + str(self.Ud_ref) + linesep
        OPdq_str += "Uq_ref = " + str(self.Uq_ref) + linesep
        return OPdq_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from OP
        if not super(OPdq, self).__eq__(other):
            return False
        if other.Id_ref != self.Id_ref:
            return False
        if other.Iq_ref != self.Iq_ref:
            return False
        if other.Ud_ref != self.Ud_ref:
            return False
        if other.Uq_ref != self.Uq_ref:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from OP
        diff_list.extend(
            super(OPdq, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Id_ref is not None
            and self._Id_ref is not None
            and isnan(other._Id_ref)
            and isnan(self._Id_ref)
        ):
            pass
        elif other._Id_ref != self._Id_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Id_ref)
                    + ", other="
                    + str(other._Id_ref)
                    + ")"
                )
                diff_list.append(name + ".Id_ref" + val_str)
            else:
                diff_list.append(name + ".Id_ref")
        if (
            other._Iq_ref is not None
            and self._Iq_ref is not None
            and isnan(other._Iq_ref)
            and isnan(self._Iq_ref)
        ):
            pass
        elif other._Iq_ref != self._Iq_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Iq_ref)
                    + ", other="
                    + str(other._Iq_ref)
                    + ")"
                )
                diff_list.append(name + ".Iq_ref" + val_str)
            else:
                diff_list.append(name + ".Iq_ref")
        if (
            other._Ud_ref is not None
            and self._Ud_ref is not None
            and isnan(other._Ud_ref)
            and isnan(self._Ud_ref)
        ):
            pass
        elif other._Ud_ref != self._Ud_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Ud_ref)
                    + ", other="
                    + str(other._Ud_ref)
                    + ")"
                )
                diff_list.append(name + ".Ud_ref" + val_str)
            else:
                diff_list.append(name + ".Ud_ref")
        if (
            other._Uq_ref is not None
            and self._Uq_ref is not None
            and isnan(other._Uq_ref)
            and isnan(self._Uq_ref)
        ):
            pass
        elif other._Uq_ref != self._Uq_ref:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Uq_ref)
                    + ", other="
                    + str(other._Uq_ref)
                    + ")"
                )
                diff_list.append(name + ".Uq_ref" + val_str)
            else:
                diff_list.append(name + ".Uq_ref")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from OP
        S += super(OPdq, self).__sizeof__()
        S += getsizeof(self.Id_ref)
        S += getsizeof(self.Iq_ref)
        S += getsizeof(self.Ud_ref)
        S += getsizeof(self.Uq_ref)
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

        # Get the properties inherited from OP
        OPdq_dict = super(OPdq, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        OPdq_dict["Id_ref"] = self.Id_ref
        OPdq_dict["Iq_ref"] = self.Iq_ref
        OPdq_dict["Ud_ref"] = self.Ud_ref
        OPdq_dict["Uq_ref"] = self.Uq_ref
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        OPdq_dict["__class__"] = "OPdq"
        return OPdq_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Id_ref_val = self.Id_ref
        Iq_ref_val = self.Iq_ref
        Ud_ref_val = self.Ud_ref
        Uq_ref_val = self.Uq_ref
        N0_val = self.N0
        felec_val = self.felec
        Tem_av_ref_val = self.Tem_av_ref
        Pem_av_ref_val = self.Pem_av_ref
        Pem_av_in_val = self.Pem_av_in
        efficiency_val = self.efficiency
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Id_ref=Id_ref_val,
            Iq_ref=Iq_ref_val,
            Ud_ref=Ud_ref_val,
            Uq_ref=Uq_ref_val,
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

        self.Id_ref = None
        self.Iq_ref = None
        self.Ud_ref = None
        self.Uq_ref = None
        # Set to None the properties inherited from OP
        super(OPdq, self)._set_None()

    def _get_Id_ref(self):
        """getter of Id_ref"""
        return self._Id_ref

    def _set_Id_ref(self, value):
        """setter of Id_ref"""
        check_var("Id_ref", value, "float")
        self._Id_ref = value

    Id_ref = property(
        fget=_get_Id_ref,
        fset=_set_Id_ref,
        doc="""d-axis current rms value

        :Type: float
        """,
    )

    def _get_Iq_ref(self):
        """getter of Iq_ref"""
        return self._Iq_ref

    def _set_Iq_ref(self, value):
        """setter of Iq_ref"""
        check_var("Iq_ref", value, "float")
        self._Iq_ref = value

    Iq_ref = property(
        fget=_get_Iq_ref,
        fset=_set_Iq_ref,
        doc="""q-axis current rms value

        :Type: float
        """,
    )

    def _get_Ud_ref(self):
        """getter of Ud_ref"""
        return self._Ud_ref

    def _set_Ud_ref(self, value):
        """setter of Ud_ref"""
        check_var("Ud_ref", value, "float")
        self._Ud_ref = value

    Ud_ref = property(
        fget=_get_Ud_ref,
        fset=_set_Ud_ref,
        doc="""d-axis voltage rms value

        :Type: float
        """,
    )

    def _get_Uq_ref(self):
        """getter of Uq_ref"""
        return self._Uq_ref

    def _set_Uq_ref(self, value):
        """setter of Uq_ref"""
        check_var("Uq_ref", value, "float")
        self._Uq_ref = value

    Uq_ref = property(
        fget=_get_Uq_ref,
        fset=_set_Uq_ref,
        doc="""q-axis voltage rms value

        :Type: float
        """,
    )
