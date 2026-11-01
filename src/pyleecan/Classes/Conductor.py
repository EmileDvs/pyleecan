# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Machine/Conductor.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Machine/Conductor
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
from pyleecan.Classes._frozen import FrozenClass

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np


from pyleecan.Classes._check import InitUnKnowClassError


class Conductor(FrozenClass):
    """abstact class for conductors"""

    VERSION = 1

    # cf Methods.Machine.Conductor.check
    def check(self):
        """Check that the Conductor object is correct

        Parameters
        ----------
        self : Conductor
            A Conductor object

        Returns
        -------
        None
        """
        pass

    # cf Methods.Machine.Conductor.comp_skin_effect_inductance
    def comp_skin_effect_inductance(
        self, freq, T_op=20, T_ref=20, b4=None, h4=None, zt=None
    ):
        """Compute the skin effect factor on inductance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters bc, h4, z4, are defined in Fig(4.14) p.249

        Parameters
        ----------
        self : Conductor
            an Conductor object
        freq: float or ndarray
            electrical frequency [Hz]
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]
        b4: float
            Slot width [m]
        h4: float
            Slot height [m]
        zt: int
            Number of radial adjacent conductors

        Returns
        ----------
        kl_skin : float
            skin effect coeff for inductance at given frequency and temperature
        """

        if b4 is None:
            # Compute slot average width
            slot = self.parent.parent.slot
            b4 = slot.comp_width()

        if h4 is None:
            # Compute slot height
            slot = self.parent.parent.slot
            h4 = slot.comp_height()

        if zt is None:
            # Get number of turns in series per coil
            zt = self.parent.Ntcoil

        # conductor width
        bc = self.comp_width_wire()

        # Electrical conductivity accounting for temperature increase
        sigma = self.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if self.cond_mat.mag is None or self.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = self.cond_mat.mag.mur_lin

        # Electrical pulsation
        w = 2 * np.pi * freq

        # reduced conductor height Eq(4.90) p.257 + addind relative permeatibility
        ksi = h4 * np.sqrt(w * mu0 * mur * sigma * bc / (2 * b4))

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # resistance factor function phi prime Eq(4.92) p.257
        phip = (
            3
            / (2 * ksi)
            * (np.sinh(2 * ksi) - np.sin(2 * ksi))
            / (np.cosh(2 * ksi) - np.cos(2 * ksi))
        )

        # resistance factor function psi prime Eq(4.91) p.257
        psip = 1 / ksi * (np.sinh(ksi) + np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

        # average resistance factor  Eq(4.91) p.257
        kl_skin = phip / zt**2 + ((zt**2 - 1) / zt**2) * psip

        return kl_skin

    # cf Methods.Machine.Conductor.comp_skin_effect_resistance
    def comp_skin_effect_resistance(self, freq, T_op=20, T_ref=20, b=None, zt=None):
        """Compute the skin effect factor on resistance for the conductors from "Design of Rotating Electrical Machines", J. Pyrhonen, second edition
        All parameters are defined p.270 / 271

        Parameters
        ----------
        self : Conductor
            an Conductor object
        b: float
            Slot width [m]
        zt: int
            Number of turns in series per coil
        freq: float or ndarray
            electrical frequency [Hz]
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        kr_skin : float
            skin effect coeff for resistance at given frequency and temperature
        """

        if b is None:
            # Compute slot average width
            slot = self.parent.parent.slot
            b = slot.comp_width()

        if zt is None:
            # Get number of turns in series per coil
            zt = self.parent.Ntcoil

        # check if wires are round or rectangular
        is_round_wire = self.is_round_wire()

        # conductor height
        hc0 = self.comp_height_wire()
        # conductor width
        bc0 = self.comp_width_wire()
        # Number of circumferential adjacent wires
        za = self.comp_nb_circumferential_wire()
        # Number of radial adjacent wires
        zp = self.comp_nb_radial_wire()
        # Equivalent height of conductor
        hc = zp * hc0

        # Electrical conductivity accounting for temperature increase
        sigma = self.cond_mat.elec.get_conductivity(T_op=T_op, T_ref=T_ref)

        # Magnetic permeability
        mu0 = 4 * np.pi * 1e-7
        if self.cond_mat.mag is None or self.cond_mat.mag.mur_lin is None:
            mur = 1
        else:
            mur = self.cond_mat.mag.mur_lin

        # Electrical pulsation
        w = 2 * np.pi * freq

        # reduced conductor height Eq(5.24) p.270 + adding relative permeatibility
        ksi = hc * np.sqrt((1 / 2) * w * mu0 * mur * sigma * za * bc0 / b)

        if not isinstance(ksi, float):
            # Avoid numerical error with 0
            ksi[ksi == 0] = 1e-4

        # average resistance factor
        if is_round_wire:
            # Use round wire approximation Eq(5.30) p.271
            kr_skin = 1 + 0.59 * ((zt**2 - 0.2) / 9) * ksi**4
        else:
            # resistance factor function phi Eq(5.26) p.271
            phi = (
                ksi
                * (np.sinh(2 * ksi) + np.sin(2 * ksi))
                / (np.cosh(2 * ksi) - np.cos(2 * ksi))
            )

            # resistance factor function psi Eq(5.27) p.271
            psi = 2 * ksi * (np.sinh(ksi) - np.sin(ksi)) / (np.cosh(ksi) + np.cos(ksi))

            kr_skin = phi + ((zt**2 - 1) / 3) * psi  # Eq(5.28) p.271
            # kr_approx = 1 + (zt ** 2 - 0.2) / 9 * ksi ** 4  # Eq(5.29) p.271

        return kr_skin

    # cf Methods.Machine.Conductor.comp_temperature_effect
    def comp_temperature_effect(self, T_op, T_ref=20):
        """Compute the temperature effect factor for the conductor

        Parameters
        ----------
        self : Conductor
            an Conductor object
        T_op: float
            Conductor operational temperature [degC]
        T_ref: float
            Conductor reference temperature [degC]

        Returns
        ----------
        Tfact : float
            temperature effect coeff for resistance at T_op
        """

        alphasw = self.cond_mat.elec.alpha
        Tfact = 1 + alphasw * (T_op - T_ref)

        return Tfact

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, cond_mat=-1, ins_mat=-1, init_dict=None, init_str=None):
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
            if "cond_mat" in list(init_dict.keys()):
                cond_mat = init_dict["cond_mat"]
            if "ins_mat" in list(init_dict.keys()):
                ins_mat = init_dict["ins_mat"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.cond_mat = cond_mat
        self.ins_mat = ins_mat

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Conductor_str = ""
        if self.parent is None:
            Conductor_str += "parent = None " + linesep
        else:
            Conductor_str += "parent = " + str(type(self.parent)) + " object" + linesep
        if self.cond_mat is not None:
            tmp = self.cond_mat.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Conductor_str += "cond_mat = " + tmp
        else:
            Conductor_str += "cond_mat = None" + linesep + linesep
        if self.ins_mat is not None:
            tmp = self.ins_mat.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Conductor_str += "ins_mat = " + tmp
        else:
            Conductor_str += "ins_mat = None" + linesep + linesep
        return Conductor_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.cond_mat != self.cond_mat:
            return False
        if other.ins_mat != self.ins_mat:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (other.cond_mat is None and self.cond_mat is not None) or (
            other.cond_mat is not None and self.cond_mat is None
        ):
            diff_list.append(name + ".cond_mat None mismatch")
        elif self.cond_mat is not None:
            diff_list.extend(
                self.cond_mat.compare(
                    other.cond_mat,
                    name=name + ".cond_mat",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.ins_mat is None and self.ins_mat is not None) or (
            other.ins_mat is not None and self.ins_mat is None
        ):
            diff_list.append(name + ".ins_mat None mismatch")
        elif self.ins_mat is not None:
            diff_list.extend(
                self.ins_mat.compare(
                    other.ins_mat,
                    name=name + ".ins_mat",
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
        S += getsizeof(self.cond_mat)
        S += getsizeof(self.ins_mat)
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

        Conductor_dict = dict()
        if self.cond_mat is None:
            Conductor_dict["cond_mat"] = None
        else:
            Conductor_dict["cond_mat"] = self.cond_mat.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.ins_mat is None:
            Conductor_dict["ins_mat"] = None
        else:
            Conductor_dict["ins_mat"] = self.ins_mat.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        Conductor_dict["__class__"] = "Conductor"
        return Conductor_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.cond_mat is None:
            cond_mat_val = None
        else:
            cond_mat_val = self.cond_mat.copy()
        if self.ins_mat is None:
            ins_mat_val = None
        else:
            ins_mat_val = self.ins_mat.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(cond_mat=cond_mat_val, ins_mat=ins_mat_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.cond_mat is not None:
            self.cond_mat._set_None()
        if self.ins_mat is not None:
            self.ins_mat._set_None()

    def _get_cond_mat(self):
        """getter of cond_mat"""
        return self._cond_mat

    def _set_cond_mat(self, value):
        """setter of cond_mat"""
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
                "pyleecan.Classes", value.get("__class__"), "cond_mat"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "cond_mat")
            value = Material()
        check_var("cond_mat", value, "Material")
        self._cond_mat = value

        if self._cond_mat is not None:
            self._cond_mat.parent = self

    cond_mat = property(
        fget=_get_cond_mat,
        fset=_set_cond_mat,
        doc="""Material of the conductor

        :Type: Material
        """,
    )

    def _get_ins_mat(self):
        """getter of ins_mat"""
        return self._ins_mat

    def _set_ins_mat(self, value):
        """setter of ins_mat"""
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
                "pyleecan.Classes", value.get("__class__"), "ins_mat"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Material = import_class("pyleecan.Classes", "Material", "ins_mat")
            value = Material()
        check_var("ins_mat", value, "Material")
        self._ins_mat = value

        if self._ins_mat is not None:
            self._ins_mat.parent = self

    ins_mat = property(
        fget=_get_ins_mat,
        fset=_set_ins_mat,
        doc="""Material of the insulation

        :Type: Material
        """,
    )
