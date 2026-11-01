# File generated according to Generator/ClassesRef/Simulation/Magnetics.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/Magnetics"""

from os import linesep
from sys import getsizeof

import numpy as np
from pyleecan.Classes.MeshSolution import MeshSolution
from pyleecan.Classes.SliceModel import SliceModel
from pyleecan.Classes._check import check_var
from pyleecan.Classes._frozen import FrozenClass
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class Magnetics(FrozenClass):
    """Magnetic module abstract object"""

    VERSION = 1

    # cf Methods.Simulation.Magnetics.comp_axes
    def comp_axes(self, output):
        """Compute the axes required in any Magnetics module

        Parameters
        ----------
        self : Magnetic
            a Magnetic object
        output : Output
            an Output object (to update)

        Returns
        -------
        axes_dict: {Data}
            Dict containing Time and Angle axes including (anti-)periodicties used in any Magnetics module

        """

        # Get geometry output
        outgeo = output.geo

        # Get axis dict from OutGeo
        axes_dict_geo = outgeo.axes_dict

        # Add periodicities to time and angle axes
        axes_dict = output.simu.input.comp_axes(
            axes_list=["time", "angle"],
            axes_dict_in=axes_dict_geo,
            is_periodicity_a=self.is_periodicity_a,
            is_periodicity_t=self.is_periodicity_t,
            is_periodicity_rotor=self.is_periodicity_rotor,
        )

        # Check Time periodicities regarding Magnetics model input
        per_t0, is_antiper_t0 = axes_dict["time"].get_periodicity()
        is_periodicity_t0 = per_t0 > 1 or is_antiper_t0
        if not is_periodicity_t0 and self.is_periodicity_t:
            # Remove time periodicity in Magnetic model
            self.is_periodicity_t = False
            if outgeo.per_t_S != 1:
                Nt_tot = axes_dict["time"].get_length(is_oneperiod=False)
                self.get_logger().warning(
                    "In Magnetic model, Nt_tot="
                    + str(Nt_tot)
                    + " is not divisible by the machine time periodicity ("
                    + str(outgeo.per_t_S)
                    + "). Time periodicity removed"
                )

        # Check Angle periodicities regarding Magnetics model input
        per_a0, is_antiper_a0 = axes_dict["angle"].get_periodicity()
        is_periodicity_a0 = per_a0 > 1 or is_antiper_a0
        if not is_periodicity_a0 and self.is_periodicity_a:
            # Remove time periodicity in Magnetic model
            self.is_periodicity_a = False
            if outgeo.per_a != 1:
                Na_tot = axes_dict["angle"].get_length(is_oneperiod=False)
                self.get_logger().warning(
                    "In Magnetic model, Na_tot="
                    + str(Na_tot)
                    + " is not divisible by the machine angular periodicity ("
                    + str(outgeo.per_a)
                    + "). Angular periodicity removed"
                )

        # Compute slice axis
        Slice = self.Slice_enforced.get_data()

        # Add slice axis
        axes_dict["z"] = Slice

        # Add Time axis on which to calculate torque
        # Copy from standard Time axis
        Time_Tem = axes_dict["time"].copy()

        # Remove anti-periodicity if any
        if "antiperiod" in Time_Tem.symmetries:
            Time_Tem.symmetries["period"] = Time_Tem.symmetries.pop("antiperiod")

        # Store in axis dict
        axes_dict["time_Tem"] = Time_Tem

        return axes_dict

    # cf Methods.Simulation.Magnetics.comp_I_mag
    def comp_I_mag(self, output, Time):
        """Compute the currents on both stator and rotor laminations for given Magnetics time axis
        Phase currents are divided by the number of parallel circuits per pole and per phase to account
        for actual current in slot conductors

        Parameters
        ----------
        self : Magnetics
            an Magnetics object
        output: Output
            An Output object
        Time : Data
            Time vector on which to interpolate currents stored in OutElec

        Returns
        -------
        Is_val: ndarray
            Stator current matrix accounting for magnetic periodicities [qs_pera,len(time)]
        Ir_val: ndarray
            Rotor current matrix accounting for magnetic periodicities [qr_pera,len(time)]
        """

        logger = self.get_logger()

        # Extract time vector
        time = Time.get_values(is_smallestperiod=True)

        # Get laminations
        stator = output.simu.machine.stator
        rotor = output.simu.machine.rotor

        # Get stator current from electrical output
        if (
            self.is_mmfs
            and hasattr(stator, "winding")
            and stator.winding is not None
            and stator.winding.conductor is not None
        ):
            # Get Data object on magnetic Time axis
            Is = output.elec.get_Is(Time=Time)

            # Get the number of parallel circuit per phase of winding
            if hasattr(stator.winding, "Npcp") and stator.winding.Npcp is not None:
                Npcp = stator.winding.Npcp
            else:
                logger.warning("Enforcing Npcp=1 at stator side")
                Npcp = 1

            # Interpolate stator currents on input time vector
            Is_val = np.transpose(
                Is.get_along(
                    "time=axis_data",
                    "phase",
                    axis_data={"time": time},
                    is_squeeze=False,
                )[Is.symbol]
                / Npcp
            )

        else:
            Is_val = None

        # Get rotor current from electrical output
        if (
            self.is_mmfr
            and output.elec.Ir is not None
            and hasattr(rotor, "winding")
            and rotor.winding is not None
            and rotor.winding.conductor is not None
        ):
            # Get Data object
            Ir = output.elec.Ir

            # Get the number of parallel circuit per phase of winding
            if hasattr(rotor.winding, "Npcp") and rotor.winding.Npcp is not None:
                Npcp = rotor.winding.Npcp
            else:
                logger.warning("Enforcing Npcp=1 at rotor side")
                Npcp = 1

            if len(Ir.get_axes("phase")[0].symmetries) > 0 and self.is_periodicity_a:
                str_phase = "phase[oneperiod]"
            else:
                str_phase = "phase"

            # Interpolate stator currents on input time vector
            Ir_val = np.transpose(
                Ir.get_along(
                    "time=axis_data",
                    str_phase,
                    axis_data={"time": time},
                    is_squeeze=False,
                )[Ir.symbol]
                / Npcp
            )

        else:
            Ir_val = None

        return Is_val, Ir_val

    # cf Methods.Simulation.Magnetics.get_slice_model
    def get_slice_model(self):
        """Compute the slice axis required in any Magnetics module

        Parameters
        ----------
        self : SliceModel
            a SliceModel object

        Returns
        -------
        Slice: DataPattern
            Slice axis

        """

        if self.Slice_enforced is None:
            machine = self.parent.machine

            # Rotor length
            L = machine.rotor.L1

            # Check rotor skew
            rotor_skew = machine.rotor.skew
            is_rotor_skew = rotor_skew is not None

            # Enforce slice model depending on rotor skew
            slice_model = SliceModel(L=L)

            if not is_rotor_skew:
                # Single slice model
                Nslices = 2
                z_list = [-0.5 * L, 0.5 * L]
                is_step = True
                angle_rotor = np.zeros(Nslices)

            elif is_rotor_skew:
                # Slice model is given by skew slices
                if rotor_skew.type_skew == "linear" and not rotor_skew.is_step:
                    if self.Nslices_enforced is None:
                        Nslices = 5
                        self.get_logger().debug(
                            "Enforce Nslices_enforced = " + str(Nslices)
                        )
                    else:
                        Nslices = self.Nslices_enforced
                    if self.type_distribution_enforced is None:
                        type_distribution = "uniform"
                        self.get_logger().debug(
                            "Enforce type_distribution_enforced = " + type_distribution
                        )

                    else:
                        type_distribution = self.type_distribution_enforced

                    # Calculating rotor skew pattern
                    angle_skew, z_skew = rotor_skew.comp_pattern()
                    # Calculating requested slice distribution
                    slice_model.Nslices = Nslices
                    slice_model.type_distribution = type_distribution
                    z_norm = slice_model.get_distribution()
                    z_list = [z * L for z in z_norm]
                    # Interpolating rotor skew angle given new slice distribution
                    angle_rotor = np.interp(z_list, z_skew, angle_skew)

                else:
                    if self.Nslices_enforced is not None:
                        self.get_logger().info(
                            "Nslice_enforced is defined but rotor is stepped-skew, set mag.slice_model.Nslices = "
                            + str(rotor_skew.Nstep)
                        )
                    angle_rotor, z_list = rotor_skew.comp_pattern()
                    Nslices = len(z_list)
                is_step = rotor_skew.is_step

            # Store values in slice model
            slice_model.z_list = z_list
            slice_model.Nslices = Nslices
            slice_model.angle_rotor = angle_rotor
            slice_model.angle_stator = np.zeros(Nslices)
            slice_model.is_step = is_step
            slice_model.is_skew = is_rotor_skew

            self.Slice_enforced = slice_model

        return self.Slice_enforced

    # cf Methods.Simulation.Magnetics.run
    def run(self):
        """Run the Magnetics module"""
        if self.parent is None:
            raise InputError(
                "The Magnetic object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")
        self.get_logger().info("Starting Magnetic module")
        self.get_logger().debug("Using " + self.__class__.__name__ + " object")

        output = self.parent.parent

        # Get slice model and store it in output
        slice_model = self.get_slice_model()
        output.mag.Slice = slice_model

        # Compute and store time and angle axes from elec output
        # and returns additional axes in axes_dict
        axes_dict = self.comp_axes(output)

        # Get z axis
        Slice_axis = axes_dict["z"]
        unique_indices = Slice_axis.unique_indices

        # Get stator and rotor currents if requested
        if "time" in axes_dict:
            Is_val, Ir_val = self.comp_I_mag(output, Time=axes_dict["time"])
        else:
            Is_val, Ir_val = None, None

        # First iteration to check dimensions
        # Assign stator and rotor angle shifts
        self.angle_stator_shift = float(slice_model.angle_stator[unique_indices[0]])
        self.angle_rotor_shift = float(slice_model.angle_rotor[unique_indices[0]])

        # Calculate airgap flux
        Nslices = len(unique_indices)
        if Nslices > 1:
            self.get_logger().info("Solving slice 1 / " + str(Nslices))
        out_dict = self.comp_flux_airgap(
            output, axes_dict, Is_val=Is_val, Ir_val=Ir_val
        )

        is_loop = True

        if Nslices == 1:
            is_loop = False
            is_resize = True
            for key in ["B_{rad}", "B_{circ}", "B_{ax}", "Tem"]:
                if key in out_dict:
                    if len(out_dict[key].shape) == 3:
                        is_resize = False
                        break
            if is_resize:
                for key in out_dict:
                    if isinstance(out_dict[key], np.ndarray):
                        out_dict[key] = out_dict[key][..., None]
                    elif key == "Phi_wind":
                        for phi_key in out_dict[key]:
                            if len(out_dict[key][phi_key]) != 3:
                                out_dict[key][phi_key] = out_dict[key][phi_key][
                                    ..., None
                                ]
        else:
            for key in ["B_{rad}", "B_{circ}", "B_{ax}", "Tem", "Phi_wind"]:
                if key in out_dict:
                    if key == "Phi_wind":
                        # Take first value in Phi_wind dict
                        val = list(out_dict[key].values())[0]
                    else:
                        val = out_dict[key]
                    if len(val.shape) == 3:
                        if val.shape[2] > 1:
                            # Flux is already 3D -> no loop
                            is_loop = False
            if not is_loop:
                for ii in range(Nslices)[1:]:
                    self.get_logger().info(
                        "Solving slice " + str(ii + 1) + " / " + str(Nslices)
                    )

        if is_loop:
            for key in out_dict:
                if isinstance(out_dict[key], np.ndarray):
                    field = out_dict[key].copy()
                    if np.iscomplexobj(field):
                        dtype = complex
                    else:
                        dtype = float
                    out_dict[key] = np.zeros(
                        tuple([s for s in field.shape] + [Nslices]), dtype=dtype
                    )
                    out_dict[key][..., 0] = field
                elif isinstance(out_dict[key], dict):
                    for key2 in out_dict[key]:
                        if isinstance(out_dict[key][key2], np.ndarray):
                            if np.iscomplexobj(out_dict[key][key2]):
                                dtype = complex
                            else:
                                dtype = float
                            field = out_dict[key][key2].copy()
                            out_dict[key][key2] = np.zeros(
                                tuple([s for s in field.shape] + [Nslices]), dtype=dtype
                            )
                            out_dict[key][key2][..., 0] = field

            # Loop over other slices
            for ii, index in enumerate(unique_indices[1:]):
                self.get_logger().info(
                    "Solving slice " + str(ii + 2) + " / " + str(Nslices)
                )
                # Assign stator and rotor angle shifts
                self.angle_stator_shift = float(slice_model.angle_stator[index])
                self.angle_rotor_shift = float(slice_model.angle_rotor[index])

                # Calculate airgap flux
                out_dict_index = self.comp_flux_airgap(
                    output,
                    axes_dict,
                    Is_val=Is_val,
                    Ir_val=Ir_val,
                )

                # Store in out_dict matrices
                for key in out_dict_index:
                    if isinstance(out_dict_index[key], np.ndarray):
                        out_dict[key][..., ii + 1] = out_dict_index[key]
                    elif isinstance(out_dict[key], dict):
                        for key2 in out_dict[key]:
                            out_dict[key][key2][..., ii + 1] = out_dict_index[key][key2]
                    elif isinstance(out_dict[key], MeshSolution):
                        out_dict[key] = self.build_MS_sliced(
                            out_dict[key],
                            out_dict_index[key],
                            axes_dict,
                            Nslices,
                            ii + 2,
                        )
                    else:
                        # TODO store other outputs in lists
                        out_dict[key] = out_dict_index[key]

        # Store magnetic quantities contained in out_dict in OutMag, as Data object if necessary
        output.mag.store(out_dict, axes_dict)
        output.mag.comp_power()

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        is_remove_slotS=False,
        is_remove_slotR=False,
        is_remove_ventS=False,
        is_remove_ventR=False,
        is_mmfs=True,
        is_mmfr=True,
        type_BH_stator=0,
        type_BH_rotor=0,
        is_periodicity_t=False,
        is_periodicity_a=False,
        angle_stator_shift=0,
        angle_rotor_shift=0,
        logger_name="Pyleecan.Magnetics",
        Slice_enforced=None,
        Nslices_enforced=None,
        type_distribution_enforced=None,
        is_current_harm=True,
        T_mag=20,
        is_periodicity_rotor=False,
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
            if "is_remove_slotS" in list(init_dict.keys()):
                is_remove_slotS = init_dict["is_remove_slotS"]
            if "is_remove_slotR" in list(init_dict.keys()):
                is_remove_slotR = init_dict["is_remove_slotR"]
            if "is_remove_ventS" in list(init_dict.keys()):
                is_remove_ventS = init_dict["is_remove_ventS"]
            if "is_remove_ventR" in list(init_dict.keys()):
                is_remove_ventR = init_dict["is_remove_ventR"]
            if "is_mmfs" in list(init_dict.keys()):
                is_mmfs = init_dict["is_mmfs"]
            if "is_mmfr" in list(init_dict.keys()):
                is_mmfr = init_dict["is_mmfr"]
            if "type_BH_stator" in list(init_dict.keys()):
                type_BH_stator = init_dict["type_BH_stator"]
            if "type_BH_rotor" in list(init_dict.keys()):
                type_BH_rotor = init_dict["type_BH_rotor"]
            if "is_periodicity_t" in list(init_dict.keys()):
                is_periodicity_t = init_dict["is_periodicity_t"]
            if "is_periodicity_a" in list(init_dict.keys()):
                is_periodicity_a = init_dict["is_periodicity_a"]
            if "angle_stator_shift" in list(init_dict.keys()):
                angle_stator_shift = init_dict["angle_stator_shift"]
            if "angle_rotor_shift" in list(init_dict.keys()):
                angle_rotor_shift = init_dict["angle_rotor_shift"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "Slice_enforced" in list(init_dict.keys()):
                Slice_enforced = init_dict["Slice_enforced"]
            if "Nslices_enforced" in list(init_dict.keys()):
                Nslices_enforced = init_dict["Nslices_enforced"]
            if "type_distribution_enforced" in list(init_dict.keys()):
                type_distribution_enforced = init_dict["type_distribution_enforced"]
            if "is_current_harm" in list(init_dict.keys()):
                is_current_harm = init_dict["is_current_harm"]
            if "T_mag" in list(init_dict.keys()):
                T_mag = init_dict["T_mag"]
            if "is_periodicity_rotor" in list(init_dict.keys()):
                is_periodicity_rotor = init_dict["is_periodicity_rotor"]
        # Set the properties (value check and convertion are done in setter)
        self.parent = None
        self.is_remove_slotS = is_remove_slotS
        self.is_remove_slotR = is_remove_slotR
        self.is_remove_ventS = is_remove_ventS
        self.is_remove_ventR = is_remove_ventR
        self.is_mmfs = is_mmfs
        self.is_mmfr = is_mmfr
        self.type_BH_stator = type_BH_stator
        self.type_BH_rotor = type_BH_rotor
        self.is_periodicity_t = is_periodicity_t
        self.is_periodicity_a = is_periodicity_a
        self.angle_stator_shift = angle_stator_shift
        self.angle_rotor_shift = angle_rotor_shift
        self.logger_name = logger_name
        self.Slice_enforced = Slice_enforced
        self.Nslices_enforced = Nslices_enforced
        self.type_distribution_enforced = type_distribution_enforced
        self.is_current_harm = is_current_harm
        self.T_mag = T_mag
        self.is_periodicity_rotor = is_periodicity_rotor

        # The class is frozen, for now it's impossible to add new properties
        self._freeze()

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Magnetics_str = ""
        if self.parent is None:
            Magnetics_str += "parent = None " + linesep
        else:
            Magnetics_str += "parent = " + str(type(self.parent)) + " object" + linesep
        Magnetics_str += "is_remove_slotS = " + str(self.is_remove_slotS) + linesep
        Magnetics_str += "is_remove_slotR = " + str(self.is_remove_slotR) + linesep
        Magnetics_str += "is_remove_ventS = " + str(self.is_remove_ventS) + linesep
        Magnetics_str += "is_remove_ventR = " + str(self.is_remove_ventR) + linesep
        Magnetics_str += "is_mmfs = " + str(self.is_mmfs) + linesep
        Magnetics_str += "is_mmfr = " + str(self.is_mmfr) + linesep
        Magnetics_str += "type_BH_stator = " + str(self.type_BH_stator) + linesep
        Magnetics_str += "type_BH_rotor = " + str(self.type_BH_rotor) + linesep
        Magnetics_str += "is_periodicity_t = " + str(self.is_periodicity_t) + linesep
        Magnetics_str += "is_periodicity_a = " + str(self.is_periodicity_a) + linesep
        Magnetics_str += (
            "angle_stator_shift = " + str(self.angle_stator_shift) + linesep
        )
        Magnetics_str += "angle_rotor_shift = " + str(self.angle_rotor_shift) + linesep
        Magnetics_str += 'logger_name = "' + str(self.logger_name) + '"' + linesep
        if self.Slice_enforced is not None:
            tmp = (
                self.Slice_enforced.__str__()
                .replace(linesep, linesep + "\t")
                .rstrip("\t")
            )
            Magnetics_str += "Slice_enforced = " + tmp
        else:
            Magnetics_str += "Slice_enforced = None" + linesep + linesep
        Magnetics_str += "Nslices_enforced = " + str(self.Nslices_enforced) + linesep
        Magnetics_str += (
            'type_distribution_enforced = "'
            + str(self.type_distribution_enforced)
            + '"'
            + linesep
        )
        Magnetics_str += "is_current_harm = " + str(self.is_current_harm) + linesep
        Magnetics_str += "T_mag = " + str(self.T_mag) + linesep
        Magnetics_str += (
            "is_periodicity_rotor = " + str(self.is_periodicity_rotor) + linesep
        )
        return Magnetics_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False
        if other.is_remove_slotS != self.is_remove_slotS:
            return False
        if other.is_remove_slotR != self.is_remove_slotR:
            return False
        if other.is_remove_ventS != self.is_remove_ventS:
            return False
        if other.is_remove_ventR != self.is_remove_ventR:
            return False
        if other.is_mmfs != self.is_mmfs:
            return False
        if other.is_mmfr != self.is_mmfr:
            return False
        if other.type_BH_stator != self.type_BH_stator:
            return False
        if other.type_BH_rotor != self.type_BH_rotor:
            return False
        if other.is_periodicity_t != self.is_periodicity_t:
            return False
        if other.is_periodicity_a != self.is_periodicity_a:
            return False
        if other.angle_stator_shift != self.angle_stator_shift:
            return False
        if other.angle_rotor_shift != self.angle_rotor_shift:
            return False
        if other.logger_name != self.logger_name:
            return False
        if other.Slice_enforced != self.Slice_enforced:
            return False
        if other.Nslices_enforced != self.Nslices_enforced:
            return False
        if other.type_distribution_enforced != self.type_distribution_enforced:
            return False
        if other.is_current_harm != self.is_current_harm:
            return False
        if other.T_mag != self.T_mag:
            return False
        if other.is_periodicity_rotor != self.is_periodicity_rotor:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()
        if other._is_remove_slotS != self._is_remove_slotS:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_remove_slotS)
                    + ", other="
                    + str(other._is_remove_slotS)
                    + ")"
                )
                diff_list.append(name + ".is_remove_slotS" + val_str)
            else:
                diff_list.append(name + ".is_remove_slotS")
        if other._is_remove_slotR != self._is_remove_slotR:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_remove_slotR)
                    + ", other="
                    + str(other._is_remove_slotR)
                    + ")"
                )
                diff_list.append(name + ".is_remove_slotR" + val_str)
            else:
                diff_list.append(name + ".is_remove_slotR")
        if other._is_remove_ventS != self._is_remove_ventS:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_remove_ventS)
                    + ", other="
                    + str(other._is_remove_ventS)
                    + ")"
                )
                diff_list.append(name + ".is_remove_ventS" + val_str)
            else:
                diff_list.append(name + ".is_remove_ventS")
        if other._is_remove_ventR != self._is_remove_ventR:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_remove_ventR)
                    + ", other="
                    + str(other._is_remove_ventR)
                    + ")"
                )
                diff_list.append(name + ".is_remove_ventR" + val_str)
            else:
                diff_list.append(name + ".is_remove_ventR")
        if other._is_mmfs != self._is_mmfs:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_mmfs)
                    + ", other="
                    + str(other._is_mmfs)
                    + ")"
                )
                diff_list.append(name + ".is_mmfs" + val_str)
            else:
                diff_list.append(name + ".is_mmfs")
        if other._is_mmfr != self._is_mmfr:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_mmfr)
                    + ", other="
                    + str(other._is_mmfr)
                    + ")"
                )
                diff_list.append(name + ".is_mmfr" + val_str)
            else:
                diff_list.append(name + ".is_mmfr")
        if other._type_BH_stator != self._type_BH_stator:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_BH_stator)
                    + ", other="
                    + str(other._type_BH_stator)
                    + ")"
                )
                diff_list.append(name + ".type_BH_stator" + val_str)
            else:
                diff_list.append(name + ".type_BH_stator")
        if other._type_BH_rotor != self._type_BH_rotor:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_BH_rotor)
                    + ", other="
                    + str(other._type_BH_rotor)
                    + ")"
                )
                diff_list.append(name + ".type_BH_rotor" + val_str)
            else:
                diff_list.append(name + ".type_BH_rotor")
        if other._is_periodicity_t != self._is_periodicity_t:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_periodicity_t)
                    + ", other="
                    + str(other._is_periodicity_t)
                    + ")"
                )
                diff_list.append(name + ".is_periodicity_t" + val_str)
            else:
                diff_list.append(name + ".is_periodicity_t")
        if other._is_periodicity_a != self._is_periodicity_a:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_periodicity_a)
                    + ", other="
                    + str(other._is_periodicity_a)
                    + ")"
                )
                diff_list.append(name + ".is_periodicity_a" + val_str)
            else:
                diff_list.append(name + ".is_periodicity_a")
        if (
            other._angle_stator_shift is not None
            and self._angle_stator_shift is not None
            and np.isnan(other._angle_stator_shift)
            and np.isnan(self._angle_stator_shift)
        ):
            pass
        elif other._angle_stator_shift != self._angle_stator_shift:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._angle_stator_shift)
                    + ", other="
                    + str(other._angle_stator_shift)
                    + ")"
                )
                diff_list.append(name + ".angle_stator_shift" + val_str)
            else:
                diff_list.append(name + ".angle_stator_shift")
        if (
            other._angle_rotor_shift is not None
            and self._angle_rotor_shift is not None
            and np.isnan(other._angle_rotor_shift)
            and np.isnan(self._angle_rotor_shift)
        ):
            pass
        elif other._angle_rotor_shift != self._angle_rotor_shift:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._angle_rotor_shift)
                    + ", other="
                    + str(other._angle_rotor_shift)
                    + ")"
                )
                diff_list.append(name + ".angle_rotor_shift" + val_str)
            else:
                diff_list.append(name + ".angle_rotor_shift")
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
        if (other.Slice_enforced is None and self.Slice_enforced is not None) or (
            other.Slice_enforced is not None and self.Slice_enforced is None
        ):
            diff_list.append(name + ".Slice_enforced None mismatch")
        elif self.Slice_enforced is not None:
            diff_list.extend(
                self.Slice_enforced.compare(
                    other.Slice_enforced,
                    name=name + ".Slice_enforced",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._Nslices_enforced != self._Nslices_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Nslices_enforced)
                    + ", other="
                    + str(other._Nslices_enforced)
                    + ")"
                )
                diff_list.append(name + ".Nslices_enforced" + val_str)
            else:
                diff_list.append(name + ".Nslices_enforced")
        if other._type_distribution_enforced != self._type_distribution_enforced:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_distribution_enforced)
                    + ", other="
                    + str(other._type_distribution_enforced)
                    + ")"
                )
                diff_list.append(name + ".type_distribution_enforced" + val_str)
            else:
                diff_list.append(name + ".type_distribution_enforced")
        if other._is_current_harm != self._is_current_harm:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_current_harm)
                    + ", other="
                    + str(other._is_current_harm)
                    + ")"
                )
                diff_list.append(name + ".is_current_harm" + val_str)
            else:
                diff_list.append(name + ".is_current_harm")
        if (
            other._T_mag is not None
            and self._T_mag is not None
            and np.isnan(other._T_mag)
            and np.isnan(self._T_mag)
        ):
            pass
        elif other._T_mag != self._T_mag:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._T_mag) + ", other=" + str(other._T_mag) + ")"
                )
                diff_list.append(name + ".T_mag" + val_str)
            else:
                diff_list.append(name + ".T_mag")
        if other._is_periodicity_rotor != self._is_periodicity_rotor:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_periodicity_rotor)
                    + ", other="
                    + str(other._is_periodicity_rotor)
                    + ")"
                )
                diff_list.append(name + ".is_periodicity_rotor" + val_str)
            else:
                diff_list.append(name + ".is_periodicity_rotor")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object
        S += getsizeof(self.is_remove_slotS)
        S += getsizeof(self.is_remove_slotR)
        S += getsizeof(self.is_remove_ventS)
        S += getsizeof(self.is_remove_ventR)
        S += getsizeof(self.is_mmfs)
        S += getsizeof(self.is_mmfr)
        S += getsizeof(self.type_BH_stator)
        S += getsizeof(self.type_BH_rotor)
        S += getsizeof(self.is_periodicity_t)
        S += getsizeof(self.is_periodicity_a)
        S += getsizeof(self.angle_stator_shift)
        S += getsizeof(self.angle_rotor_shift)
        S += getsizeof(self.logger_name)
        S += getsizeof(self.Slice_enforced)
        S += getsizeof(self.Nslices_enforced)
        S += getsizeof(self.type_distribution_enforced)
        S += getsizeof(self.is_current_harm)
        S += getsizeof(self.T_mag)
        S += getsizeof(self.is_periodicity_rotor)
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

        Magnetics_dict = dict()
        Magnetics_dict["is_remove_slotS"] = self.is_remove_slotS
        Magnetics_dict["is_remove_slotR"] = self.is_remove_slotR
        Magnetics_dict["is_remove_ventS"] = self.is_remove_ventS
        Magnetics_dict["is_remove_ventR"] = self.is_remove_ventR
        Magnetics_dict["is_mmfs"] = self.is_mmfs
        Magnetics_dict["is_mmfr"] = self.is_mmfr
        Magnetics_dict["type_BH_stator"] = self.type_BH_stator
        Magnetics_dict["type_BH_rotor"] = self.type_BH_rotor
        Magnetics_dict["is_periodicity_t"] = self.is_periodicity_t
        Magnetics_dict["is_periodicity_a"] = self.is_periodicity_a
        Magnetics_dict["angle_stator_shift"] = self.angle_stator_shift
        Magnetics_dict["angle_rotor_shift"] = self.angle_rotor_shift
        Magnetics_dict["logger_name"] = self.logger_name
        if self.Slice_enforced is None:
            Magnetics_dict["Slice_enforced"] = None
        else:
            Magnetics_dict["Slice_enforced"] = self.Slice_enforced.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        Magnetics_dict["Nslices_enforced"] = self.Nslices_enforced
        Magnetics_dict["type_distribution_enforced"] = self.type_distribution_enforced
        Magnetics_dict["is_current_harm"] = self.is_current_harm
        Magnetics_dict["T_mag"] = self.T_mag
        Magnetics_dict["is_periodicity_rotor"] = self.is_periodicity_rotor
        # The class name is added to the dict for deserialisation purpose
        Magnetics_dict["__class__"] = "Magnetics"
        return Magnetics_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        is_remove_slotS_val = self.is_remove_slotS
        is_remove_slotR_val = self.is_remove_slotR
        is_remove_ventS_val = self.is_remove_ventS
        is_remove_ventR_val = self.is_remove_ventR
        is_mmfs_val = self.is_mmfs
        is_mmfr_val = self.is_mmfr
        type_BH_stator_val = self.type_BH_stator
        type_BH_rotor_val = self.type_BH_rotor
        is_periodicity_t_val = self.is_periodicity_t
        is_periodicity_a_val = self.is_periodicity_a
        angle_stator_shift_val = self.angle_stator_shift
        angle_rotor_shift_val = self.angle_rotor_shift
        logger_name_val = self.logger_name
        if self.Slice_enforced is None:
            Slice_enforced_val = None
        else:
            Slice_enforced_val = self.Slice_enforced.copy()
        Nslices_enforced_val = self.Nslices_enforced
        type_distribution_enforced_val = self.type_distribution_enforced
        is_current_harm_val = self.is_current_harm
        T_mag_val = self.T_mag
        is_periodicity_rotor_val = self.is_periodicity_rotor
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            is_remove_slotS=is_remove_slotS_val,
            is_remove_slotR=is_remove_slotR_val,
            is_remove_ventS=is_remove_ventS_val,
            is_remove_ventR=is_remove_ventR_val,
            is_mmfs=is_mmfs_val,
            is_mmfr=is_mmfr_val,
            type_BH_stator=type_BH_stator_val,
            type_BH_rotor=type_BH_rotor_val,
            is_periodicity_t=is_periodicity_t_val,
            is_periodicity_a=is_periodicity_a_val,
            angle_stator_shift=angle_stator_shift_val,
            angle_rotor_shift=angle_rotor_shift_val,
            logger_name=logger_name_val,
            Slice_enforced=Slice_enforced_val,
            Nslices_enforced=Nslices_enforced_val,
            type_distribution_enforced=type_distribution_enforced_val,
            is_current_harm=is_current_harm_val,
            T_mag=T_mag_val,
            is_periodicity_rotor=is_periodicity_rotor_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.is_remove_slotS = None
        self.is_remove_slotR = None
        self.is_remove_ventS = None
        self.is_remove_ventR = None
        self.is_mmfs = None
        self.is_mmfr = None
        self.type_BH_stator = None
        self.type_BH_rotor = None
        self.is_periodicity_t = None
        self.is_periodicity_a = None
        self.angle_stator_shift = None
        self.angle_rotor_shift = None
        self.logger_name = None
        if self.Slice_enforced is not None:
            self.Slice_enforced._set_None()
        self.Nslices_enforced = None
        self.type_distribution_enforced = None
        self.is_current_harm = None
        self.T_mag = None
        self.is_periodicity_rotor = None

    def _get_is_remove_slotS(self):
        """getter of is_remove_slotS"""
        return self._is_remove_slotS

    def _set_is_remove_slotS(self, value):
        """setter of is_remove_slotS"""
        check_var("is_remove_slotS", value, "bool")
        self._is_remove_slotS = value

    is_remove_slotS = property(
        fget=_get_is_remove_slotS,
        fset=_set_is_remove_slotS,
        doc="""1 to artificially remove stator slotting effects in permeance mmf calculations

        :Type: bool
        """,
    )

    def _get_is_remove_slotR(self):
        """getter of is_remove_slotR"""
        return self._is_remove_slotR

    def _set_is_remove_slotR(self, value):
        """setter of is_remove_slotR"""
        check_var("is_remove_slotR", value, "bool")
        self._is_remove_slotR = value

    is_remove_slotR = property(
        fget=_get_is_remove_slotR,
        fset=_set_is_remove_slotR,
        doc="""1 to artificially remove rotor slotting effects in permeance mmf calculations

        :Type: bool
        """,
    )

    def _get_is_remove_ventS(self):
        """getter of is_remove_ventS"""
        return self._is_remove_ventS

    def _set_is_remove_ventS(self, value):
        """setter of is_remove_ventS"""
        check_var("is_remove_ventS", value, "bool")
        self._is_remove_ventS = value

    is_remove_ventS = property(
        fget=_get_is_remove_ventS,
        fset=_set_is_remove_ventS,
        doc="""1 to artificially remove the ventilations duct of the stator

        :Type: bool
        """,
    )

    def _get_is_remove_ventR(self):
        """getter of is_remove_ventR"""
        return self._is_remove_ventR

    def _set_is_remove_ventR(self, value):
        """setter of is_remove_ventR"""
        check_var("is_remove_ventR", value, "bool")
        self._is_remove_ventR = value

    is_remove_ventR = property(
        fget=_get_is_remove_ventR,
        fset=_set_is_remove_ventR,
        doc="""1 to artificially remove the ventilations duct of the rotor

        :Type: bool
        """,
    )

    def _get_is_mmfs(self):
        """getter of is_mmfs"""
        return self._is_mmfs

    def _set_is_mmfs(self, value):
        """setter of is_mmfs"""
        check_var("is_mmfs", value, "bool")
        self._is_mmfs = value

    is_mmfs = property(
        fget=_get_is_mmfs,
        fset=_set_is_mmfs,
        doc="""1 to compute the stator magnetomotive force / stator armature magnetic field

        :Type: bool
        """,
    )

    def _get_is_mmfr(self):
        """getter of is_mmfr"""
        return self._is_mmfr

    def _set_is_mmfr(self, value):
        """setter of is_mmfr"""
        check_var("is_mmfr", value, "bool")
        self._is_mmfr = value

    is_mmfr = property(
        fget=_get_is_mmfr,
        fset=_set_is_mmfr,
        doc="""1 to compute the rotor magnetomotive force / rotor magnetic field

        :Type: bool
        """,
    )

    def _get_type_BH_stator(self):
        """getter of type_BH_stator"""
        return self._type_BH_stator

    def _set_type_BH_stator(self, value):
        """setter of type_BH_stator"""
        check_var("type_BH_stator", value, "int", Vmin=0, Vmax=2)
        self._type_BH_stator = value

    type_BH_stator = property(
        fget=_get_type_BH_stator,
        fset=_set_type_BH_stator,
        doc="""0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)

        :Type: int
        :min: 0
        :max: 2
        """,
    )

    def _get_type_BH_rotor(self):
        """getter of type_BH_rotor"""
        return self._type_BH_rotor

    def _set_type_BH_rotor(self, value):
        """setter of type_BH_rotor"""
        check_var("type_BH_rotor", value, "int", Vmin=0, Vmax=2)
        self._type_BH_rotor = value

    type_BH_rotor = property(
        fget=_get_type_BH_rotor,
        fset=_set_type_BH_rotor,
        doc="""0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)

        :Type: int
        :min: 0
        :max: 2
        """,
    )

    def _get_is_periodicity_t(self):
        """getter of is_periodicity_t"""
        return self._is_periodicity_t

    def _set_is_periodicity_t(self, value):
        """setter of is_periodicity_t"""
        check_var("is_periodicity_t", value, "bool")
        self._is_periodicity_t = value

    is_periodicity_t = property(
        fget=_get_is_periodicity_t,
        fset=_set_is_periodicity_t,
        doc="""True to compute only on one time periodicity (use periodicities defined in axes_dict[time])

        :Type: bool
        """,
    )

    def _get_is_periodicity_a(self):
        """getter of is_periodicity_a"""
        return self._is_periodicity_a

    def _set_is_periodicity_a(self, value):
        """setter of is_periodicity_a"""
        check_var("is_periodicity_a", value, "bool")
        self._is_periodicity_a = value

    is_periodicity_a = property(
        fget=_get_is_periodicity_a,
        fset=_set_is_periodicity_a,
        doc="""True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle])

        :Type: bool
        """,
    )

    def _get_angle_stator_shift(self):
        """getter of angle_stator_shift"""
        return self._angle_stator_shift

    def _set_angle_stator_shift(self, value):
        """setter of angle_stator_shift"""
        check_var("angle_stator_shift", value, "float")
        self._angle_stator_shift = value

    angle_stator_shift = property(
        fget=_get_angle_stator_shift,
        fset=_set_angle_stator_shift,
        doc="""Shift angle to appy to the stator in magnetic model

        :Type: float
        """,
    )

    def _get_angle_rotor_shift(self):
        """getter of angle_rotor_shift"""
        return self._angle_rotor_shift

    def _set_angle_rotor_shift(self, value):
        """setter of angle_rotor_shift"""
        check_var("angle_rotor_shift", value, "float")
        self._angle_rotor_shift = value

    angle_rotor_shift = property(
        fget=_get_angle_rotor_shift,
        fset=_set_angle_rotor_shift,
        doc="""Shift angle to appy to the rotor in magnetic model

        :Type: float
        """,
    )

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

    def _get_Slice_enforced(self):
        """getter of Slice_enforced"""
        return self._Slice_enforced

    def _set_Slice_enforced(self, value):
        """setter of Slice_enforced"""
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
                "pyleecan.Classes", value.get("__class__"), "Slice_enforced"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            SliceModel = import_class(
                "pyleecan.Classes", "SliceModel", "Slice_enforced"
            )
            value = SliceModel()
        check_var("Slice_enforced", value, "SliceModel")
        self._Slice_enforced = value

        if self._Slice_enforced is not None:
            self._Slice_enforced.parent = self

    Slice_enforced = property(
        fget=_get_Slice_enforced,
        fset=_set_Slice_enforced,
        doc="""Enforce slice model to account for skew

        :Type: SliceModel
        """,
    )

    def _get_Nslices_enforced(self):
        """getter of Nslices_enforced"""
        return self._Nslices_enforced

    def _set_Nslices_enforced(self, value):
        """setter of Nslices_enforced"""
        check_var("Nslices_enforced", value, "int")
        self._Nslices_enforced = value

    Nslices_enforced = property(
        fget=_get_Nslices_enforced,
        fset=_set_Nslices_enforced,
        doc="""To enforce number of slices in slice model

        :Type: int
        """,
    )

    def _get_type_distribution_enforced(self):
        """getter of type_distribution_enforced"""
        return self._type_distribution_enforced

    def _set_type_distribution_enforced(self, value):
        """setter of type_distribution_enforced"""
        check_var("type_distribution_enforced", value, "str")
        self._type_distribution_enforced = value

    type_distribution_enforced = property(
        fget=_get_type_distribution_enforced,
        fset=_set_type_distribution_enforced,
        doc="""To enforce type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")

        :Type: str
        """,
    )

    def _get_is_current_harm(self):
        """getter of is_current_harm"""
        return self._is_current_harm

    def _set_is_current_harm(self, value):
        """setter of is_current_harm"""
        check_var("is_current_harm", value, "bool")
        self._is_current_harm = value

    is_current_harm = property(
        fget=_get_is_current_harm,
        fset=_set_is_current_harm,
        doc="""0 To compute only the airgap flux from fundamental current harmonics

        :Type: bool
        """,
    )

    def _get_T_mag(self):
        """getter of T_mag"""
        return self._T_mag

    def _set_T_mag(self, value):
        """setter of T_mag"""
        check_var("T_mag", value, "float")
        self._T_mag = value

    T_mag = property(
        fget=_get_T_mag,
        fset=_set_T_mag,
        doc="""Permanent magnet temperature to adapt magnet remanent flux density

        :Type: float
        """,
    )

    def _get_is_periodicity_rotor(self):
        """getter of is_periodicity_rotor"""
        return self._is_periodicity_rotor

    def _set_is_periodicity_rotor(self, value):
        """setter of is_periodicity_rotor"""
        check_var("is_periodicity_rotor", value, "bool")
        self._is_periodicity_rotor = value

    is_periodicity_rotor = property(
        fget=_get_is_periodicity_rotor,
        fset=_set_is_periodicity_rotor,
        doc="""True to consider rotor periodicity over time instead of stator

        :Type: bool
        """,
    )

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""

        pass


InputError = Magnetics.InputError
