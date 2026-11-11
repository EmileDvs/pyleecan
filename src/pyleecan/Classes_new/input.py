# Experimental dataclass generated from Generator/ClassesRef/Simulation/Input.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ._pyleecan_class import PyleecanClass
from .data_1d import Data1D
from .data_linspace import DataLinspace
from .import_matrix import ImportMatrix
from .norm_affine import NormAffine
from .norm_indices import NormIndices
from .norm_ref import NormRef
from .op import OP

ROT_DIR_REF = -1
CURRENT_DIR_REF = -1
PHASE_DIR_REF = -1


@dataclass(eq=False)
class Input(PyleecanClass):
    """Starting data of the simulation

    Attributes
    ----------
    time : ImportMatrix or None
        Electrical time vector (no symmetry) to import
        Unit: s; Default: None
    angle : ImportMatrix or None
        Electrical position vector (no symmetry) to import
        Unit: rad; Default: None
    Nt_tot : int
        Time discretization
        Default: 2048; Minimum: 1
    Nrev : float or None
        Number of rotor revolution (to compute the final time)
        Default: None; Minimum: 0
    Na_tot : int
        Angular discretization
        Default: 2048; Minimum: 1
    OP : OP or None
        Operating Point
        Default: None
    t_final : float or None
        To enforce final time
        Default: None
    """

    time: ImportMatrix | None = field(
        default=None, metadata={"default_class": "ImportMatrix"}
    )
    """Electrical time vector (no symmetry) to import"""
    angle: ImportMatrix | None = field(
        default=None, metadata={"default_class": "ImportMatrix"}
    )
    """Electrical position vector (no symmetry) to import"""
    Nt_tot: int = 2048
    """Time discretization"""
    Nrev: float | None = None
    """Number of rotor revolution (to compute the final time)"""
    Na_tot: int = 2048
    """Angular discretization"""
    OP: OP | None = field(default=None, metadata={"default_class": "OP"})
    """Operating Point"""
    t_final: float | None = None
    """To enforce final time"""

    # Inlined from Methods.Simulation.Input.comp_axes
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
        axes_dict = {}

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
            except Exception:  # Case where rotor is not defined yet (Rag is only used for angle axis normalization)
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

    # Inlined from Methods.Simulation.Input.comp_axis_angle
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

        norm_angle = {"space_order": NormRef(ref=p), "distance": NormRef(ref=1 / Rag)}

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
                final=2 * np.pi,
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
            sym_a = {}
            if is_antiper_a:
                sym_a["antiperiod"] = per_a
            elif per_a > 1:
                sym_a["period"] = per_a
            Angle.symmetries = sym_a
            Angle = Angle.to_linspace()

        return Angle

    # Inlined from Methods.Simulation.Input.comp_axis_phase
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
                    sym_dict = {}
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
                        final=2 * np.pi / per_a,
                        number=int(len(name_phase) / per_a),
                        include_endpoint=False,
                        symmetries=sym_dict,
                        normalizations={"bar_id": NormIndices()},
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
                    final=2 * np.pi,
                    number=1,
                    include_endpoint=False,
                    normalizations={"bar_id": NormIndices()},
                    is_overlay=True,
                    # filter={"Phase": []},
                )

        return Phase

    # Inlined from Methods.Simulation.Input.comp_axis_time
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
            "elec_order": NormRef(ref=f_elec),
            "mech_order": NormRef(ref=N0 / 60),
            "angle_elec": NormRef(ref=self.current_dir / (2 * np.pi * f_elec)),
            "angle_rotor": NormAffine(
                slope=self.rot_dir * N0 * 360 / 60, offset=A0 * 180 / np.pi
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
            sym_t = {}
            if is_antiper_t:
                sym_t["antiperiod"] = per_t
            elif per_t > 1:
                sym_t["period"] = per_t
            Time.symmetries = sym_t
            Time = Time.to_linspace()

        return Time
