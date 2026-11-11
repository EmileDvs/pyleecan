# Experimental dataclass generated from Generator/ClassesRef/Simulation/InputCurrent.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np

from ..Functions_new.Electrical.dqh_transformation import get_phase_dir, n2dqh_DataTime
from ._error import InputError
from .data_1d import Data1D
from .data_freq import DataFreq
from .data_time import DataTime
from .elec_lut_dq import ElecLUTdq
from .import_data import ImportData
from .import_matrix import ImportMatrix
from .input_voltage import InputVoltage


@dataclass(eq=False)
class InputCurrent(InputVoltage):
    """Input to skip the electrical module and start with the magnetic one

    Attributes
    ----------
    Is : ImportMatrix or None
        Stator currents as a function of time (each column correspond to one phase) to import
        Unit: A; Default: None
    Ir : ImportMatrix or None
        Rotor currents as a function of time (each column correspond to one phase) to import
        Unit: A; Default: None
    Is_harm : ImportData or None
        Stator harmonic currents
        Unit: A; Default: None
    """

    Is: ImportMatrix | None = field(
        default=None, metadata={"default_class": "ImportMatrix"}
    )
    """Stator currents as a function of time (each column correspond to one phase) to import"""
    Ir: ImportMatrix | None = field(
        default=None, metadata={"default_class": "ImportMatrix"}
    )
    """Rotor currents as a function of time (each column correspond to one phase) to import"""
    Is_harm: ImportData | None = field(
        default=None, metadata={"default_class": "ImportData"}
    )
    """Stator harmonic currents"""

    # Inlined from Methods.Simulation.InputCurrent.gen_input
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

    # Inlined from Methods.Simulation.InputCurrent.set_Id_Iq
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
