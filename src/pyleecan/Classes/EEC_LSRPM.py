# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/EEC_LSRPM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/EEC_LSRPM
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - solve: method function is missing

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.EEC import EEC

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from pyleecan.Methods.Simulation.EEC_LSRPM.solve import solve

import numpy as np
from pyleecan.Classes._check import InitUnKnowClassError


class EEC_LSRPM(EEC):
    """Electrical Equivalent Circuit for LSRPM"""

    VERSION = 1

    # cf Methods.Simulation.EEC_LSRPM.comp_joule_losses
    def comp_joule_losses(self, output):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : Electrical
            an Electrical object
        output : Output
            an Output object
        """

        qs = output.simu.machine.stator.winding.qs
        I_ds = output.elec.Ids_ref
        I_qs = output.elec.Iqs_ref
        I_da = output.elec.Ida_ref
        I_qa = output.elec.Iqa_ref

        R_s = self.parameters["R_s"]
        R_a = self.parameters["R_a"]

        # Id and Iq are in RMS
        Pj_losses = qs * (R_s * (I_ds**2 + I_qs**2) + R_a * (I_da**2 + I_qa**2))

        output.elec.Pj_losses = Pj_losses

    # cf Methods.Simulation.EEC_LSRPM.comp_parameters
    def comp_parameters(self, output, Tsta=None, Trot=None):
        """Compute the parameters dict for the equivalent electrical circuit:
        resistance, inductance and back electromotive force
        Parameters
        ----------
        self : EEC_LSRPM
            an EEC_LSRPM object
        output : Output
            an Output object
        """
        machine = output.simu.machine
        p = machine.rotor.winding.p
        PAR = self.parameters

        if self.N0 is None and self.felec is None:
            N0 = 100 * 60 / p
            felec = 100
        elif self.N0 is None and self.felec is not None:
            N0 = self.felec * 60 / p
        elif self.N0 is not None and self.felec is None:
            N0 = self.N0
            felec = N0 / 60 * p
        else:
            N0 = self.N0
            felec = self.felec

        N_s = machine.stator.winding.comp_Ntspc()  # stator number of turns
        # TODO defind the method "comp_N_auxiliary"
        # N_a = machine.stator.winding.comp_N_auxiliary() # damper winding number of turns
        norm = 1  # rotor - stator transformation factor N_a=N_s

        self.parameters["norm"] = norm

        Tws = 20 if "Tws" not in self.parameters else self.parameter["Tws"]
        Twr = 20 if "Twr" not in self.parameters else self.parameter["Twr"]

        # TODO all methods should be verfied for PMSM with damper winding
        if "R_s" not in self.parameters or self.parameters["Rs"] is None:
            # 3 phase equivalent stator resistance
            self.parameters["Rs"] = machine.stator.comp_resistance_wind(T=Tws)

        if "R_a" not in self.parameters or self.parameters["R_a"] is None:
            # 3 phase equivalent damper resistance
            # TODO have to defind the method"comp_resistance_damper_winding"
            R_a = machine.rotor.comp_resistance_damper_winding(T=Twr, qs=3)
            self.parameters["R_a"] = norm**2 * R_a

        if "Phi_m" not in PAR:
            PAR["Phi_m"] = self.fluxlink.comp_fluxlinkage(output)

        if "C_a" not in PAR:
            self.parameters["C_a"] = 0  # Not sure

        is_comp_ind = False
        # check for complete parameter set
        # (there may be some redundancy here but it seems simplier to implement)
        # if not all(k in PAR for k in ("Phid", "Phiq", "Ld", "Lq")):
        #     is_comp_ind = True

        # check for d- and q-current (change)
        if "I_ds" not in PAR or PAR["I_ds"] != output.elec.Ids_ref:
            PAR["I_ds"] = output.elec.Ids_ref
            is_comp_ind = True

        if "I_qs" not in PAR or PAR["I_qs"] != output.elec.Iqs_ref:
            PAR["I_qs"] = output.elec.Iqs_ref
            is_comp_ind = True

        if "I_da" not in PAR or PAR["I_da"] != output.elec.Ida_ref:
            PAR["I_da"] = output.elec.Ida_ref
            is_comp_ind = True

        if "I_qa" not in PAR or PAR["I_qa"] != output.elec.Iqa_ref:
            PAR["I_qa"] = output.elec.Iqa_ref
            is_comp_ind = True

        if "L_dss" not in self.parameters or self.parameters["L_dss"] is None:
            is_comp_ind = True

        if "L_dmu" not in self.parameters or self.parameters["L_dmu"] is None:
            is_comp_ind = True

        if "L_dsa" not in self.parameters or self.parameters["L_dsa"] is None:
            is_comp_ind = True

        if "L_daa" not in self.parameters or self.parameters["L_daa"] is None:
            is_comp_ind = True

        if "L_qss" not in self.parameters or self.parameters["L_qss"] is None:
            is_comp_ind = True

        if "L_qmu" not in self.parameters or self.parameters["L_qmu"] is None:
            is_comp_ind = True

        if "Lr_qaa" not in self.parameters or self.parameters["Lr_qaa"] is None:
            is_comp_ind = True

        # compute inductance if necessary
        if is_comp_ind:
            print("We will return soon")
            print("Please input all variables")

    # cf Methods.Simulation.EEC_LSRPM.solve
    solve = solve
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        type_skin_effect=1,
        OP=None,
        Tsta=20,
        Trot=20,
        Xkr_skinS=1,
        Xke_skinS=1,
        Xkr_skinR=1,
        Xke_skinR=1,
        R1=None,
        fluxlink=None,
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
            if "type_skin_effect" in list(init_dict.keys()):
                type_skin_effect = init_dict["type_skin_effect"]
            if "OP" in list(init_dict.keys()):
                OP = init_dict["OP"]
            if "Tsta" in list(init_dict.keys()):
                Tsta = init_dict["Tsta"]
            if "Trot" in list(init_dict.keys()):
                Trot = init_dict["Trot"]
            if "Xkr_skinS" in list(init_dict.keys()):
                Xkr_skinS = init_dict["Xkr_skinS"]
            if "Xke_skinS" in list(init_dict.keys()):
                Xke_skinS = init_dict["Xke_skinS"]
            if "Xkr_skinR" in list(init_dict.keys()):
                Xkr_skinR = init_dict["Xkr_skinR"]
            if "Xke_skinR" in list(init_dict.keys()):
                Xke_skinR = init_dict["Xke_skinR"]
            if "R1" in list(init_dict.keys()):
                R1 = init_dict["R1"]
            if "fluxlink" in list(init_dict.keys()):
                fluxlink = init_dict["fluxlink"]
        # Set the properties (value check and convertion are done in setter)
        # Call EEC init
        super(EEC_LSRPM, self).__init__(
            type_skin_effect=type_skin_effect,
            OP=OP,
            Tsta=Tsta,
            Trot=Trot,
            Xkr_skinS=Xkr_skinS,
            Xke_skinS=Xke_skinS,
            Xkr_skinR=Xkr_skinR,
            Xke_skinR=Xke_skinR,
            R1=R1,
            fluxlink=fluxlink,
        )
        # The class is frozen (in EEC init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        EEC_LSRPM_str = ""
        # Get the properties inherited from EEC
        EEC_LSRPM_str += super(EEC_LSRPM, self).__str__()
        return EEC_LSRPM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from EEC
        if not super(EEC_LSRPM, self).__eq__(other):
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from EEC
        diff_list.extend(
            super(EEC_LSRPM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from EEC
        S += super(EEC_LSRPM, self).__sizeof__()
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

        # Get the properties inherited from EEC
        EEC_LSRPM_dict = super(EEC_LSRPM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        EEC_LSRPM_dict["__class__"] = "EEC_LSRPM"
        return EEC_LSRPM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        type_skin_effect_val = self.type_skin_effect
        if self.OP is None:
            OP_val = None
        else:
            OP_val = self.OP.copy()
        Tsta_val = self.Tsta
        Trot_val = self.Trot
        Xkr_skinS_val = self.Xkr_skinS
        Xke_skinS_val = self.Xke_skinS
        Xkr_skinR_val = self.Xkr_skinR
        Xke_skinR_val = self.Xke_skinR
        R1_val = self.R1
        if self.fluxlink is None:
            fluxlink_val = None
        else:
            fluxlink_val = self.fluxlink.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            type_skin_effect=type_skin_effect_val,
            OP=OP_val,
            Tsta=Tsta_val,
            Trot=Trot_val,
            Xkr_skinS=Xkr_skinS_val,
            Xke_skinS=Xke_skinS_val,
            Xkr_skinR=Xkr_skinR_val,
            Xke_skinR=Xke_skinR_val,
            R1=R1_val,
            fluxlink=fluxlink_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from EEC
        super(EEC_LSRPM, self)._set_None()
