# Experimental dataclass generated from Generator/ClassesRef/Simulation/Electrical.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._error import InputError
from ._pyleecan_class import PyleecanClass
from .data_1d import Data1D
from .data_time import DataTime
from .eec import EEC
from .eec_pmsm import EEC_PMSM
from .eec_scim import EEC_SCIM
from .lut import LUT
from .machine_ipmsm import MachineIPMSM
from .machine_scim import MachineSCIM
from .machine_sipmsm import MachineSIPMSM


@dataclass(eq=False)
class Electrical(PyleecanClass):
    """Electric module object for electrical equivalent circuit simulation

    Attributes
    ----------
    eec : EEC or None
        Electrical Equivalent Circuit
        Default: None
    logger_name : str
        Name of the logger to use
        Default: "Pyleecan.Electrical"
    freq_max : float
        Maximum frequency to calculate voltage and current harmonics
        Unit: Hz; Default: 40000
    LUT_enforced : LUT or None
        Look-Up Tables to update equivalent circuit parameters
        Default: None
    Tsta : float
        Average stator temperature for Electrical calculation
        Unit: deg Celsius; Default: 20
    Trot : float
        Average rotor temperature for Electrical calculation
        Unit: deg Celsius; Default: 20
    type_skin_effect : int
        Skin effect for resistance and inductance
        Default: 1
    is_skin_effect_inductance : bool
        True to include skin effect on inductance if type_skin_effect != False
        Default: True
    """

    eec: EEC | None = None
    """Electrical Equivalent Circuit"""
    logger_name: str = "Pyleecan.Electrical"
    """Name of the logger to use"""
    freq_max: float = 40000
    """Maximum frequency to calculate voltage and current harmonics"""
    LUT_enforced: LUT | None = None
    """Look-Up Tables to update equivalent circuit parameters"""
    Tsta: float = 20
    """Average stator temperature for Electrical calculation"""
    Trot: float = 20
    """Average rotor temperature for Electrical calculation"""
    type_skin_effect: int = 1
    """Skin effect for resistance and inductance"""
    is_skin_effect_inductance: bool = True
    """True to include skin effect on inductance if type_skin_effect != False"""

    # Inlined from Methods.Simulation.Electrical.comp_power
    def comp_power(self, out_dict, machine):
        """Compute the electrical average power

        Parameters
        ----------
        self : Electrical
            an Electrical object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        """

        qs = machine.stator.winding.qs
        Id, Iq = out_dict["Id"], out_dict["Iq"]
        Ud, Uq = out_dict["Ud"], out_dict["Uq"]

        # All quantities are in RMS
        Pem_av = qs * (Ud * Id + Uq * Iq)

        out_dict["Pem_av"] = Pem_av

        return out_dict

    # Inlined from Methods.Simulation.Electrical.comp_torque
    def comp_torque(self, out_dict, N0):
        """Compute the electrical average torque

        Parameters
        ----------
        self : Electrical
            an Electrical object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        """

        omega = 2 * np.pi * N0 / 60

        P = out_dict["Pem_av"]

        Tem_av = (P - out_dict["Pj_losses"]) / omega

        out_dict["Tem_av"] = Tem_av

        return out_dict

    # Inlined from Methods.Simulation.Electrical.gen_drive
    def gen_drive(self, output):
        """Generate the drive for the equivalent electrical circuit (only PWM drive for now)

        Parameters
        ----------
        self : Electrical
            an Electrical object
        output : Output
            an Output object
        """

        self.get_logger().info("Calculating PWM voltage")

        p = output.simu.machine.get_pole_pair_number()

        # Get PWM object
        PWM = output.elec.PWM

        if PWM.U0 in [0, None]:
            raise Exception("Cannot calculate PWM voltage if PWM.U0 is None or 0")

        # Get operating point
        OP = output.elec.OP

        if PWM.is_star:
            # Calculate modulation index to account for quick variations
            M_I = PWM.get_modulation_index()

            # Number of points depends on modulation index
            PWM.fs /= max([M_I, 0.05])

        # Number of points depends on modulation index
        Nt_tot = int(PWM.fs * PWM.duration)

        # Get time axis
        input_pwm = type(output.simu.input)(
            OP=OP,
            Nt_tot=Nt_tot,
            t_final=PWM.duration,
            current_dir=output.elec.current_dir,
            rot_dir=output.geo.rot_dir,
        )
        Time_PWM = input_pwm.comp_axis_time(p, per_t=1, is_antiper_t=False)

        # Generate PWM signal
        Uabc = PWM.get_data(is_norm=False, Time=Time_PWM)[0]

        # Get phase axis
        stator_label = output.simu.machine.stator.get_label()
        Phase = output.elec.axes_dict["phase_" + stator_label]

        # Create DataTime object
        Us_dt = DataTime(
            name="Stator voltage",
            symbol="U_s",
            unit="V",
            axes=[Time_PWM, Phase],
            values=Uabc,
        )

        # Get DataFreq object and frequency axis by taking FFT
        Us_df = Us_dt.get_data_along("freqs<" + str(self.freq_max), "phase")
        Freqs = Us_df.axes[0]
        freqs = Freqs.get_values()

        # Filter frequencies with low amplitude and create new frequency axis
        Un_norm = np.linalg.norm(Us_df.values, axis=-1)
        Iamp_n = Un_norm > 1e-2 * Un_norm.max()
        Us_df.axes[0] = Data1D(
            name=Freqs.name,
            unit=Freqs.unit,
            symbol=Freqs.symbol,
            values=freqs[Iamp_n],
            normalizations=Freqs.normalizations,
            is_components=False,
            symmetries=Freqs.symmetries,
        )
        Us_df.values = Us_df.values[Iamp_n, :]

        # Store voltage spectrum in OutElec
        output.elec.Us = Us_dt.to_datadual(datafreq=Us_df)

        # Store Time_PWM axis in axes_dict
        output.elec.axes_dict["time"] = Time_PWM

    # Inlined from Methods.Simulation.Electrical.run
    def run(self):
        """Run the Electrical module"""
        if self.parent is None:
            raise InputError(
                "The Electrical object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")

        self.get_logger().info("Starting Electric module")

        output = self.parent.parent

        machine = output.simu.machine

        if self.eec is None:
            # Init EEC depending on machine type
            if isinstance(machine, MachineSCIM):
                self.eec = EEC_SCIM()
            elif isinstance(machine, (MachineSIPMSM, MachineIPMSM)):
                self.eec = EEC_PMSM()
        else:
            # Check that EEC is consistent with machine type
            if isinstance(machine, MachineSCIM) and not isinstance(self.eec, EEC_SCIM):
                raise Exception(
                    "Cannot run Electrical model if machine is SCIM and eec is not EEC_SCIM"
                )
            elif isinstance(machine, (MachineSIPMSM, MachineIPMSM)) and not isinstance(
                self.eec, EEC_PMSM
            ):
                raise Exception(
                    "Cannot run Electrical model if machine is PMSM and eec is not EEC_PMSM"
                )

        # Initialize all the parameters of the EEC
        eec_out = self.eec.copy()  # Keep reference
        output.elec.eec = eec_out  # For parent setup
        # EEC will be computed on:
        eec_out.Tsta = self.Tsta
        eec_out.Trot = self.Trot
        eec_out.OP = output.elec.OP

        # LUT should contains a full EEC at given OP/T
        if self.LUT_enforced is not None:
            eec_out.clear_parameters()  # Remove eec enforced parameters to use LUT ones
            eec_out.type_skin_effect = self.LUT_enforced.simu.elec.eec.type_skin_effect
            eec_out.update_from_ref(self.LUT_enforced)
        else:
            # Compute/Enforce parameters of the electrical equivalent circuit
            eec_out.comp_parameters()

        if output.elec.PWM is None:
            # Solve the electrical equivalent circuit for fundamental only
            out_dict = eec_out.solve()
        else:
            # Generate voltage signal (PWM signal generation is the only strategy for now)
            if output.elec.PWM.U0 is None:
                # Current driven mode
                # Solve the electrical equivalent circuit for fundamental current
                # to get fundamental phase voltage
                out_dict = eec_out.solve()
                U0c = out_dict["Ud"] + 1j * out_dict["Uq"]
                output.elec.PWM.U0 = abs(U0c)
                output.elec.PWM.Phi0 = np.angle(U0c)

                # Calculate PWM voltage
                self.gen_drive(output)

            else:
                # Voltage driven mode
                # Calculate PWM voltage first
                self.gen_drive(output)

                # Solve the electrical equivalent circuit for fundamental voltage
                # to get fundamental current
                out_dict = eec_out.solve()

            # Solve for each voltage harmonics in case of PWM
            out_dict["Is_PWM"] = eec_out.solve_PWM(
                output,
                is_skin_effect_inductance=self.is_skin_effect_inductance
                and self.type_skin_effect != 0,
            )

        # Compute losses due to Joule effects
        out_dict = eec_out.comp_joule_losses(out_dict, machine)

        # Compute electromagnetic power
        out_dict = self.comp_power(out_dict, machine)

        # Compute torque
        self.comp_torque(out_dict, output.elec.OP.get_N0())

        # Store electrical quantities contained in out_dict in OutElec, as Data object if necessary
        output.elec.store(out_dict)
