# File generated according to Generator/ClassesRef/Simulation/InputCurrent.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/InputCurrent"""

from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.InputVoltage import InputVoltage

from pyleecan.Classes._check import check_var
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataFreq import DataFreq
from pyleecan.Classes.DataTime import DataTime
from pyleecan.Classes.ElecLUTdq import ElecLUTdq
from pyleecan.Functions.Electrical.dqh_transformation import (
    get_phase_dir,
    n2dqh_DataTime,
)
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save


class InputCurrent(InputVoltage):
    """Input to skip the electrical module and start with the magnetic one"""

    VERSION = 1

    # cf Methods.Simulation.InputCurrent.gen_input
    def gen_input(self):
        """Generate the input for the magnetic module (electrical output)

        Parameters
        ----------
        self : InputCurrent
            An InputCurrent object
        """

        # Call InputVoltage.gen_input()
        InputVoltage.gen_input(self)

        # Get simulation and outputs
        simu = self.parent
        output = simu.parent
        outelec = output.elec

        # Number of winding phases for stator/rotor
        if simu.machine is not None:
            qs = len(simu.machine.stator.get_name_phase())
            qr = len(simu.machine.rotor.get_name_phase())
        else:
            qs = 0
            qr = 0

        if outelec.axes_dict is not None and "time" in outelec.axes_dict:
            # Get time axis
            Time = outelec.axes_dict["time"]

        # Load and check Is
        if qs > 0:
            if qs == 6 and simu.machine.stator.winding.dual_tri_phase_shift is not None:
                Is_val = np.zeros((1, 6), dtype=complex)
                Id = self.OP.get_Id_Iq()["Id"]
                Iq = self.OP.get_Id_Iq()["Iq"]
                I0 = np.sqrt(Id**2 + Iq**2) * np.sqrt(2)
                if Iq == 0:
                    phi0 = 0 if Id >= 0 else -np.pi
                else:
                    phi0 = np.arctan(Id / Iq) - np.pi / 2
                if not simu.machine.stator.winding.is_wye:
                    I0 = I0 / np.sqrt(3)
                    phi0 = phi0 + np.pi / 6
                Is_val[0, 0] = I0 * np.exp(1j * phi0)
                Is_val[0, 1] = I0 * np.exp(
                    1j * (phi0 + simu.machine.stator.winding.dual_tri_phase_shift)
                )
                Is_val[0, 2] = I0 * np.exp(1j * (phi0 + 2 * np.pi / 3))
                Is_val[0, 3] = I0 * np.exp(
                    1j
                    * (
                        phi0
                        + 2 * np.pi / 3
                        + simu.machine.stator.winding.dual_tri_phase_shift
                    )
                )
                Is_val[0, 4] = I0 * np.exp(1j * (phi0 + 4 * np.pi / 3))
                Is_val[0, 5] = I0 * np.exp(
                    1j
                    * (
                        phi0
                        + 4 * np.pi / 3
                        + simu.machine.stator.winding.dual_tri_phase_shift
                    )
                )
                felec = self.OP.N0 * simu.machine.get_pole_pair_number() / 60
                # Create Data object
                Phases = Data1D(
                    name="phase",
                    unit="",
                    values=["A", "A2", "B", "B2", "C", "C2"],
                    is_components=True,
                )
                Freqs = Data1D(
                    values=[felec],
                    unit="Hz",
                    name="freqs",
                    normalizations=Time.normalizations.copy(),
                )
                Is = DataFreq(
                    name="Stator current",
                    unit="A",
                    symbol="I_s",
                    axes=[Freqs, Phases],
                    values=Is_val,
                )
                outelec.OP = self.OP
                outelec.Is = Is.get_data_along(
                    "time=axis_data",
                    "phase",
                    axis_data={"time": Time.get_values(is_smallestperiod=True)},
                )
                outelec.Is.axes[0].symmetries = Time.symmetries.copy()
            elif self.Is is None:
                if (
                    self.OP.get_Id_Iq()["Id"] is None
                    and self.OP.get_Id_Iq()["Iq"] is None
                ):
                    if not isinstance(simu.elec, ElecLUTdq):
                        raise InputError(
                            "InputCurrent.Is, InputCurrent.OP.Id_ref, and InputCurrent.OP.Iq_ref missing"
                        )
                else:
                    outelec.OP = self.OP
                    outelec.Is = None
            else:
                Is_val = self.Is.get_data()
                Nt_per = Time.get_length(is_smallestperiod=True)
                Phase_S = outelec.axes_dict["phase_" + simu.machine.stator.get_label()]
                try:
                    # Get phase_dir from Is
                    phase_dir = get_phase_dir(Is_val, current_dir=outelec.current_dir)
                    if phase_dir != outelec.phase_dir:
                        self.get_logger().warning(
                            "Enforcing outelec.phase_dir="
                            + str(phase_dir)
                            + " to comply with input current"
                        )
                        outelec.phase_dir = phase_dir
                except Exception:
                    # Cannot calculate phase_dir
                    self.get_logger().warning(
                        "phase_dir cannot be calculated, please make sure that input.phase_dir="
                        + str(outelec.phase_dir)
                        + " is compliant with enforced currents"
                    )
                try:
                    # Creating the data object
                    Is = DataTime(
                        name="Stator current",
                        unit="A",
                        symbol="I_s",
                        axes=[Time, Phase_S],
                        values=Is_val,
                    )
                except Exception:
                    raise InputError(
                        "InputCurrent.Is must be a matrix with the shape "
                        + str((Nt_per, qs))
                        + " (len(time), stator phase number), "
                        + str(Is_val.shape)
                        + " returned"
                    )
                # Compute corresponding Id/Iq reference
                Idq = n2dqh_DataTime(
                    Is,
                    is_dqh_rms=True,
                    phase_dir=outelec.phase_dir,
                )
                Idq_mean = Idq.get_along("time=mean", "phase")[Is.symbol]
                # Store currents in OutElec
                outelec.OP.set_Id_Iq(Idq_mean[0], Idq_mean[1])
                outelec.Is = Is

            if self.Is_harm is not None:
                # Enforce current harmonics
                # TODO: merge Is_harm and Is_fund
                outelec.Is_harm = self.Is_harm.get_data()

        # Load and check if Ir is needed
        if qr > 0:
            Nt_per = Time.get_length(is_smallestperiod=True)
            Phase_R = outelec.axes_dict["phase_" + simu.machine.rotor.get_label()]
            qr_per = Phase_R.get_length(is_smallestperiod=True)
            if hasattr(self.OP, "If_ref"):  # WRSM case
                Ir_val = np.ones((Nt_per, qr_per)) * self.OP.If_ref
            elif self.Ir is None:
                Ir_val = np.zeros((Nt_per, qr_per))
            else:
                Ir_val = self.Ir.get_data()
                if Ir_val.ndim == 1:
                    # time axis is squeeze, putting it back to first dimension
                    Ir_val = Ir_val[None, :]
                if Ir_val.shape[1] > qr_per:
                    Ir_val = Ir_val[:, :qr_per]
                    self.get_logger().info(
                        "Restrict input rotor bar currents to smallest spatial periodicity"
                    )

            try:
                Ir = DataTime(
                    name="Rotor current",
                    unit="A",
                    symbol="Ir",
                    axes=[Time, Phase_R],
                    values=Ir_val,
                )
            except Exception:
                raise InputError(
                    "InputCurrent.Ir must be a matrix with the shape "
                    + str((Nt_per, qr_per))
                    + " (len(time), rotor phase number), "
                    + str(Ir_val.shape)
                    + " returned"
                )

            outelec.Ir = Ir

        if outelec.PWM is not None:
            Udq_dict = outelec.OP.get_Ud_Uq()
            Ud_ref, Uq_ref = Udq_dict["Ud"], Udq_dict["Uq"]
            # Check PWM phase voltage consistency in current driven mode
            if outelec.PWM.U0 is not None or Ud_ref is not None or Uq_ref is not None:
                if outelec.PWM.U0 is not None:
                    self.get_logger().warning(
                        "Neglecting U0 given as input of PWM object since voltage will be calculated"
                    )
                if Ud_ref is not None or Uq_ref is not None:
                    self.get_logger().warning(
                        "Neglecting Ud_ref/Uq_ref given as input since voltage will be calculated"
                    )
            # Set all voltages to None since they will be calculated by Electrical model
            outelec.PWM.U0 = None
            outelec.PWM.Phi0 = None
            outelec.OP.Ud_ref = None
            outelec.OP.Uq_ref = None

    # cf Methods.Simulation.InputCurrent.set_Id_Iq
    def set_Id_Iq(self, I0, Phi0):
        """Set Id_ref and Iq_ref according to I0, Phi0

        Parameters
        ----------
        self : InputCurrent
            An InputCurrent object
        I0 : float
            Current amplitude [Arms]
        Phi0 : float
            Current phase [rad]
        """

        self.OP.Id_ref = I0 * np.cos(Phi0)
        self.OP.Iq_ref = I0 * np.sin(Phi0)
        if abs(self.OP.Id_ref) < 1e-10:
            self.OP.Id_ref = 0
        if abs(self.OP.Iq_ref) < 1e-10:
            self.OP.Iq_ref = 0

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Is=None,
        Ir=None,
        Is_harm=None,
        rot_dir=None,
        angle_rotor_initial=0,
        PWM=None,
        phase_dir=None,
        current_dir=None,
        is_periodicity_t=False,
        is_periodicity_a=False,
        is_generator=False,
        time=None,
        angle=None,
        Nt_tot=2048,
        Nrev=None,
        Na_tot=2048,
        OP=None,
        t_final=None,
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
            if "Is" in list(init_dict.keys()):
                Is = init_dict["Is"]
            if "Ir" in list(init_dict.keys()):
                Ir = init_dict["Ir"]
            if "Is_harm" in list(init_dict.keys()):
                Is_harm = init_dict["Is_harm"]
            if "rot_dir" in list(init_dict.keys()):
                rot_dir = init_dict["rot_dir"]
            if "angle_rotor_initial" in list(init_dict.keys()):
                angle_rotor_initial = init_dict["angle_rotor_initial"]
            if "PWM" in list(init_dict.keys()):
                PWM = init_dict["PWM"]
            if "phase_dir" in list(init_dict.keys()):
                phase_dir = init_dict["phase_dir"]
            if "current_dir" in list(init_dict.keys()):
                current_dir = init_dict["current_dir"]
            if "is_periodicity_t" in list(init_dict.keys()):
                is_periodicity_t = init_dict["is_periodicity_t"]
            if "is_periodicity_a" in list(init_dict.keys()):
                is_periodicity_a = init_dict["is_periodicity_a"]
            if "is_generator" in list(init_dict.keys()):
                is_generator = init_dict["is_generator"]
            if "time" in list(init_dict.keys()):
                time = init_dict["time"]
            if "angle" in list(init_dict.keys()):
                angle = init_dict["angle"]
            if "Nt_tot" in list(init_dict.keys()):
                Nt_tot = init_dict["Nt_tot"]
            if "Nrev" in list(init_dict.keys()):
                Nrev = init_dict["Nrev"]
            if "Na_tot" in list(init_dict.keys()):
                Na_tot = init_dict["Na_tot"]
            if "OP" in list(init_dict.keys()):
                OP = init_dict["OP"]
            if "t_final" in list(init_dict.keys()):
                t_final = init_dict["t_final"]
        # Set the properties (value check and convertion are done in setter)
        self.Is = Is
        self.Ir = Ir
        self.Is_harm = Is_harm
        # Call InputVoltage init
        super(InputCurrent, self).__init__(
            rot_dir=rot_dir,
            angle_rotor_initial=angle_rotor_initial,
            PWM=PWM,
            phase_dir=phase_dir,
            current_dir=current_dir,
            is_periodicity_t=is_periodicity_t,
            is_periodicity_a=is_periodicity_a,
            is_generator=is_generator,
            time=time,
            angle=angle,
            Nt_tot=Nt_tot,
            Nrev=Nrev,
            Na_tot=Na_tot,
            OP=OP,
            t_final=t_final,
        )
        # The class is frozen (in InputVoltage init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        InputCurrent_str = ""
        # Get the properties inherited from InputVoltage
        InputCurrent_str += super(InputCurrent, self).__str__()
        if self.Is is not None:
            tmp = self.Is.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            InputCurrent_str += "Is = " + tmp
        else:
            InputCurrent_str += "Is = None" + linesep + linesep
        if self.Ir is not None:
            tmp = self.Ir.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            InputCurrent_str += "Ir = " + tmp
        else:
            InputCurrent_str += "Ir = None" + linesep + linesep
        if self.Is_harm is not None:
            tmp = self.Is_harm.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            InputCurrent_str += "Is_harm = " + tmp
        else:
            InputCurrent_str += "Is_harm = None" + linesep + linesep
        return InputCurrent_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from InputVoltage
        if not super(InputCurrent, self).__eq__(other):
            return False
        if other.Is != self.Is:
            return False
        if other.Ir != self.Ir:
            return False
        if other.Is_harm != self.Is_harm:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from InputVoltage
        diff_list.extend(
            super(InputCurrent, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (other.Is is None and self.Is is not None) or (
            other.Is is not None and self.Is is None
        ):
            diff_list.append(name + ".Is None mismatch")
        elif self.Is is not None:
            diff_list.extend(
                self.Is.compare(
                    other.Is,
                    name=name + ".Is",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.Ir is None and self.Ir is not None) or (
            other.Ir is not None and self.Ir is None
        ):
            diff_list.append(name + ".Ir None mismatch")
        elif self.Ir is not None:
            diff_list.extend(
                self.Ir.compare(
                    other.Ir,
                    name=name + ".Ir",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.Is_harm is None and self.Is_harm is not None) or (
            other.Is_harm is not None and self.Is_harm is None
        ):
            diff_list.append(name + ".Is_harm None mismatch")
        elif self.Is_harm is not None:
            diff_list.extend(
                self.Is_harm.compare(
                    other.Is_harm,
                    name=name + ".Is_harm",
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

        # Get size of the properties inherited from InputVoltage
        S += super(InputCurrent, self).__sizeof__()
        S += getsizeof(self.Is)
        S += getsizeof(self.Ir)
        S += getsizeof(self.Is_harm)
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

        # Get the properties inherited from InputVoltage
        InputCurrent_dict = super(InputCurrent, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.Is is None:
            InputCurrent_dict["Is"] = None
        else:
            InputCurrent_dict["Is"] = self.Is.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.Ir is None:
            InputCurrent_dict["Ir"] = None
        else:
            InputCurrent_dict["Ir"] = self.Ir.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.Is_harm is None:
            InputCurrent_dict["Is_harm"] = None
        else:
            InputCurrent_dict["Is_harm"] = self.Is_harm.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        InputCurrent_dict["__class__"] = "InputCurrent"
        return InputCurrent_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.Is is None:
            Is_val = None
        else:
            Is_val = self.Is.copy()
        if self.Ir is None:
            Ir_val = None
        else:
            Ir_val = self.Ir.copy()
        if self.Is_harm is None:
            Is_harm_val = None
        else:
            Is_harm_val = self.Is_harm.copy()
        rot_dir_val = self.rot_dir
        angle_rotor_initial_val = self.angle_rotor_initial
        if self.PWM is None:
            PWM_val = None
        else:
            PWM_val = self.PWM.copy()
        phase_dir_val = self.phase_dir
        current_dir_val = self.current_dir
        is_periodicity_t_val = self.is_periodicity_t
        is_periodicity_a_val = self.is_periodicity_a
        is_generator_val = self.is_generator
        if self.time is None:
            time_val = None
        else:
            time_val = self.time.copy()
        if self.angle is None:
            angle_val = None
        else:
            angle_val = self.angle.copy()
        Nt_tot_val = self.Nt_tot
        Nrev_val = self.Nrev
        Na_tot_val = self.Na_tot
        if self.OP is None:
            OP_val = None
        else:
            OP_val = self.OP.copy()
        t_final_val = self.t_final
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            Is=Is_val,
            Ir=Ir_val,
            Is_harm=Is_harm_val,
            rot_dir=rot_dir_val,
            angle_rotor_initial=angle_rotor_initial_val,
            PWM=PWM_val,
            phase_dir=phase_dir_val,
            current_dir=current_dir_val,
            is_periodicity_t=is_periodicity_t_val,
            is_periodicity_a=is_periodicity_a_val,
            is_generator=is_generator_val,
            time=time_val,
            angle=angle_val,
            Nt_tot=Nt_tot_val,
            Nrev=Nrev_val,
            Na_tot=Na_tot_val,
            OP=OP_val,
            t_final=t_final_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        if self.Is is not None:
            self.Is._set_None()
        if self.Ir is not None:
            self.Ir._set_None()
        if self.Is_harm is not None:
            self.Is_harm._set_None()
        # Set to None the properties inherited from InputVoltage
        super(InputCurrent, self)._set_None()

    def _get_Is(self):
        """getter of Is"""
        return self._Is

    def _set_Is(self, value):
        """setter of Is"""
        ImportMatrix = import_class("pyleecan.Classes", "ImportMatrix", "Is")
        ImportMatrixVal = import_class("pyleecan.Classes", "ImportMatrixVal", "Is")
        if isinstance(value, str):  # Load from file
            value = load_init_dict(value)[1]
        if isinstance(value, np.ndarray):
            value = ImportMatrixVal(value=value)
        elif isinstance(value, list):
            value = ImportMatrixVal(value=np.array(value))
        elif value == -1:
            value = ImportMatrix()
        elif isinstance(value, dict):
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "Is")
            value = class_obj(init_dict=value)
        check_var("Is", value, "ImportMatrix")
        self._Is = value

        if self._Is is not None:
            self._Is.parent = self

    Is = property(
        fget=_get_Is,
        fset=_set_Is,
        doc="""Stator currents as a function of time (each column correspond to one phase) to import

        :Type: ImportMatrix
        """,
    )

    def _get_Ir(self):
        """getter of Ir"""
        return self._Ir

    def _set_Ir(self, value):
        """setter of Ir"""
        ImportMatrix = import_class("pyleecan.Classes", "ImportMatrix", "Ir")
        ImportMatrixVal = import_class("pyleecan.Classes", "ImportMatrixVal", "Ir")
        if isinstance(value, str):  # Load from file
            value = load_init_dict(value)[1]
        if isinstance(value, np.ndarray):
            value = ImportMatrixVal(value=value)
        elif isinstance(value, list):
            value = ImportMatrixVal(value=np.array(value))
        elif value == -1:
            value = ImportMatrix()
        elif isinstance(value, dict):
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "Ir")
            value = class_obj(init_dict=value)
        check_var("Ir", value, "ImportMatrix")
        self._Ir = value

        if self._Ir is not None:
            self._Ir.parent = self

    Ir = property(
        fget=_get_Ir,
        fset=_set_Ir,
        doc="""Rotor currents as a function of time (each column correspond to one phase) to import

        :Type: ImportMatrix
        """,
    )

    def _get_Is_harm(self):
        """getter of Is_harm"""
        return self._Is_harm

    def _set_Is_harm(self, value):
        """setter of Is_harm"""
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
                "pyleecan.Classes", value.get("__class__"), "Is_harm"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            ImportData = import_class("pyleecan.Classes", "ImportData", "Is_harm")
            value = ImportData()
        check_var("Is_harm", value, "ImportData")
        self._Is_harm = value

        if self._Is_harm is not None:
            self._Is_harm.parent = self

    Is_harm = property(
        fget=_get_Is_harm,
        fset=_set_Is_harm,
        doc="""Stator harmonic currents

        :Type: ImportData
        """,
    )

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""

        pass


InputError = InputCurrent.InputError
