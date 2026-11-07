# Experimental dataclass generated from Generator/ClassesRef/Simulation/Magnetics.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._pyleecan_class import PyleecanClass
from .eec import EEC
from .mesh_solution import MeshSolution
from .simulation import Simulation
from .slice_model import SliceModel


@dataclass(eq=False)
class Magnetics(PyleecanClass):
    """Magnetic module abstract object

    Attributes
    ----------
    is_remove_slotS : bool
        True to artificially remove stator slotting effects in permeance mmf calculations
        Default: False
    is_remove_slotR : bool
        True to artificially remove rotor slotting effects in permeance mmf calculations
        Default: False
    is_remove_ventS : bool
        True to artificially remove the ventilations duct of the stator
        Default: False
    is_remove_ventR : bool
        True to artificially remove the ventilations duct of the rotor
        Default: False
    is_mmfs : bool
        True to compute the stator magnetomotive force / stator armature magnetic field
        Default: True
    is_mmfr : bool
        True to compute the rotor magnetomotive force / rotor magnetic field
        Default: True
    type_BH_stator : int
        0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)
        Default: 0; Minimum: 0; Maximum: 2
    type_BH_rotor : int
        0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)
        Default: 0; Minimum: 0; Maximum: 2
    is_periodicity_t : bool
        True to compute only on one time periodicity (use periodicities defined in axes_dict[time])
        Default: False
    is_periodicity_a : bool
        True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle])
        Default: False
    angle_stator_shift : float
        Shift angle to appy to the stator in magnetic model
        Unit: rad; Default: 0
    angle_rotor_shift : float
        Shift angle to appy to the rotor in magnetic model
        Unit: rad; Default: 0
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Magnetics"
    Slice_enforced : SliceModel or None
        Enforce slice model to account for skew
        Default: None
    Nslices_enforced : int or None
        To enforce number of slices in slice model
        Default: None
    type_distribution_enforced : str or None
        To enforce type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")
        Default: None
    is_current_harm : bool
        False To compute only the airgap flux from fundamental current harmonics
        Default: True
    T_mag : float
        Permanent magnet temperature to adapt magnet remanent flux density
        Unit: deg Celsius; Default: 20
    is_periodicity_rotor : bool
        True to consider rotor periodicity over time instead of stator
        Default: False
    """

    is_remove_slotS: bool = False
    """True to artificially remove stator slotting effects in permeance mmf calculations"""
    is_remove_slotR: bool = False
    """True to artificially remove rotor slotting effects in permeance mmf calculations"""
    is_remove_ventS: bool = False
    """True to artificially remove the ventilations duct of the stator"""
    is_remove_ventR: bool = False
    """True to artificially remove the ventilations duct of the rotor"""
    is_mmfs: bool = True
    """True to compute the stator magnetomotive force / stator armature magnetic field"""
    is_mmfr: bool = True
    """True to compute the rotor magnetomotive force / rotor magnetic field"""
    type_BH_stator: int = 0
    """0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)"""
    type_BH_rotor: int = 0
    """0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)"""
    is_periodicity_t: bool = False
    """True to compute only on one time periodicity (use periodicities defined in axes_dict[time])"""
    is_periodicity_a: bool = False
    """True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle])"""
    angle_stator_shift: float = 0
    """Shift angle to appy to the stator in magnetic model"""
    angle_rotor_shift: float = 0
    """Shift angle to appy to the rotor in magnetic model"""
    logger_name: str = "Pyleecan.Magnetics"
    """Name of the logger to use"""
    Slice_enforced: SliceModel | None = None
    """Enforce slice model to account for skew"""
    Nslices_enforced: int | None = None
    """To enforce number of slices in slice model"""
    type_distribution_enforced: str | None = None
    """To enforce type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")"""
    is_current_harm: bool = True
    """False To compute only the airgap flux from fundamental current harmonics"""
    T_mag: float = 20
    """Permanent magnet temperature to adapt magnet remanent flux density"""
    is_periodicity_rotor: bool = False
    """True to consider rotor periodicity over time instead of stator"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                EEC,
                Simulation,
            ),
        ):
            raise TypeError(
                "Magnetics parent must be an instance of EEC or Simulation, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Simulation.Magnetics.comp_axes
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

    # Inlined from Methods.Simulation.Magnetics.comp_I_mag
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

    # Inlined from Methods.Simulation.Magnetics.get_slice_model
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

    # Inlined from Methods.Simulation.Magnetics.run
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

    class InputError(Exception):
        """Raised when the input data are incomplete or incorrect"""


InputError = Magnetics.InputError
