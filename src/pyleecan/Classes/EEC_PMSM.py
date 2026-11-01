# File generated according to Generator/ClassesRef/Simulation/EEC_PMSM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/EEC_PMSM"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pylab import False_

from pyleecan.Classes._check import check_var
from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataFreq import DataFreq
from pyleecan.Classes.DataLinspace import DataLinspace
from pyleecan.Classes.DataTime import DataTime
from pyleecan.Classes.EEC import EEC
from pyleecan.Functions.Electrical.dqh_transformation_freq import dqh2n_DataFreq
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class EEC_PMSM(EEC):
    """Electrical Equivalent Circuit of Permanent Magnet Synchronous Machines"""

    VERSION = 1

    # cf Methods.Simulation.EEC_PMSM.clear_parameters
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

    # cf Methods.Simulation.EEC_PMSM.comp_BEMF_harmonics
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

    # cf Methods.Simulation.EEC_PMSM.comp_joule_losses
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

    # cf Methods.Simulation.EEC_PMSM.comp_Ld
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

    # cf Methods.Simulation.EEC_PMSM.comp_Lq
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

    # cf Methods.Simulation.EEC_PMSM.comp_parameters
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

    # cf Methods.Simulation.EEC_PMSM.comp_Phidq
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

    # cf Methods.Simulation.EEC_PMSM.comp_Phidq_mag
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

    # cf Methods.Simulation.EEC_PMSM.comp_torque_sync_rel
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

    # cf Methods.Simulation.EEC_PMSM.solve
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

        out_dict = dict()

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

    # cf Methods.Simulation.EEC_PMSM.solve_PWM
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

        norm_freq = dict()
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

    # cf Methods.Simulation.EEC_PMSM.update_from_ref
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Ld=None,
        Lq=None,
        Phid=None,
        Phiq=None,
        Phid_mag=None,
        Phiq_mag=None,
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
            if "Ld" in list(init_dict.keys()):
                Ld = init_dict["Ld"]
            if "Lq" in list(init_dict.keys()):
                Lq = init_dict["Lq"]
            if "Phid" in list(init_dict.keys()):
                Phid = init_dict["Phid"]
            if "Phiq" in list(init_dict.keys()):
                Phiq = init_dict["Phiq"]
            if "Phid_mag" in list(init_dict.keys()):
                Phid_mag = init_dict["Phid_mag"]
            if "Phiq_mag" in list(init_dict.keys()):
                Phiq_mag = init_dict["Phiq_mag"]
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
        self.Ld = Ld
        self.Lq = Lq
        self.Phid = Phid
        self.Phiq = Phiq
        self.Phid_mag = Phid_mag
        self.Phiq_mag = Phiq_mag
        # Call EEC init
        super(EEC_PMSM, self).__init__(
            type_skin_effect=type_skin_effect,
            OP=OP,
            Tsta=Tsta,
            Trot=Trot,
            Xkr_skinS=Xkr_skinS,
            Xke_skinS=Xke_skinS,
            Xkr_skinR=Xkr_skinR,
            Xke_skinR=Xke_skinR,
            R1=R1,
            fluxlink=fluxlink,
        )
        # The class is frozen (in EEC init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        EEC_PMSM_str = ""
        # Get the properties inherited from EEC
        EEC_PMSM_str += super(EEC_PMSM, self).__str__()
        EEC_PMSM_str += "Ld = " + str(self.Ld) + linesep
        EEC_PMSM_str += "Lq = " + str(self.Lq) + linesep
        EEC_PMSM_str += "Phid = " + str(self.Phid) + linesep
        EEC_PMSM_str += "Phiq = " + str(self.Phiq) + linesep
        EEC_PMSM_str += "Phid_mag = " + str(self.Phid_mag) + linesep
        EEC_PMSM_str += "Phiq_mag = " + str(self.Phiq_mag) + linesep
        return EEC_PMSM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from EEC
        if not super(EEC_PMSM, self).__eq__(other):
            return False
        if other.Ld != self.Ld:
            return False
        if other.Lq != self.Lq:
            return False
        if other.Phid != self.Phid:
            return False
        if other.Phiq != self.Phiq:
            return False
        if other.Phid_mag != self.Phid_mag:
            return False
        if other.Phiq_mag != self.Phiq_mag:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from EEC
        diff_list.extend(
            super(EEC_PMSM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Ld is not None
            and self._Ld is not None
            and np.isnan(other._Ld)
            and np.isnan(self._Ld)
        ):
            pass
        elif other._Ld != self._Ld:
            if is_add_value:
                val_str = " (self=" + str(self._Ld) + ", other=" + str(other._Ld) + ")"
                diff_list.append(name + ".Ld" + val_str)
            else:
                diff_list.append(name + ".Ld")
        if (
            other._Lq is not None
            and self._Lq is not None
            and np.isnan(other._Lq)
            and np.isnan(self._Lq)
        ):
            pass
        elif other._Lq != self._Lq:
            if is_add_value:
                val_str = " (self=" + str(self._Lq) + ", other=" + str(other._Lq) + ")"
                diff_list.append(name + ".Lq" + val_str)
            else:
                diff_list.append(name + ".Lq")
        if (
            other._Phid is not None
            and self._Phid is not None
            and np.isnan(other._Phid)
            and np.isnan(self._Phid)
        ):
            pass
        elif other._Phid != self._Phid:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Phid) + ", other=" + str(other._Phid) + ")"
                )
                diff_list.append(name + ".Phid" + val_str)
            else:
                diff_list.append(name + ".Phid")
        if (
            other._Phiq is not None
            and self._Phiq is not None
            and np.isnan(other._Phiq)
            and np.isnan(self._Phiq)
        ):
            pass
        elif other._Phiq != self._Phiq:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Phiq) + ", other=" + str(other._Phiq) + ")"
                )
                diff_list.append(name + ".Phiq" + val_str)
            else:
                diff_list.append(name + ".Phiq")
        if (
            other._Phid_mag is not None
            and self._Phid_mag is not None
            and np.isnan(other._Phid_mag)
            and np.isnan(self._Phid_mag)
        ):
            pass
        elif other._Phid_mag != self._Phid_mag:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Phid_mag)
                    + ", other="
                    + str(other._Phid_mag)
                    + ")"
                )
                diff_list.append(name + ".Phid_mag" + val_str)
            else:
                diff_list.append(name + ".Phid_mag")
        if (
            other._Phiq_mag is not None
            and self._Phiq_mag is not None
            and np.isnan(other._Phiq_mag)
            and np.isnan(self._Phiq_mag)
        ):
            pass
        elif other._Phiq_mag != self._Phiq_mag:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Phiq_mag)
                    + ", other="
                    + str(other._Phiq_mag)
                    + ")"
                )
                diff_list.append(name + ".Phiq_mag" + val_str)
            else:
                diff_list.append(name + ".Phiq_mag")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from EEC
        S += super(EEC_PMSM, self).__sizeof__()
        S += getsizeof(self.Ld)
        S += getsizeof(self.Lq)
        S += getsizeof(self.Phid)
        S += getsizeof(self.Phiq)
        S += getsizeof(self.Phid_mag)
        S += getsizeof(self.Phiq_mag)
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

        # Get the properties inherited from EEC
        EEC_PMSM_dict = super(EEC_PMSM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        EEC_PMSM_dict["Ld"] = self.Ld
        EEC_PMSM_dict["Lq"] = self.Lq
        EEC_PMSM_dict["Phid"] = self.Phid
        EEC_PMSM_dict["Phiq"] = self.Phiq
        EEC_PMSM_dict["Phid_mag"] = self.Phid_mag
        EEC_PMSM_dict["Phiq_mag"] = self.Phiq_mag
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        EEC_PMSM_dict["__class__"] = "EEC_PMSM"
        return EEC_PMSM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Ld_val = self.Ld
        Lq_val = self.Lq
        Phid_val = self.Phid
        Phiq_val = self.Phiq
        Phid_mag_val = self.Phid_mag
        Phiq_mag_val = self.Phiq_mag
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
            Ld=Ld_val,
            Lq=Lq_val,
            Phid=Phid_val,
            Phiq=Phiq_val,
            Phid_mag=Phid_mag_val,
            Phiq_mag=Phiq_mag_val,
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

        self.Ld = None
        self.Lq = None
        self.Phid = None
        self.Phiq = None
        self.Phid_mag = None
        self.Phiq_mag = None
        # Set to None the properties inherited from EEC
        super(EEC_PMSM, self)._set_None()

    def _get_Ld(self):
        """getter of Ld"""
        return self._Ld

    def _set_Ld(self, value):
        """setter of Ld"""
        check_var("Ld", value, "float")
        self._Ld = value

    Ld = property(
        fget=_get_Ld,
        fset=_set_Ld,
        doc="""Stator winding inductance along d-axis

        :Type: float
        """,
    )

    def _get_Lq(self):
        """getter of Lq"""
        return self._Lq

    def _set_Lq(self, value):
        """setter of Lq"""
        check_var("Lq", value, "float")
        self._Lq = value

    Lq = property(
        fget=_get_Lq,
        fset=_set_Lq,
        doc="""Stator winding inductance along q-axis

        :Type: float
        """,
    )

    def _get_Phid(self):
        """getter of Phid"""
        return self._Phid

    def _set_Phid(self, value):
        """setter of Phid"""
        check_var("Phid", value, "float")
        self._Phid = value

    Phid = property(
        fget=_get_Phid,
        fset=_set_Phid,
        doc="""Stator winding flux along d-axis

        :Type: float
        """,
    )

    def _get_Phiq(self):
        """getter of Phiq"""
        return self._Phiq

    def _set_Phiq(self, value):
        """setter of Phiq"""
        check_var("Phiq", value, "float")
        self._Phiq = value

    Phiq = property(
        fget=_get_Phiq,
        fset=_set_Phiq,
        doc="""Stator winding flux along q-axis

        :Type: float
        """,
    )

    def _get_Phid_mag(self):
        """getter of Phid_mag"""
        return self._Phid_mag

    def _set_Phid_mag(self, value):
        """setter of Phid_mag"""
        check_var("Phid_mag", value, "float")
        self._Phid_mag = value

    Phid_mag = property(
        fget=_get_Phid_mag,
        fset=_set_Phid_mag,
        doc="""Stator winding flux along d-axis in open-circuit (rotor flux linkage)

        :Type: float
        """,
    )

    def _get_Phiq_mag(self):
        """getter of Phiq_mag"""
        return self._Phiq_mag

    def _set_Phiq_mag(self, value):
        """setter of Phiq_mag"""
        check_var("Phiq_mag", value, "float")
        self._Phiq_mag = value

    Phiq_mag = property(
        fget=_get_Phiq_mag,
        fset=_set_Phiq_mag,
        doc="""Stator winding flux along q-axis in open-circuit (rotor flux linkage)

        :Type: float
        """,
    )
