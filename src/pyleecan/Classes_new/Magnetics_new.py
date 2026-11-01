# Experimental dataclass generated from Generator/ClassesRef/Simulation/Magnetics.csv
"""Generated experimental dataclass; do not edit by hand."""

from copy import deepcopy
from dataclasses import dataclass, field, fields
from sys import getsizeof
from typing import Any, ClassVar, get_args, get_type_hints

import numpy as np
from dacite import Config, from_dict

from pyleecan.Classes.MeshSolution import MeshSolution
from pyleecan.Classes.SliceModel import SliceModel
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save


def _walk_types(type_hint):
    yield type_hint
    for argument in get_args(type_hint):
        yield from _walk_types(argument)


def _set_parent_links(value, parent):
    if isinstance(value, (list, tuple)):
        for item in value:
            _set_parent_links(item, parent)
    elif isinstance(value, dict):
        for item in value.values():
            _set_parent_links(item, parent)
    elif hasattr(value, "parent"):
        value.parent = parent


def _serialize_value(value, type_handle_ndarray, keep_function, kwargs):
    if value is None:
        return None
    if isinstance(value, np.ndarray):
        if type_handle_ndarray == 0:
            return value.tolist()
        if type_handle_ndarray == 1:
            return value.copy()
        if type_handle_ndarray == 2:
            return value
        raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
    if hasattr(value, "as_dict"):
        return value.as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
    if isinstance(value, dict):
        return {
            key: _serialize_value(item, type_handle_ndarray, keep_function, kwargs)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [
            _serialize_value(item, type_handle_ndarray, keep_function, kwargs)
            for item in value
        ]
    if type(value) is complex:
        return str(value)
    if callable(value) and not keep_function:
        return None
    return value


def _copy_value(value):
    if value is None:
        return None
    if isinstance(value, list):
        return [_copy_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _copy_value(item) for key, item in value.items()}
    if hasattr(value, "copy"):
        return value.copy()
    return deepcopy(value)


@dataclass(eq=False)
class Magnetics_new:
    """Magnetic module abstract object

    Attributes
    ----------
    is_remove_slotS : bool
        1 to artificially remove stator slotting effects in permeance mmf calculations
        Unit: -
        Default: False
    is_remove_slotR : bool
        1 to artificially remove rotor slotting effects in permeance mmf calculations
        Unit: -
        Default: False
    is_remove_ventS : bool
        1 to artificially remove the ventilations duct of the stator
        Unit: -
        Default: False
    is_remove_ventR : bool
        1 to artificially remove the ventilations duct of the rotor
        Unit: -
        Default: False
    is_mmfs : bool
        1 to compute the stator magnetomotive force / stator armature magnetic field
        Unit: -
        Default: True
    is_mmfr : bool
        1 to compute the rotor magnetomotive force / rotor magnetic field
        Unit: -
        Default: True
    type_BH_stator : int
        0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)
        Unit: -
        Default: 0
        Minimum: 0
        Maximum: 2
    type_BH_rotor : int
        0 to use the B(H) curve, 1 to use linear B(H) curve according to mur_lin, 2 to enforce infinite permeability (mur_lin =100000)
        Unit: -
        Default: 0
        Minimum: 0
        Maximum: 2
    is_periodicity_t : bool
        True to compute only on one time periodicity (use periodicities defined in axes_dict[time])
        Unit: -
        Default: False
    is_periodicity_a : bool
        True to compute only on one angle periodicity (use periodicities defined in axes_dict[angle])
        Unit: -
        Default: False
    angle_stator_shift : float
        Shift angle to appy to the stator in magnetic model
        Unit: rad
        Default: 0
    angle_rotor_shift : float
        Shift angle to appy to the rotor in magnetic model
        Unit: rad
        Default: 0
    logger_name : str
        Name of the logger to use
        Unit: -
        Default: "Pyleecan.Magnetics"
    Slice_enforced : SliceModel or None
        Enforce slice model to account for skew
        Unit: -
        Default: None
    Nslices_enforced : int or None
        To enforce number of slices in slice model
        Default: None
    type_distribution_enforced : str or None
        To enforce type of slice distribution to use for rotor skew if linear and continuous ("uniform", "gauss", "user-defined")
        Unit: -
        Default: None
    is_current_harm : bool
        0 To compute only the airgap flux from fundamental current harmonics
        Default: True
    T_mag : float
        Permanent magnet temperature to adapt magnet remanent flux density
        Unit: deg Celsius
        Default: 20
    is_periodicity_rotor : bool
        True to consider rotor periodicity over time instead of stator
        Default: False
    """

    VERSION: ClassVar = 1
    parent: Any = field(
        default=None,
        init=False,
        repr=False,
        compare=False,
        metadata={"serialize": False, "compare": False},
    )
    is_remove_slotS: bool = False
    """1 to artificially remove stator slotting effects in permeance mmf calculations"""
    is_remove_slotR: bool = False
    """1 to artificially remove rotor slotting effects in permeance mmf calculations"""
    is_remove_ventS: bool = False
    """1 to artificially remove the ventilations duct of the stator"""
    is_remove_ventR: bool = False
    """1 to artificially remove the ventilations duct of the rotor"""
    is_mmfs: bool = True
    """1 to compute the stator magnetomotive force / stator armature magnetic field"""
    is_mmfr: bool = True
    """1 to compute the rotor magnetomotive force / rotor magnetic field"""
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
    """0 To compute only the airgap flux from fundamental current harmonics"""
    T_mag: float = 20
    """Permanent magnet temperature to adapt magnet remanent flux density"""
    is_periodicity_rotor: bool = False
    """True to consider rotor periodicity over time instead of stator"""

    def __post_init__(self):
        self._set_child_parents()

    @classmethod
    def from_dict(cls, data):
        """Create this dataclass from a Pyleecan-style dictionary."""
        values = {key: value for key, value in data.items() if key != "__class__"}
        hints = get_type_hints(cls)
        hooks = {}
        for field_info in fields(cls):
            field_type = hints.get(field_info.name)
            for candidate in _walk_types(field_type):
                if isinstance(candidate, type) and hasattr(candidate, "as_dict"):
                    hooks[candidate] = lambda value, target=candidate: (
                        value if isinstance(value, target) else target(init_dict=value)
                    )
        instance = from_dict(cls, values, config=Config(type_hooks=hooks))
        instance._set_child_parents()
        return instance

    def _set_child_parents(self):
        """Set parent links on nested Pyleecan objects."""
        for field_info in fields(self):
            if field_info.name == "parent":
                continue
            _set_parent_links(getattr(self, field_info.name), self)

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """Serialize dataclass fields using Pyleecan's object dictionary format."""
        if type_handle_ndarray not in (0, 1, 2):
            raise ValueError(f"Unknown type_handle_ndarray: {type_handle_ndarray}")
        values = {}
        for field_info in fields(self):
            if field_info.metadata.get("serialize", True):
                if field_info.metadata.get("as_dict") in ("1", "2"):
                    values[field_info.name] = None
                else:
                    values[field_info.name] = _serialize_value(
                        getattr(self, field_info.name),
                        type_handle_ndarray,
                        keep_function,
                        kwargs,
                    )
        values["__class__"] = type(self).__name__
        return values

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare dataclass fields and return paths to differing values."""
        if type(other) is not type(self):
            return [f"type({name})"]
        ignored = set(ignore_list or ())
        differences = []
        for field_info in fields(self):
            if not field_info.metadata.get("compare", True):
                continue
            left = getattr(self, field_info.name)
            right = getattr(other, field_info.name)
            field_name = f"{name}.{field_info.name}"
            if left is None or right is None:
                if left is not right:
                    differences.append(field_name + " None mismatch")
                continue
            if hasattr(left, "compare"):
                differences.extend(
                    left.compare(
                        right,
                        name=field_name,
                        ignore_list=ignore_list,
                        is_add_value=is_add_value,
                    )
                )
                continue
            if isinstance(left, np.ndarray) or isinstance(right, np.ndarray):
                equal = np.array_equal(left, right, equal_nan=True)
            else:
                try:
                    equal = bool(left == right)
                except TypeError, ValueError:
                    equal = False
            if not equal:
                suffix = f" (self={left}, other={right})" if is_add_value else ""
                differences.append(field_name + suffix)
        return [item for item in differences if item not in ignored]

    def __eq__(self, other):
        return isinstance(other, type(self)) and not self.compare(other)

    def copy(self):
        """Copy dataclass values and their nested Pyleecan objects."""
        values = {}
        for field_info in fields(self):
            if not field_info.init:
                continue
            mode = field_info.metadata.get("as_dict")
            value = getattr(self, field_info.name)
            if mode == "1":
                values[field_info.name] = None
            elif mode == "2":
                values[field_info.name] = value
            else:
                values[field_info.name] = _copy_value(value)
        return type(self)(**values)

    def _set_None(self):
        """Set fields to None, recursively clearing nested objects."""
        for field_info in fields(self):
            if field_info.name == "parent":
                continue
            value = getattr(self, field_info.name)
            if value is not None and hasattr(value, "_set_None"):
                value._set_None()
            else:
                setattr(self, field_info.name, None)

    def __sizeof__(self):
        return object.__sizeof__(self) + sum(
            getsizeof(getattr(self, field_info.name))
            for field_info in fields(self)
            if field_info.name != "parent"
        )

    def __str__(self):
        return self.__repr__()

    def get_logger(self):
        return get_logger(self)

    def save(self, *args, **kwargs):
        return save(self, *args, **kwargs)

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

        pass


InputError = Magnetics_new.InputError
