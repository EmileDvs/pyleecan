# Experimental dataclass generated from Generator/ClassesRef/Simulation/EEC_PMSM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from pylab import False_

from ..Functions_new.Electrical.dqh_transformation_freq import dqh2n_DataFreq
from .data_1d import Data1D
from .data_freq import DataFreq
from .data_linspace import DataLinspace
from .data_time import DataTime
from .eec import EEC


@dataclass(eq=False)
class EEC_PMSM(EEC):
    """Electrical Equivalent Circuit of Permanent Magnet Synchronous Machines

    Attributes
    ----------
    Ld : float or None
        Stator winding inductance along d-axis
        Unit: H; Default: None
    Lq : float or None
        Stator winding inductance along q-axis
        Unit: H; Default: None
    Phid : float or None
        Stator winding flux along d-axis
        Unit: Wb; Default: None
    Phiq : float or None
        Stator winding flux along q-axis
        Unit: Wb; Default: None
    Phid_mag : float or None
        Stator winding flux along d-axis in open-circuit (rotor flux linkage)
        Unit: Wb; Default: None
    Phiq_mag : float or None
        Stator winding flux along q-axis in open-circuit (rotor flux linkage)
        Unit: Wb; Default: None
    """

    Ld: float | None = None
    """Stator winding inductance along d-axis"""
    Lq: float | None = None
    """Stator winding inductance along q-axis"""
    Phid: float | None = None
    """Stator winding flux along d-axis"""
    Phiq: float | None = None
    """Stator winding flux along q-axis"""
    Phid_mag: float | None = None
    """Stator winding flux along d-axis in open-circuit (rotor flux linkage)"""
    Phiq_mag: float | None = None
    """Stator winding flux along q-axis in open-circuit (rotor flux linkage)"""

    # Inlined from Methods.Simulation.EEC_PMSM.clear_parameters
    def clear_parameters(self):
        """Clear all the parameters of an EEC_PMSM

        Parameters
        ----------
        self : EEC_PMSM
            An EEC_PMSM object
        """

        self.R1 = None
        self.Phid = None
        self.Phiq = None
        self.Phid_mag = None
        self.Phiq_mag = None
        self.Ld = None
        self.Lq = None
        self.Xkr_skinS, self.Xke_skinS = 1, 1
        self.Xkr_skinR, self.Xke_skinR = 1, 1

    # Inlined from Methods.Simulation.EEC_PMSM.comp_BEMF_harmonics
    def comp_BEMF_harmonics(Phi_A, Phi_B, Phi_C, delta, time, is_test=False_):
        """
        Compute the back electromotive force harmonics from magnet fluxes (PMSM)

        Parameters
        ----------
        Phi_A: Magnetic flux of phase A
        Phi_B: Magnetic flux of phase B
        Phi_C: Magnetic flux of phase C
        delta: Rotor angular position
        time: time vector

        """

        # Park transformation (keep the amplitude factor=2/3)
        Phi_d = (
            2
            / 3
            * (
                Phi_A * np.cos(delta)
                + Phi_B * np.cos(delta - 2 * np.pi / 3)
                + Phi_C * np.cos(delta + 2 * np.pi / 3)
            )
        )
        Phi_q = (
            2
            / 3
            * (
                -Phi_A * np.sin(delta)
                - Phi_B * np.sin(delta - 2 * np.pi / 3)
                - Phi_C * np.sin(delta + 2 * np.pi / 3)
            )
        )
        Phi_h = 2 / 3 * 1 / 2 * (Phi_A + Phi_B + Phi_C)

        # Create time vector in form of DataLinspace
        time_axis = DataLinspace(
            name="time",
            unit="s",
            initial=0,
            final=time[-1],
            number=len(time),
            include_endpoint=True,
        )

        # Load Phi into DataTime
        # Phi_A_data = DataTime(
        #     name="Phi_A",
        #     symbol="Phi_A",
        #     unit="Wb",
        #     normalizations=None,
        #     axes=[time_axis],
        #     values=Phi_A,
        # )

        # Phi_B_data = DataTime(
        #     name="Phi_B",
        #     symbol="Phi_B",
        #     unit="Wb",
        #     normalizations=None,
        #     axes=[time_axis],
        #     values=Phi_B,
        # )
        # Phi_C_data = DataTime(
        #     name="Phi_C",
        #     symbol="Phi_C",
        #     unit="Wb",
        #     normalizations=None,
        #     axes=[time_axis],
        #     values=Phi_C,
        # )

        Phi_d_data = DataTime(
            name="Phi_d",
            symbol="Phi_d",
            unit="Wb",
            normalizations=None,
            axes=[time_axis],
            values=Phi_d,
        )

        Phi_q_data = DataTime(
            name="Phi_q",
            symbol="Phi_q",
            unit="Wb",
            normalizations=None,
            axes=[time_axis],
            values=Phi_q,
        )
        Phi_h_data = DataTime(
            name="Phi_h",
            symbol="Phi_h",
            unit="Wb",
            normalizations=None,
            axes=[time_axis],
            values=Phi_h,
        )

        # Phi_q_data.plot_2D_Data("time")
        # Phi_q_data.plot_2D_Data("freqs", type_plot='curve')
        # plt.show()

        # Calculate FFT for Phi on the dq0 frame
        d = Phi_d_data.get_along("freqs")
        freqs_d = d["freqs"]
        complx_d = d["Phi_d"]

        q = Phi_q_data.get_along("freqs")
        freqs_q = q["freqs"]
        complx_q = q["Phi_q"]

        h = Phi_h_data.get_along("freqs")
        freqs_h = h["freqs"]
        complx_h = h["Phi_h"]

        # Calculate back-emf (E) on dq0 frame
        E_d = -2 * np.pi * freqs_q * complx_q + 2 * np.pi * freqs_d * complx_d * 1j
        E_q = 2 * np.pi * freqs_d * complx_d + 2 * np.pi * freqs_q * complx_q * 1j
        E_h = 2 * np.pi * freqs_h * complx_h * 1j

        if is_test:
            # Example:
            N = 10000
            # sample spacing
            T = 1.0 / 20000
            time = np.linspace(0.0, N * T, N, endpoint=False)
            Phi_A = (
                0.5 * np.cos(50.0 * 2.0 * np.pi * time)
                + 0.001 * np.cos(100 * 2.0 * np.pi * time)
                + 0.0009 * np.cos(150 * 2.0 * np.pi * time)
            )
            Phi_B = (
                0.5 * np.cos(50.0 * 2.0 * np.pi * time - 2 * np.pi / 3)
                + 0.001 * np.cos(100 * 2.0 * np.pi * time - 2 * np.pi / 3)
                + 0.0009 * np.cos(150 * 2.0 * np.pi * time - 2 * np.pi / 3)
            )
            Phi_C = (
                0.5 * np.cos(50.0 * 2.0 * np.pi * time + 2 * np.pi / 3)
                + 0.001 * np.cos(100 * 2.0 * np.pi * time + 2 * np.pi / 3)
                + 0.0009 * np.cos(150 * 2.0 * np.pi * time + 2 * np.pi / 3)
            )
            delta = 50.0 * 2.0 * np.pi * time

            E_d, E_q, E_h, freqs_d, freqs_q, freqs_h = comp_BEMF_harmonics(
                Phi_A=Phi_A, Phi_B=Phi_B, Phi_C=Phi_C, delta=delta, time=time
            )

            fig, axs = plt.subplots(3)
            axs[0].plot(freqs_d, abs(E_d))
            axs[1].plot(freqs_q, abs(E_q))
            axs[2].plot(freqs_h, abs(E_h))
            plt.show()

        return E_d, E_q, E_h, freqs_d, freqs_q, freqs_h

    # Inlined from Methods.Simulation.EEC_PMSM.comp_joule_losses
    def comp_joule_losses(self, out_dict, machine):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        machine : Machine
            a Machine object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        qs = machine.stator.winding.qs
        Id, Iq = out_dict["Id"], out_dict["Iq"]
        R1 = self.R1

        # Id and Iq are in RMS
        Pj_losses = qs * R1 * (Id**2 + Iq**2)

        out_dict["Pj_losses"] = Pj_losses

        return out_dict

    # Inlined from Methods.Simulation.EEC_PMSM.comp_Ld
    def comp_Ld(self):
        """Compute and set the stator winding inductance along d-axis for the EEC

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        """

        Id = self.OP.get_Id_Iq()["Id"]
        if Id not in [None, 0]:
            if self.Phid is None:
                self.comp_Phidq()
            if self.Phid_mag is None:
                self.comp_Phidq_mag()
            self.Ld = (self.Phid - self.Phid_mag) / Id
        else:
            self.Ld = None

    # Inlined from Methods.Simulation.EEC_PMSM.comp_Lq
    def comp_Lq(self):
        """Compute and set the stator winding inductance along q-axis for the EEC

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        """

        Iq = self.OP.get_Id_Iq()["Iq"]
        if Iq not in [None, 0]:
            if self.Phiq is None:
                self.comp_Phidq()
            if self.Phiq_mag is None:
                self.comp_Phidq_mag()
            self.Lq = (self.Phiq - self.Phiq_mag) / Iq
        else:
            self.Lq = None

    # Inlined from Methods.Simulation.EEC_PMSM.comp_parameters
    def comp_parameters(self):
        """Compute and set the parameter attributes of the EEC that are not set:
        resistance, skin effect factors, inductance, fluxlinkage and back emf

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        """

        # Check that OP and temperature are set
        assert self.OP is not None
        assert self.Tsta is not None

        if self.type_skin_effect:
            # Update skin effect
            self.comp_skin_effect()

        # Compute stator winding resistance
        if self.R1 is None:
            self.comp_R1()

        # Compute stator winding flux in open-circuit
        if self.Phid_mag is None or self.Phiq_mag is None:
            self.comp_Phidq_mag()

        # Compute stator winding flux
        if self.Phid is None or self.Phiq is None:
            self.comp_Phidq()

        # Compute stator winding inductance along d-axis
        if self.Ld is None:
            self.comp_Ld()

        # Compute stator winding inductance along q-axis
        if self.Lq is None:
            self.comp_Lq()

    # Inlined from Methods.Simulation.EEC_PMSM.comp_Phidq
    def comp_Phidq(self):
        """Compute and set the stator winding flux for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        """
        Phid, Phiq = None, None
        Idq_dict = self.OP.get_Id_Iq()

        if Idq_dict["Id"] is not None and Idq_dict["Iq"] is not None:
            if self.Ld is not None and self.Phid_mag is not None:
                # Calculate Phid from available data
                Phid = self.Ld * Idq_dict["Id"] + self.Phid_mag

            if self.Lq is not None and self.Phiq_mag is not None:
                # Calculate Phiq from available data
                Phiq = self.Lq * Idq_dict["Iq"] + self.Phiq_mag

            if Phid is None or Phiq is None:
                # Calculate Phid and Phiq for the given Id/Iq
                Phi_dqh_mean = self.comp_fluxlinkage(OP=self.OP)[0]

            if Phid is None:
                Phid = Phi_dqh_mean[0]  # * self.Xke_skinS

            if Phiq is None:
                Phiq = Phi_dqh_mean[1]  # * self.Xke_skinS

        self.Phid = Phid
        self.Phiq = Phiq

    # Inlined from Methods.Simulation.EEC_PMSM.comp_Phidq_mag
    def comp_Phidq_mag(self):
        """Compute and set the stator winding flux in open-circuit for the EEC

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        """
        OP_oc = self.OP.copy()
        OP_oc.Id_ref = 0
        OP_oc.Iq_ref = 0

        Phi_dqh_mag_mean = self.comp_fluxlinkage(OP=OP_oc)[0]

        self.Phid_mag = float(Phi_dqh_mag_mean[0])
        self.Phiq_mag = float(Phi_dqh_mag_mean[1])

    # Inlined from Methods.Simulation.EEC_PMSM.comp_torque_sync_rel
    def comp_torque_sync_rel(self):
        """Calculate synchronous and reluctant torque

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object
        qs: int
            Number of stator winding phase
        p: int
            Number of pole pairs

        Returns
        ------
        Tem_sync : float or ndarray
            Synchronous torque [N.m]
        Tem_rel : float or ndarray
            Reluctant torque [N.m]
        """

        machine = self.get_machine_from_parent()
        qs = machine.stator.winding.qs
        p = machine.get_pole_pair_number()

        Id = self.OP.get_Id_Iq()["Id"]
        Iq = self.OP.get_Id_Iq()["Iq"]
        Phid = self.Phid
        Phiq = self.Phiq

        if self.Phid_mag is None:
            # Recalculate dqh flux due to permanent magnets
            self.comp_Phidq_mag()

        Phid_mag = self.Phid_mag

        Tem_sync = qs * p * Phid_mag * Iq

        Tem_rel = qs * p * ((Phid - Phid_mag) * Iq - Phiq * Id)

        return Tem_sync, Tem_rel

    # Inlined from Methods.Simulation.EEC_PMSM.solve
    def solve(self):
        """Compute the parameters dict for the equivalent electrical circuit
        cf "Advanced Electrical Drives, analysis, modeling, control"
        Rik de doncker, Duco W.J. Pulle, Andre Veltman, Springer edition

                     <---                               --->
         -----R-----wsLqIq----              -----R-----wsLdId----
        |                     |            |                     |
        |                     |            |                    BEMF
        |                     |            |                     |
         ---------Id----------              ---------Iq----------

                 --->                               --->
                  Ud                                 Uq

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        ws = 2 * np.pi * self.OP.get_felec()

        out_dict = {}

        if self.OP.get_Ud_Uq()["Ud"] is not None:
            # Voltage driven
            # Impedance matrix
            XR = np.array(
                [
                    [self.R1, -ws * self.Lq],
                    [ws * self.Ld, self.R1],
                ]
            )
            # Back emf array
            if self.Phid_mag is not None:
                XE = np.array([-ws * self.Phiq_mag, ws * self.Phid_mag])
            else:
                XE = np.array([0, 0])
            # Voltage array
            XU = np.array([self.OP.get_Ud_Uq()["Ud"], self.OP.get_Ud_Uq()["Uq"]])
            # Solve system to get current array
            XI = np.linalg.solve(XR, XU - XE)

            # Store values in out_dict
            out_dict["Id"] = XI[0]
            out_dict["Iq"] = XI[1]
            out_dict["Ud"] = self.OP.get_Ud_Uq()["Ud"]
            out_dict["Uq"] = self.OP.get_Ud_Uq()["Uq"]

        elif self.OP.get_Id_Iq()["Id"] is not None:
            # Current Driven
            Ud = self.R1 * self.OP.get_Id_Iq()["Id"] - ws * self.Phiq
            Uq = self.R1 * self.OP.get_Id_Iq()["Iq"] + ws * self.Phid
            out_dict["Ud"] = Ud
            out_dict["Uq"] = Uq
            out_dict["Id"] = self.OP.get_Id_Iq()["Id"]
            out_dict["Iq"] = self.OP.get_Id_Iq()["Iq"]

        else:
            raise Exception("Cannot solve EEC if both voltage or current are not given")

        return out_dict

    # Inlined from Methods.Simulation.EEC_PMSM.solve_PWM
    def solve_PWM(self, output, is_dqh_freq=False, is_skin_effect_inductance=False):
        """Get stator current harmonics due to PWM harmonics
        TODO: validation with transient FEA simulation

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object
        output: Output
            An Output object
        is_dqh_freq: bool
            True to consider frequencies in dqh frame (generate resonances in current)
        is_skin_effect_inductance : bool
            True to include skin effect on inductance

        Returns
        ------
        Is_PWM : DataFreq
            Stator current harmonics as DataFreq
        """
        self.get_logger().info("Calculating PWM current harmonics")

        # Get fundamental frequency
        felec = self.OP.get_felec()

        # Get stator winding phase number
        qs = output.simu.machine.stator.winding.qs

        # Get PWM frequencies in abc frame
        freqs_n = output.elec.Us.get_axes("freqs")[0].values

        # Get stator voltage harmonics in dqh frame
        Us_PWM = output.elec.get_Us(is_dqh=True, is_harm_only=True, is_freq=True)
        result = Us_PWM.get_along("freqs", "phase")
        Udqh_val = result[Us_PWM.symbol]
        freqs_dqh = result["freqs"]

        # # Plot Us_n and U_dqh
        # output.elec.Us.plot_2D_Data("freqs", "phase[0]")
        # Us_PWM.plot_2D_Data("freqs=[0,200]", "phase[0]")

        # Filter Udqh_val zeros values
        Udqh_norm = np.linalg.norm(Udqh_val, axis=-1)
        Iamp = Udqh_norm > 1e-6 * Udqh_norm.max()
        freqs_dqh = freqs_dqh[Iamp]
        Udqh_val = Udqh_val[Iamp, :]

        # Init current harmonics matrix
        Idqh_val = np.zeros((freqs_dqh.size, qs), dtype=complex)

        if is_dqh_freq:
            # Take dqh frequency values
            fn_dqh = freqs_dqh
        else:
            # Look for frequency value in n frame for each frequency in dqh frame
            fn_dqh = np.zeros(freqs_dqh.size)
            fn_pos = freqs_dqh + felec
            fn_neg = freqs_dqh - felec
            for ii, (fpos, fneg) in enumerate(zip(fn_pos, fn_neg)):
                fn_ii = None
                jj = 0
                while fn_ii is None and jj < freqs_n.size:
                    if (
                        np.abs(fpos - freqs_n[jj]) < 1e-4
                        or np.abs(fneg - freqs_n[jj]) < 1e-4
                    ):
                        fn_ii = freqs_n[jj]
                    elif (
                        np.abs(fpos + freqs_n[jj]) < 1e-4
                        or np.abs(fneg + freqs_n[jj]) < 1e-4
                    ):
                        fn_ii = -freqs_n[jj]
                    else:
                        jj += 1
                if fn_ii is None:
                    raise Exception("Cannot map dqh frequency back to n frequency")
                else:
                    fn_dqh[ii] = fn_ii

            fn_dqh[np.abs(fn_dqh) < felec] = felec

        if self.type_skin_effect:
            CondS = output.simu.machine.stator.winding.conductor
            # Calculate skin effect coefficient on stator resistance
            Xkr_skinS = CondS.comp_skin_effect_resistance(
                freq=fn_dqh, T_op=self.Tsta, T_ref=20
            )
            if is_skin_effect_inductance:
                # Calculate skin effect coefficient on stator inductances
                Xke_skinS = CondS.comp_skin_effect_inductance(
                    freq=fn_dqh, T_op=self.Tsta, T_ref=20
                )
            else:
                Xke_skinS = 1
        else:
            Xkr_skinS, Xke_skinS = 1, 1

        # Calculate impedances to solve linear system for all frequencies
        # (from Wenli Liang thesis if is_dqh_freq=True but generate resonances in current harmonics at specific frequencies)
        we = int(is_dqh_freq) * 2 * np.pi * felec
        wh = 2 * np.pi * fn_dqh
        a = self.R1 * Xkr_skinS + 1j * wh * self.Ld * Xke_skinS
        b = -we * self.Lq * Xke_skinS
        c = we * self.Ld * Xke_skinS
        d = self.R1 * Xkr_skinS + 1j * wh * self.Lq * Xke_skinS
        det = a * d - c * b

        # Calculate current harmonics
        # Calculate Id
        Idqh_val[:, 0] = (d * Udqh_val[:, 0] - b * Udqh_val[:, 1]) / det
        # Calculate Iq
        Idqh_val[:, 1] = (-c * Udqh_val[:, 0] + a * Udqh_val[:, 1]) / det

        # Create frequency axis
        Freqs_PWM = Us_PWM.axes[0]

        norm_freq = {}
        if Freqs_PWM.normalizations is not None and len(Freqs_PWM.normalizations) > 0:
            for key, val in Freqs_PWM.normalizations.items():
                norm_freq[key] = val.copy()

        Freqs = Data1D(
            name=Freqs_PWM.name,
            symbol=Freqs_PWM.symbol,
            unit=Freqs_PWM.unit,
            values=freqs_dqh,
            normalizations=norm_freq,
        )

        # Create DataFreq in DQH Frame
        Is_PWM_dqh = DataFreq(
            name="Stator current",
            unit="A",
            symbol="I_s",
            axes=[Freqs, Us_PWM.axes[1].copy()],
            values=Idqh_val,
        )

        # # Plot PWM current in dqh frame over frequency
        # Is_PWM_dqh.plot_2D_Data("freqs=[0,20000]", "phase[]")

        # Convert I_dqh spectrum back to stator frame
        Is_PWM_n = dqh2n_DataFreq(
            Is_PWM_dqh,
            n=qs,
            phase_dir=output.elec.phase_dir,
            current_dir=output.elec.current_dir,
            felec=output.elec.OP.felec,
            is_n_rms=False,
        )

        # Reduce current to original voltage frequencies
        Is_PWM_n = Is_PWM_n.get_data_along("freqs=" + str(freqs_n.tolist()), "phase")

        return Is_PWM_n

    # Inlined from Methods.Simulation.EEC_PMSM.update_from_ref
    def update_from_ref(self, LUT_ref):
        """Compute and set the parameter attributes of the EEC from a reference LUT:
        resistance, skin effect factors, inductance, fluxlinkage and back emf

        Parameters
        ----------
        self : EEC_PMSM
            an EEC_PMSM object
        LUT_ref : LUTdq
            a LUTdq object

        """

        if self.type_skin_effect:
            # Update skin effect
            self.comp_skin_effect()

        eec_ref = LUT_ref.get_eec()

        if eec_ref is None:
            eec_ref = type(self)()

        Tsta_ref, Trot_ref = eec_ref.Tsta, eec_ref.Trot
        Xkr_skinS_ref, Xke_skinS_ref = eec_ref.Xkr_skinS, eec_ref.Xke_skinS
        # Xkr_skinR_ref, Xke_skinR_ref = eec_ref.Xkr_skinR, eec_ref.Xke_skinR

        Idq_dict = self.OP.get_Id_Iq()
        Id = Idq_dict["Id"]
        Iq = Idq_dict["Iq"]

        # Update stator winding resistance
        if eec_ref.R1 is None:
            self.comp_R1()
        else:
            self.comp_R1(R1_ref=eec_ref.R1 / Xkr_skinS_ref, T_ref=Tsta_ref)

        # Update stator winding flux in open-circuit
        Phi_dqh_mag = LUT_ref.get_Phi_dqh_mag_mean()
        if Phi_dqh_mag is not None:
            self.Phid_mag = Phi_dqh_mag[0]
            self.Phiq_mag = Phi_dqh_mag[1]

        # Compute stator winding flux
        Phi_dqh = LUT_ref.interp_Phi_dqh(Id=Id, Iq=Iq)
        self.Phid = Phi_dqh[0]
        self.Phiq = Phi_dqh[1]

        # Compute stator winding inductance
        Ldqh = LUT_ref.get_L_dqh(Id=Id, Iq=Iq, Phi_dqh=Phi_dqh)
        if Ldqh is not None:
            self.Ld = Ldqh[0]
            self.Lq = Ldqh[1]
