# File generated according to Generator/ClassesRef/Simulation/EEC.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/EEC"""

from os import linesep
from os.path import join
from sys import getsizeof

import numpy as np

from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass

from pyleecan.Functions.Electrical.dqh_transformation import n2dqh_DataTime
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class EEC(FrozenClass):
    """Equivalent Electrical Circuit abstract class"""

    VERSION = 1

    # cf Methods.Simulation.EEC.comp_fluxlinkage
    def comp_fluxlinkage(self, machine=None, OP=None, Nt_tot=None):
        """Compute flux linkage using magnetic model in self.fluxlink

        Parameters
        ----------
        self : EEC
            an EEC object
        machine: Machine
            a Machine object
        OP: OP
            an OP object
        Nt_tot:
            Number of time steps for magnetic calculation

        Returns
        ----------
        Phi_dqh_mean: ndarray
            Flux linkage in dqh frame
        Phi_wind: DataND
            Stator flux linkage Data object
        """

        Simu1 = import_class("pyleecan.Classes", "Simu1")
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
        MagFEMM = import_class("pyleecan.Classes", "MagFEMM")

        if self.fluxlink is None:
            mag_model = MagFEMM()
        else:
            mag_model = self.fluxlink.copy()

        self.get_logger().info("Compute flux linkage with FEMM")

        if machine is None:
            machine = self.get_machine_from_parent()

        # Get simulation name and result path
        if isinstance(machine.parent, Simu1) and machine.parent.name not in [None, ""]:
            simu_name = machine.parent.name + "_FluxLinkFEMM"
            path_result = (
                join(machine.parent.path_result, "FluxLinkFEMM")
                if machine.parent.path_result not in [None, ""]
                else None
            )
        elif machine.name not in [None, ""]:
            simu_name = machine.name + "_FluxLinkFEMM"
            path_result = None
        else:
            simu_name = "FluxLinkFEMM"
            path_result = None

        # Define simulation
        p = machine.get_pole_pair_number()
        simu = Simu1(
            elec=None, name=simu_name, path_result=path_result, machine=machine
        )

        simu.input = InputCurrent(OP=OP, Na_tot=200 * p)
        simu.mag = mag_model
        if Nt_tot is not None:
            simu.input.Nt_tot = Nt_tot
        else:
            simu.input.Nt_tot = int(max(simu.mag.nb_worker * 5, 10) * p)

        # Run Simulation
        out = simu.run()

        # Post-Process
        stator_label = machine.stator.get_label()

        Phi_wind = out.mag.Phi_wind[stator_label]

        Phidqh = n2dqh_DataTime(Phi_wind, phase_dir=out.elec.phase_dir)
        Phi_dqh_mean = Phidqh.get_along("time=mean", "phase")[Phidqh.symbol]

        return Phi_dqh_mean, Phi_wind

    # cf Methods.Simulation.EEC.comp_joule_losses
    def comp_joule_losses(self, out_dict, machine):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : EEC
            an EEC object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        machine : Machine
            a Machine object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        raise AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # cf Methods.Simulation.EEC.comp_parameters
    def comp_parameters(self):
        """Compute and set the parameter attributes of the EEC that are not set.

        Parameters
        ----------
        self : EEC
            an EEC object

        """

        raise AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # cf Methods.Simulation.EEC.comp_R1
    def comp_R1(self, R1_ref=None, T_ref=None):
        """Compute the stator phase resistance for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC
            an EEC object
        R1_ref : float
            reference resistance
        T_ref : float
            reference temperature

        """

        if R1_ref is None:
            # Compute at correct temperature
            machine = self.get_machine_from_parent()
            R1_ref = machine.stator.comp_resistance_wind(T=self.Tsta)
        elif T_ref is None:
            # Assume that the reference match EEC temperature (should not happend)
            pass
        else:  # Adpat the temperature
            # Get stator conductor
            machine = self.get_machine_from_parent()
            CondS = machine.stator.winding.conductor

            # Compute temperature effect on stator side
            Tfact1 = CondS.comp_temperature_effect(T_op=self.Tsta, T_ref=T_ref)
            R1_ref = R1_ref * Tfact1
        # Stator resistance
        self.R1 = R1_ref * self.Xkr_skinS

    # cf Methods.Simulation.EEC.comp_skin_effect
    def comp_skin_effect(self):
        """Compute the skin effect factors (update value in object)

        Parameters
        ----------
        self : EEC
            An EEC objects
        """

        assert self.OP is not None
        assert self.Tsta is not None
        assert self.Trot is not None
        machine = self.get_machine_from_parent()
        CondS = machine.stator.winding.conductor
        felec = self.OP.get_felec()

        # compute skin_effect on stator side
        self.Xkr_skinS = CondS.comp_skin_effect_resistance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

        self.Xke_skinS = CondS.comp_skin_effect_inductance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

    # cf Methods.Simulation.EEC.get_machine_from_parent
    def get_machine_from_parent(self):
        """Get machine object from parent

        Parameters
        ----------
        self : EEC
            an EEC object

        Returns
        ----------
        machine : Machine
            a Machine object
        """

        parent = self.parent
        # Try to find simulation parent (output.simu.elec.eec)
        while parent is not None and not hasattr(parent, "machine"):
            parent = parent.parent

        if parent is not None and hasattr(parent, "machine"):
            return parent.machine
        else:
            # Try to find output parent (output.elec.eec)
            parent = self.parent
            while parent is not None and not hasattr(parent, "simu"):
                parent = parent.parent
            if parent is not None:
                return parent.simu.machine
            else:
                return None

    # cf Methods.Simulation.EEC.solve
    def solve(self):
        """Compute the parameters dict for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC
            an EEC object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        raise AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # cf Methods.Simulation.EEC.solve_PWM
    def solve_PWM(self, output):
        """Get stator current harmonics due to PWM harmonics

        Parameters
        ----------
        self : EEC
            an EEC object
        output: Output
            An Output object
        is_dqh_freq: bool
            True to consider frequencies in dqh frame

        Returns
        ------
        Is_PWM : DataFreq
            Stator current harmonics as DataFreq
        """
        raise AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

    # cf Methods.Simulation.EEC.update_from_ref
    def update_from_ref(self, LUT_ref):
        """Compute and set the parameter attributes of the EEC from a reference LUT

        Parameters
        ----------
        self : EEC
            an EEC object
        LUT_ref : LUTdq
            a LUTdq object

        """

        raise AbstractClassError(
            "EEC is an abstract class, please create one of its daughters."
        )

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
        self.parent = None
        self.type_skin_effect = type_skin_effect
        self.OP = OP
        self.Tsta = Tsta
        self.Trot = Trot
        self.Xkr_skinS = Xkr_skinS
        self.Xke_skinS = Xke_skinS
        self.Xkr_skinR = Xkr_skinR
        self.Xke_skinR = Xke_skinR
        self.R1 = R1
        self.fluxlink = fluxlink

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        EEC_str = ""
        if self.parent is None:
            EEC_str += "parent = None " + linesep
        else:
            EEC_str += "parent = " + str(type(self.parent)) + " object" + linesep
        EEC_str += "type_skin_effect = " + str(self.type_skin_effect) + linesep
        if self.OP is not None:
            tmp = self.OP.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            EEC_str += "OP = " + tmp
        else:
            EEC_str += "OP = None" + linesep + linesep
        EEC_str += "Tsta = " + str(self.Tsta) + linesep
        EEC_str += "Trot = " + str(self.Trot) + linesep
        EEC_str += "Xkr_skinS = " + str(self.Xkr_skinS) + linesep
        EEC_str += "Xke_skinS = " + str(self.Xke_skinS) + linesep
        EEC_str += "Xkr_skinR = " + str(self.Xkr_skinR) + linesep
        EEC_str += "Xke_skinR = " + str(self.Xke_skinR) + linesep
        EEC_str += "R1 = " + str(self.R1) + linesep
        if self.fluxlink is not None:
            tmp = self.fluxlink.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            EEC_str += "fluxlink = " + tmp
        else:
            EEC_str += "fluxlink = None" + linesep + linesep
        return EEC_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.type_skin_effect != self.type_skin_effect:
            return False
        if other.OP != self.OP:
            return False
        if other.Tsta != self.Tsta:
            return False
        if other.Trot != self.Trot:
            return False
        if other.Xkr_skinS != self.Xkr_skinS:
            return False
        if other.Xke_skinS != self.Xke_skinS:
            return False
        if other.Xkr_skinR != self.Xkr_skinR:
            return False
        if other.Xke_skinR != self.Xke_skinR:
            return False
        if other.R1 != self.R1:
            return False
        if other.fluxlink != self.fluxlink:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._type_skin_effect != self._type_skin_effect:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_skin_effect)
                    + ", other="
                    + str(other._type_skin_effect)
                    + ")"
                )
                diff_list.append(name + ".type_skin_effect" + val_str)
            else:
                diff_list.append(name + ".type_skin_effect")
        if (other.OP is None and self.OP is not None) or (
            other.OP is not None and self.OP is None
        ):
            diff_list.append(name + ".OP None mismatch")
        elif self.OP is not None:
            diff_list.extend(
                self.OP.compare(
                    other.OP,
                    name=name + ".OP",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (
            other._Tsta is not None
            and self._Tsta is not None
            and np.isnan(other._Tsta)
            and np.isnan(self._Tsta)
        ):
            pass
        elif other._Tsta != self._Tsta:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Tsta) + ", other=" + str(other._Tsta) + ")"
                )
                diff_list.append(name + ".Tsta" + val_str)
            else:
                diff_list.append(name + ".Tsta")
        if (
            other._Trot is not None
            and self._Trot is not None
            and np.isnan(other._Trot)
            and np.isnan(self._Trot)
        ):
            pass
        elif other._Trot != self._Trot:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Trot) + ", other=" + str(other._Trot) + ")"
                )
                diff_list.append(name + ".Trot" + val_str)
            else:
                diff_list.append(name + ".Trot")
        if (
            other._Xkr_skinS is not None
            and self._Xkr_skinS is not None
            and np.isnan(other._Xkr_skinS)
            and np.isnan(self._Xkr_skinS)
        ):
            pass
        elif other._Xkr_skinS != self._Xkr_skinS:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Xkr_skinS)
                    + ", other="
                    + str(other._Xkr_skinS)
                    + ")"
                )
                diff_list.append(name + ".Xkr_skinS" + val_str)
            else:
                diff_list.append(name + ".Xkr_skinS")
        if (
            other._Xke_skinS is not None
            and self._Xke_skinS is not None
            and np.isnan(other._Xke_skinS)
            and np.isnan(self._Xke_skinS)
        ):
            pass
        elif other._Xke_skinS != self._Xke_skinS:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Xke_skinS)
                    + ", other="
                    + str(other._Xke_skinS)
                    + ")"
                )
                diff_list.append(name + ".Xke_skinS" + val_str)
            else:
                diff_list.append(name + ".Xke_skinS")
        if (
            other._Xkr_skinR is not None
            and self._Xkr_skinR is not None
            and np.isnan(other._Xkr_skinR)
            and np.isnan(self._Xkr_skinR)
        ):
            pass
        elif other._Xkr_skinR != self._Xkr_skinR:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Xkr_skinR)
                    + ", other="
                    + str(other._Xkr_skinR)
                    + ")"
                )
                diff_list.append(name + ".Xkr_skinR" + val_str)
            else:
                diff_list.append(name + ".Xkr_skinR")
        if (
            other._Xke_skinR is not None
            and self._Xke_skinR is not None
            and np.isnan(other._Xke_skinR)
            and np.isnan(self._Xke_skinR)
        ):
            pass
        elif other._Xke_skinR != self._Xke_skinR:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Xke_skinR)
                    + ", other="
                    + str(other._Xke_skinR)
                    + ")"
                )
                diff_list.append(name + ".Xke_skinR" + val_str)
            else:
                diff_list.append(name + ".Xke_skinR")
        if (
            other._R1 is not None
            and self._R1 is not None
            and np.isnan(other._R1)
            and np.isnan(self._R1)
        ):
            pass
        elif other._R1 != self._R1:
            if is_add_value:
                val_str = " (self=" + str(self._R1) + ", other=" + str(other._R1) + ")"
                diff_list.append(name + ".R1" + val_str)
            else:
                diff_list.append(name + ".R1")
        if (other.fluxlink is None and self.fluxlink is not None) or (
            other.fluxlink is not None and self.fluxlink is None
        ):
            diff_list.append(name + ".fluxlink None mismatch")
        elif self.fluxlink is not None:
            diff_list.extend(
                self.fluxlink.compare(
                    other.fluxlink,
                    name=name + ".fluxlink",
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
        S += getsizeof(self.type_skin_effect)
        S += getsizeof(self.OP)
        S += getsizeof(self.Tsta)
        S += getsizeof(self.Trot)
        S += getsizeof(self.Xkr_skinS)
        S += getsizeof(self.Xke_skinS)
        S += getsizeof(self.Xkr_skinR)
        S += getsizeof(self.Xke_skinR)
        S += getsizeof(self.R1)
        S += getsizeof(self.fluxlink)
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

        EEC_dict = dict()
        EEC_dict["type_skin_effect"] = self.type_skin_effect
        if self.OP is None:
            EEC_dict["OP"] = None
        else:
            EEC_dict["OP"] = self.OP.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        EEC_dict["Tsta"] = self.Tsta
        EEC_dict["Trot"] = self.Trot
        EEC_dict["Xkr_skinS"] = self.Xkr_skinS
        EEC_dict["Xke_skinS"] = self.Xke_skinS
        EEC_dict["Xkr_skinR"] = self.Xkr_skinR
        EEC_dict["Xke_skinR"] = self.Xke_skinR
        EEC_dict["R1"] = self.R1
        if self.fluxlink is None:
            EEC_dict["fluxlink"] = None
        else:
            EEC_dict["fluxlink"] = self.fluxlink.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        EEC_dict["__class__"] = "EEC"
        return EEC_dict

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

        self.type_skin_effect = None
        if self.OP is not None:
            self.OP._set_None()
        self.Tsta = None
        self.Trot = None
        self.Xkr_skinS = None
        self.Xke_skinS = None
        self.Xkr_skinR = None
        self.Xke_skinR = None
        self.R1 = None
        if self.fluxlink is not None:
            self.fluxlink._set_None()

    def _get_type_skin_effect(self):
        """getter of type_skin_effect"""
        return self._type_skin_effect

    def _set_type_skin_effect(self, value):
        """setter of type_skin_effect"""
        check_var("type_skin_effect", value, "int")
        self._type_skin_effect = value

    type_skin_effect = property(
        fget=_get_type_skin_effect,
        fset=_set_type_skin_effect,
        doc="""Skin effect for resistance and inductance

        :Type: int
        """,
    )

    def _get_OP(self):
        """getter of OP"""
        return self._OP

    def _set_OP(self, value):
        """setter of OP"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "OP")
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            OP = import_class("pyleecan.Classes", "OP", "OP")
            value = OP()
        check_var("OP", value, "OP")
        self._OP = value

        if self._OP is not None:
            self._OP.parent = self

    OP = property(
        fget=_get_OP,
        fset=_set_OP,
        doc="""Operating Point

        :Type: OP
        """,
    )

    def _get_Tsta(self):
        """getter of Tsta"""
        return self._Tsta

    def _set_Tsta(self, value):
        """setter of Tsta"""
        check_var("Tsta", value, "float")
        self._Tsta = value

    Tsta = property(
        fget=_get_Tsta,
        fset=_set_Tsta,
        doc="""Average stator temperature for operational EEC calculation

        :Type: float
        """,
    )

    def _get_Trot(self):
        """getter of Trot"""
        return self._Trot

    def _set_Trot(self, value):
        """setter of Trot"""
        check_var("Trot", value, "float")
        self._Trot = value

    Trot = property(
        fget=_get_Trot,
        fset=_set_Trot,
        doc="""Average rotor temperature for operational EEC calculation

        :Type: float
        """,
    )

    def _get_Xkr_skinS(self):
        """getter of Xkr_skinS"""
        return self._Xkr_skinS

    def _set_Xkr_skinS(self, value):
        """setter of Xkr_skinS"""
        check_var("Xkr_skinS", value, "float")
        self._Xkr_skinS = value

    Xkr_skinS = property(
        fget=_get_Xkr_skinS,
        fset=_set_Xkr_skinS,
        doc="""Skin effect coefficient for resistances at stator side

        :Type: float
        """,
    )

    def _get_Xke_skinS(self):
        """getter of Xke_skinS"""
        return self._Xke_skinS

    def _set_Xke_skinS(self, value):
        """setter of Xke_skinS"""
        check_var("Xke_skinS", value, "float")
        self._Xke_skinS = value

    Xke_skinS = property(
        fget=_get_Xke_skinS,
        fset=_set_Xke_skinS,
        doc="""Skin effect coefficient for inductances at stator side

        :Type: float
        """,
    )

    def _get_Xkr_skinR(self):
        """getter of Xkr_skinR"""
        return self._Xkr_skinR

    def _set_Xkr_skinR(self, value):
        """setter of Xkr_skinR"""
        check_var("Xkr_skinR", value, "float")
        self._Xkr_skinR = value

    Xkr_skinR = property(
        fget=_get_Xkr_skinR,
        fset=_set_Xkr_skinR,
        doc="""Skin effect coefficient for resistances at rotor side

        :Type: float
        """,
    )

    def _get_Xke_skinR(self):
        """getter of Xke_skinR"""
        return self._Xke_skinR

    def _set_Xke_skinR(self, value):
        """setter of Xke_skinR"""
        check_var("Xke_skinR", value, "float")
        self._Xke_skinR = value

    Xke_skinR = property(
        fget=_get_Xke_skinR,
        fset=_set_Xke_skinR,
        doc="""Skin effect coefficient for inductances at rotor side

        :Type: float
        """,
    )

    def _get_R1(self):
        """getter of R1"""
        return self._R1

    def _set_R1(self, value):
        """setter of R1"""
        check_var("R1", value, "float")
        self._R1 = value

    R1 = property(
        fget=_get_R1,
        fset=_set_R1,
        doc="""Stator phase resistance

        :Type: float
        """,
    )

    def _get_fluxlink(self):
        """getter of fluxlink"""
        return self._fluxlink

    def _set_fluxlink(self, value):
        """setter of fluxlink"""
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
                "pyleecan.Classes", value.get("__class__"), "fluxlink"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnetics = import_class("pyleecan.Classes", "Magnetics", "fluxlink")
            value = Magnetics()
        check_var("fluxlink", value, "Magnetics")
        self._fluxlink = value

        if self._fluxlink is not None:
            self._fluxlink.parent = self

    fluxlink = property(
        fget=_get_fluxlink,
        fset=_set_fluxlink,
        doc="""Magnetic model for flux linkage calculation

        :Type: Magnetics
        """,
    )

    class AbstractClassError(Exception):
        pass


AbstractClassError = EEC.AbstractClassError
