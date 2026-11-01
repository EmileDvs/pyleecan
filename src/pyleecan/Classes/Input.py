# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/Input.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/Input
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
from numpy import pi
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataLinspace import DataLinspace
from pyleecan.Classes.Norm_ref import Norm_ref
from pyleecan.Classes.Norm_indices import Norm_indices
from pyleecan.Classes.Norm_affine import Norm_affine

from pyleecan.Classes.ImportMatrixVal import ImportMatrixVal
from numpy import ndarray
from numpy import array, array_equal
from numpy import isnan
from pyleecan.Classes._check import InitUnKnowClassError


class Input(FrozenClass):
    """Starting data of the simulation"""

    VERSION = 1

    # cf Methods.Simulation.Input.comp_axes
    def comp_axes(
        self,
        axes_list,
        machine=None,
        axes_dict_in=None,
        is_periodicity_a=None,
        is_periodicity_t=None,
        per_a=None,
        is_antiper_a=None,
        per_t=None,
        is_antiper_t=None,
        is_periodicity_rotor=False,
    ):
        """Compute simulation axes such as time / angle / phase axes, with or without periodicities
        and including normalizations

        Parameters
        ----------
        self : Input
            an Input object
        machine : Machine
            a Machine object
        axes_list: list
            List of axes name to return in axes dict
        axes_dict: {Data}
            dict of axes containing time and angle axes (with or without (anti-)periodicity)
        is_periodicity_a: bool
            True if spatial periodicity is requested
        is_periodicity_t: bool
            True if time periodicity is requested
        per_a : int
            angle periodicity
        is_antiper_a : bool
            if the angle axis is antiperiodic
        per_t : int
            time periodicity
        is_antiper_t : bool
            if the time axis is antiperiodic
        is_periodicity_rotor: bool
            True to consider rotor periodicity over time instead of stator

        Returns
        -------
        axes_dict: {Data}
            dict of axes containing requested axes

        """
        if len(axes_list) == 0:
            raise Exception("axes_list should not be empty")

        if self.parent is not None:
            simu = self.parent
        else:
            simu = None

        if hasattr(simu, "parent") and simu.parent is not None:
            output = simu.parent
        else:
            output = None

        if (axes_list is None or len(axes_list) == 0) and (
            axes_dict_in is None or len(axes_dict_in) == 0
        ):
            raise Exception(
                "Cannot calculate axes if both axes list and axes dict are None"
            )

        if machine is None:
            # Fetch machine from input
            if hasattr(simu, "machine") and simu.machine is not None:
                machine = simu.machine
            else:
                raise Exception("Cannot calculate axes if simu.machine is None")

        # Get machine pole pair number
        p = machine.get_pole_pair_number()

        # Fill periodicity parameters that are None
        if (is_periodicity_a is not False or is_periodicity_t is not False) and (
            per_a is None
            or is_antiper_a is None
            or per_t is None
            or is_antiper_t is None
        ):
            if output is not None:
                # Get time and space (anti-)periodicities from the output
                (
                    per_a_0,
                    is_antiper_a_0,
                    per_t_0,
                    is_antiper_t_0,
                ) = output.get_machine_periodicity(is_rotor_ref=is_periodicity_rotor)
            else:
                # Compute time and space (anti-)periodicities from the machine
                per_a_0, is_antiper_a_0 = machine.comp_periodicity_spatial()
                if is_periodicity_rotor:
                    _, _, per_t_0, is_antiper_t_0 = machine.comp_periodicity_time()
                else:
                    per_t_0, is_antiper_t_0, _, _ = machine.comp_periodicity_time()

        if is_periodicity_t is None or is_periodicity_t:
            # Enforce None values to machine time periodicity
            per_t = per_t_0 if per_t is None else per_t
            is_antiper_t = is_antiper_t_0 if is_antiper_t is None else is_antiper_t
            if is_periodicity_t is None:
                # Check time periodicity is included
                is_periodicity_t = per_t > 1 or is_antiper_t
        elif not is_periodicity_t:
            # Remove time periodicity
            per_t = 1
            is_antiper_t = False

        if is_periodicity_a is None or is_periodicity_a:
            # Enforce None values to machine periodicity
            per_a = per_a_0 if per_a is None else per_a
            is_antiper_a = is_antiper_a_0 if is_antiper_a is None else is_antiper_a
            if is_periodicity_a is None:
                # Enforce requested angle periodicity
                is_periodicity_a = per_a > 1 or is_antiper_a
        elif not is_periodicity_a:
            # Remove angle periodicity
            per_a = 1
            is_antiper_a = False

        # Init axes_dict
        axes_dict = dict()

        # Get time axis
        if "time" in axes_list:
            # Check if Time is already in input dict of axes
            if axes_dict_in is not None and "time" in axes_dict_in:
                Time_in = axes_dict_in["time"]
            else:
                Time_in = None

            # Calculate time axis
            Time = self.comp_axis_time(p, per_t, is_antiper_t, Time_in)

            # Store time axis in dict
            axes_dict["time"] = Time

        # Get angle axis
        if "angle" in axes_list:
            # Airgap radius
            try:
                Rag = machine.comp_Rgap_mec()
            except (
                Exception
            ):  # Case where rotor is not defined yet (Rag is only used for angle axis normalization)
                Rag = 1

            # Check if Angle is already in input dict of axes
            if axes_dict_in is not None and "angle" in axes_dict_in:
                Angle_in = axes_dict_in["angle"]
            else:
                Angle_in = None

            # Calculate angle axis
            Angle = self.comp_axis_angle(p, Rag, per_a, is_antiper_a, Angle_in)

            # Store angle axis in dict
            axes_dict["angle"] = Angle

        if "phase_S" in axes_list:
            # Check if Phase is already in input dict of axes
            stator_label = "phase_" + machine.stator.get_label()
            if axes_dict_in is not None and stator_label in axes_dict_in:
                Phase_in = axes_dict_in[stator_label]
            else:
                Phase_in = None

            # Calculate stator phase axis
            Phase = self.comp_axis_phase(machine.stator, Phase_in)

            if Phase is not None:
                # Store phase axis in dict
                axes_dict[stator_label] = Phase

        if "phase_R" in axes_list:
            # Check if Phase is already in input dict of axes
            rotor_label = "phase_" + machine.rotor.get_label()
            if axes_dict_in is not None and rotor_label in axes_dict_in:
                Phase_in = axes_dict_in[rotor_label]
            else:
                Phase_in = None

            # Calculate rotor phase axis
            Phase = self.comp_axis_phase(machine.rotor, per_a, is_antiper_a, Phase_in)

            if Phase is not None:
                # Store phase axis in dict
                axes_dict[rotor_label] = Phase

        return axes_dict

    # cf Methods.Simulation.Input.comp_axis_angle
    def comp_axis_angle(self, p, Rag, per_a=None, is_antiper_a=None, Angle_in=None):
        """Compute angle axis with or without periodicities and including normalizations

        Parameters
        ----------
        self : Input
            an Input object
        p : int
            Machine pole pair number
        Rag: float
            Airgap mean radius [m]
        per_a : int
            angle periodicity
        is_antiper_a : bool
            if the angle axis is antiperiodic
        Angle_in: Data
            Input axis angle

        Returns
        -------
        Timee_in: Data
            Requested axis angle

        """

        norm_angle = {"space_order": Norm_ref(ref=p), "distance": Norm_ref(ref=1 / Rag)}

        # Compute angle axis based on input one
        if Angle_in is not None:
            if per_a is None or is_antiper_a is None:
                # Get periodicity from input Angle axis
                per_a, is_antiper_a = Angle_in.get_periodicity()
                per_a = int(per_a / 2) if is_antiper_a else per_a
            # Get Angle axis on requested periodicities
            Angle = Angle_in.get_axis_periodic(Nper=per_a, is_aper=is_antiper_a)
            Angle.normalizations = norm_angle

        # Create angle axis
        elif self.angle is None:
            # Create angle axis as a DataLinspace
            Angle = DataLinspace(
                name="angle",
                unit="rad",
                initial=0,
                final=2 * pi,
                number=self.Na_tot,
                include_endpoint=False,
                normalizations=norm_angle,
            )
            # Add angle (anti-)periodicity
            if per_a > 1 or is_antiper_a:
                Angle = Angle.get_axis_periodic(per_a, is_antiper_a)

        else:
            # Load angle data
            angle = self.angle.get_data()
            self.Na_tot = angle.size
            Angle = Data1D(
                name="angle", unit="rad", values=angle, normalizations=norm_angle
            )
            # Add angle (anti-)periodicity
            sym_a = dict()
            if is_antiper_a:
                sym_a["antiperiod"] = per_a
            elif per_a > 1:
                sym_a["period"] = per_a
            Angle.symmetries = sym_a
            Angle = Angle.to_linspace()

        return Angle

    # cf Methods.Simulation.Input.comp_axis_phase
    def comp_axis_phase(self, lamination, per_a=None, is_apera=None, Phase_in=None):
        """Compute phase axes for given lamination

        Parameters
        ----------
        self : Input
            an Input object
        lamination: Lamination
            a Lamination object
        per_a : int
            time periodicity
        Phase_in: Data
            Input phase axis

        Returns
        -------
        Phase: Data
            Requested phase axis
        """

        Phase = None

        if Phase_in is not None:
            Phase = Phase_in.copy()

        else:
            name_phase = lamination.get_name_phase()

            if len(name_phase) > 1:
                if per_a is not None and is_apera is not None:
                    sym_dict = dict()
                    if is_apera:
                        per_a *= 2
                        sym_dict["antiperiod"] = per_a
                    elif per_a > 1:
                        sym_dict["period"] = per_a

                    # Creating the data object
                    Phase = DataLinspace(
                        name="phase",
                        unit="rad",
                        initial=0,
                        final=2 * pi / per_a,
                        number=int(len(name_phase) / per_a),
                        include_endpoint=False,
                        symmetries=sym_dict,
                        normalizations={"bar_id": Norm_indices()},
                        is_overlay=True,
                        # filter={"Phase": []},
                    )
                else:
                    # Creating the data object
                    Phase = Data1D(
                        name="phase",
                        unit="rad",
                        values=name_phase,
                        is_components=True,
                        is_overlay=True,
                        filter={"Phase": []},
                    )
            elif len(name_phase) == 1:
                # Creating the data object
                Phase = DataLinspace(
                    name="phase",
                    unit="rad",
                    initial=0,
                    final=2 * pi,
                    number=1,
                    include_endpoint=False,
                    normalizations={"bar_id": Norm_indices()},
                    is_overlay=True,
                    # filter={"Phase": []},
                )

        return Phase

    # cf Methods.Simulation.Input.comp_axis_time
    def comp_axis_time(self, p, per_t=None, is_antiper_t=None, Time_in=None):
        """Compute time axis, with or without periodicities and including normalizations

        Parameters
        ----------
        self : Input
            an Input object
        p: int
            Number of pole pairs
        per_t : int
            time periodicity
        is_antiper_t : bool
            if the time axis is antiperiodic
        Time_in: Data
            Input time axis

        Returns
        -------
        Time: Data
            Requested Time axis
        """

        f_elec = self.OP.get_felec(p=p)
        N0 = self.OP.get_N0(p=p)
        A0 = self.angle_rotor_initial

        # Setup normalizations for time and angle axes
        norm_time = {
            "elec_order": Norm_ref(ref=f_elec),
            "mech_order": Norm_ref(ref=N0 / 60),
            "angle_elec": Norm_ref(ref=self.current_dir / (2 * pi * f_elec)),
            "angle_rotor": Norm_affine(
                slope=self.rot_dir * N0 * 360 / 60, offset=A0 * 180 / pi
            ),
        }

        # Compute Time axis based on input one
        if Time_in is not None:
            if per_t is None or is_antiper_t is None:
                # Get periodicity from input Time axis
                per_t, is_antiper_t = Time_in.get_periodicity()
                per_t = int(per_t / 2) if is_antiper_t else per_t
            # Get axis on given periodicities
            Time = Time_in.get_axis_periodic(Nper=per_t, is_aper=is_antiper_t)
            Time.normalizations = norm_time

        # Create time axis
        elif self.time is None:
            # Create time axis as a DataLinspace
            if self.t_final is not None:
                # Enforce final time
                t_final = self.t_final
            elif self.Nrev is not None:
                # Set final time depending on rotor speed and number of revolutions
                t_final = 60 / self.OP.N0 * self.Nrev
            else:
                # Set final time to p times the number of electrical periods
                t_final = p / f_elec
            # Create time axis as a DataLinspace
            Time = DataLinspace(
                name="time",
                unit="s",
                initial=0,
                final=t_final,
                number=self.Nt_tot,
                include_endpoint=False,
                normalizations=norm_time,
            )
            # Add time (anti-)periodicity
            if per_t > 1 or is_antiper_t:
                Time = Time.get_axis_periodic(per_t, is_antiper_t)
        else:
            # Load time data
            time = self.time.get_data()
            self.Nt_tot = time.size
            Time = Data1D(name="time", unit="s", values=time, normalizations=norm_time)
            # Add time (anti-)periodicity
            sym_t = dict()
            if is_antiper_t:
                sym_t["antiperiod"] = per_t
            elif per_t > 1:
                sym_t["period"] = per_t
            Time.symmetries = sym_t
            Time = Time.to_linspace()

        return Time

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
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
        self.parent = None
        self.time = time
        self.angle = angle
        self.Nt_tot = Nt_tot
        self.Nrev = Nrev
        self.Na_tot = Na_tot
        self.OP = OP
        self.t_final = t_final

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Input_str = ""
        if self.parent is None:
            Input_str += "parent = None " + linesep
        else:
            Input_str += "parent = " + str(type(self.parent)) + " object" + linesep
        if self.time is not None:
            tmp = self.time.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Input_str += "time = " + tmp
        else:
            Input_str += "time = None" + linesep + linesep
        if self.angle is not None:
            tmp = self.angle.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Input_str += "angle = " + tmp
        else:
            Input_str += "angle = None" + linesep + linesep
        Input_str += "Nt_tot = " + str(self.Nt_tot) + linesep
        Input_str += "Nrev = " + str(self.Nrev) + linesep
        Input_str += "Na_tot = " + str(self.Na_tot) + linesep
        if self.OP is not None:
            tmp = self.OP.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            Input_str += "OP = " + tmp
        else:
            Input_str += "OP = None" + linesep + linesep
        Input_str += "t_final = " + str(self.t_final) + linesep
        return Input_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.time != self.time:
            return False
        if other.angle != self.angle:
            return False
        if other.Nt_tot != self.Nt_tot:
            return False
        if other.Nrev != self.Nrev:
            return False
        if other.Na_tot != self.Na_tot:
            return False
        if other.OP != self.OP:
            return False
        if other.t_final != self.t_final:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if (other.time is None and self.time is not None) or (
            other.time is not None and self.time is None
        ):
            diff_list.append(name + ".time None mismatch")
        elif self.time is not None:
            diff_list.extend(
                self.time.compare(
                    other.time,
                    name=name + ".time",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.angle is None and self.angle is not None) or (
            other.angle is not None and self.angle is None
        ):
            diff_list.append(name + ".angle None mismatch")
        elif self.angle is not None:
            diff_list.extend(
                self.angle.compare(
                    other.angle,
                    name=name + ".angle",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._Nt_tot != self._Nt_tot:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nt_tot)
                    + ", other="
                    + str(other._Nt_tot)
                    + ")"
                )
                diff_list.append(name + ".Nt_tot" + val_str)
            else:
                diff_list.append(name + ".Nt_tot")
        if (
            other._Nrev is not None
            and self._Nrev is not None
            and isnan(other._Nrev)
            and isnan(self._Nrev)
        ):
            pass
        elif other._Nrev != self._Nrev:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Nrev) + ", other=" + str(other._Nrev) + ")"
                )
                diff_list.append(name + ".Nrev" + val_str)
            else:
                diff_list.append(name + ".Nrev")
        if other._Na_tot != self._Na_tot:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Na_tot)
                    + ", other="
                    + str(other._Na_tot)
                    + ")"
                )
                diff_list.append(name + ".Na_tot" + val_str)
            else:
                diff_list.append(name + ".Na_tot")
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
            other._t_final is not None
            and self._t_final is not None
            and isnan(other._t_final)
            and isnan(self._t_final)
        ):
            pass
        elif other._t_final != self._t_final:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._t_final)
                    + ", other="
                    + str(other._t_final)
                    + ")"
                )
                diff_list.append(name + ".t_final" + val_str)
            else:
                diff_list.append(name + ".t_final")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.time)
        S += getsizeof(self.angle)
        S += getsizeof(self.Nt_tot)
        S += getsizeof(self.Nrev)
        S += getsizeof(self.Na_tot)
        S += getsizeof(self.OP)
        S += getsizeof(self.t_final)
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

        Input_dict = dict()
        if self.time is None:
            Input_dict["time"] = None
        else:
            Input_dict["time"] = self.time.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.angle is None:
            Input_dict["angle"] = None
        else:
            Input_dict["angle"] = self.angle.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Input_dict["Nt_tot"] = self.Nt_tot
        Input_dict["Nrev"] = self.Nrev
        Input_dict["Na_tot"] = self.Na_tot
        if self.OP is None:
            Input_dict["OP"] = None
        else:
            Input_dict["OP"] = self.OP.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Input_dict["t_final"] = self.t_final
        # The class name is added to the dict for deserialisation purpose
        Input_dict["__class__"] = "Input"
        return Input_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
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

        if self.time is not None:
            self.time._set_None()
        if self.angle is not None:
            self.angle._set_None()
        self.Nt_tot = None
        self.Nrev = None
        self.Na_tot = None
        if self.OP is not None:
            self.OP._set_None()
        self.t_final = None

    def _get_time(self):
        """getter of time"""
        return self._time

    def _set_time(self, value):
        """setter of time"""
        ImportMatrix = import_class("pyleecan.Classes", "ImportMatrix", "time")
        ImportMatrixVal = import_class("pyleecan.Classes", "ImportMatrixVal", "time")
        if isinstance(value, str):  # Load from file
            value = load_init_dict(value)[1]
        if isinstance(value, ndarray):
            value = ImportMatrixVal(value=value)
        elif isinstance(value, list):
            value = ImportMatrixVal(value=array(value))
        elif value == -1:
            value = ImportMatrix()
        elif isinstance(value, dict):
            class_obj = import_class("pyleecan.Classes", value.get("__class__"), "time")
            value = class_obj(init_dict=value)
        check_var("time", value, "ImportMatrix")
        self._time = value

        if self._time is not None:
            self._time.parent = self

    time = property(
        fget=_get_time,
        fset=_set_time,
        doc="""Electrical time vector (no symmetry) to import

        :Type: ImportMatrix
        """,
    )

    def _get_angle(self):
        """getter of angle"""
        return self._angle

    def _set_angle(self, value):
        """setter of angle"""
        ImportMatrix = import_class("pyleecan.Classes", "ImportMatrix", "angle")
        ImportMatrixVal = import_class("pyleecan.Classes", "ImportMatrixVal", "angle")
        if isinstance(value, str):  # Load from file
            value = load_init_dict(value)[1]
        if isinstance(value, ndarray):
            value = ImportMatrixVal(value=value)
        elif isinstance(value, list):
            value = ImportMatrixVal(value=array(value))
        elif value == -1:
            value = ImportMatrix()
        elif isinstance(value, dict):
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "angle"
            )
            value = class_obj(init_dict=value)
        check_var("angle", value, "ImportMatrix")
        self._angle = value

        if self._angle is not None:
            self._angle.parent = self

    angle = property(
        fget=_get_angle,
        fset=_set_angle,
        doc="""Electrical position vector (no symmetry) to import

        :Type: ImportMatrix
        """,
    )

    def _get_Nt_tot(self):
        """getter of Nt_tot"""
        return self._Nt_tot

    def _set_Nt_tot(self, value):
        """setter of Nt_tot"""
        check_var("Nt_tot", value, "int", Vmin=1)
        self._Nt_tot = value

    Nt_tot = property(
        fget=_get_Nt_tot,
        fset=_set_Nt_tot,
        doc="""Time discretization

        :Type: int
        :min: 1
        """,
    )

    def _get_Nrev(self):
        """getter of Nrev"""
        return self._Nrev

    def _set_Nrev(self, value):
        """setter of Nrev"""
        check_var("Nrev", value, "float", Vmin=0)
        self._Nrev = value

    Nrev = property(
        fget=_get_Nrev,
        fset=_set_Nrev,
        doc="""Number of rotor revolution (to compute the final time)

        :Type: float
        :min: 0
        """,
    )

    def _get_Na_tot(self):
        """getter of Na_tot"""
        return self._Na_tot

    def _set_Na_tot(self, value):
        """setter of Na_tot"""
        check_var("Na_tot", value, "int", Vmin=1)
        self._Na_tot = value

    Na_tot = property(
        fget=_get_Na_tot,
        fset=_set_Na_tot,
        doc="""Angular discretization

        :Type: int
        :min: 1
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

    def _get_t_final(self):
        """getter of t_final"""
        return self._t_final

    def _set_t_final(self, value):
        """setter of t_final"""
        check_var("t_final", value, "float")
        self._t_final = value

    t_final = property(
        fget=_get_t_final,
        fset=_set_t_final,
        doc="""To enforce final time

        :Type: float
        """,
    )
