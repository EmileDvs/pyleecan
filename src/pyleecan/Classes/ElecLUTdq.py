# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Simulation/ElecLUTdq.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/ElecLUTdq
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
from pyleecan.Classes.Electrical import Electrical

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from pyleecan.Classes.LUTdq import LUTdq
from pyleecan.Classes.EEC_PMSM import EEC_PMSM
from pyleecan.Classes.OutLoss import OutLoss
from pyleecan.Methods.Simulation.Input import InputError


from pyleecan.Classes._check import InitUnKnowClassError


class ElecLUTdq(Electrical):
    """Electric module object for electrical equivalent circuit simulation"""

    VERSION = 1

    # cf Methods.Simulation.ElecLUTdq.comp_LUTdq
    def comp_LUTdq(self):
        """Compute Look up table function of Id / Iq

        Parameters
        ----------
        self : ElecLUTdq
            a ElecLUTdq object

        Returns
        ----------
        LUT : LUTdq
            Calculated look-up table
        """

        if self.LUT_simu is None:
            raise Exception("Cannot calculate LUTdq if self.LUT_simu is None")
        else:
            simu = self.LUT_simu.copy()

        N0 = self.parent.input.OP.N0

        if self.is_grid_dq:
            N_OP = self.n_Id * self.n_Iq
            Id, Iq = np.meshgrid(
                np.linspace(self.Id_min, self.Id_max, self.n_Id),
                np.linspace(self.Iq_min, self.Iq_max, self.n_Iq),
            )
        else:
            Id0 = np.linspace(self.Id_min, self.Id_max, self.n_Id)
            Iq0 = np.linspace(self.Iq_min, self.Iq_max, self.n_Iq)
            if 0 in Id0 and 0 in Iq0:
                Iq0 = np.array([val for val in Iq0 if val != 0])
            N_OP = self.n_Id + Iq0.size
            Id = np.zeros(N_OP)
            Iq = np.zeros(N_OP)
            Id[: self.n_Id] = Id0
            Iq[self.n_Id :] = Iq0

        OP_matrix = np.zeros((N_OP, 3))
        OP_matrix[:, 0] = N0
        OP_matrix[:, 1] = Id.ravel()
        OP_matrix[:, 2] = Iq.ravel()

        simu.machine = self.parent.machine
        simu.var_simu.set_OP_array(
            OP_matrix, "N0", "Id", "Iq", is_update_input=True, input_index=0
        )

        LUT = LUTdq(simu=simu)

        LUT.simu.run()

        return LUT

    # cf Methods.Simulation.ElecLUTdq.run
    def run(self):
        """Run the ElecLUTdq module"""
        if self.parent is None:
            raise InputError(
                "The Electrical object must be in a Simulation object to run"
            )
        if self.parent.parent is None:
            raise InputError("The Simulation object must be in an Output object to run")

        self.get_logger().info("Starting Electrical module")

        # Get output, machine and OP
        output = self.parent.parent

        machine = output.simu.machine
        OP = output.elec.OP

        # Get winding resistance
        Rs = machine.stator.comp_resistance_wind(T=self.Tsta)

        # Account for skin effect
        if self.type_skin_effect > 0:
            # Calculate skin effect coefficient
            kr_skin = machine.stator.winding.conductor.comp_skin_effect_resistance(
                T_op=self.Tsta, freq=OP.get_felec()
            )
            Rs *= kr_skin
        else:
            kr_skin = 1

        # Maximum phase current
        if self.Irms_max is None:
            if self.Jrms_max is None:
                raise Exception("Irms_max and Jrms_max cannot be both None")
            # Calculate maximum current function of current density
            Swire = machine.stator.winding.conductor.comp_surface_active()
            Npcp = machine.stator.winding.Npcp
            self.Irms_max = self.Jrms_max * Swire * Npcp
        else:
            self.Irms_max = output.simu.input.Irms_max

        if self.LUT_enforced is not None:
            # Take enforced LUT
            LUT = self.LUT_enforced

            # Get Id_min, Id_max, Iq_min, Iq_max from OP_matrix
            OP_matrix = LUT.get_OP_array("N0", "Id", "Iq")
            self.Id_min = OP_matrix[:, 1].min()
            self.Id_max = OP_matrix[:, 1].max()
            self.Iq_min = OP_matrix[:, 2].min()
            self.Iq_max = OP_matrix[:, 2].max()

        else:
            # Run look up table calculation
            # Check dq current boundaries
            if self.Id_min is None:
                if self.n_Id == 1 and self.Id_max is not None:
                    self.Id_min = self.Id_max
                else:
                    self.Id_min = -self.Irms_max
            if self.Id_max is None:
                if self.n_Id == 1 and self.Id_min is not None:
                    self.Id_max = self.Id_min
                else:
                    self.Id_max = self.Irms_max
            if self.Iq_min is None:
                if self.n_Iq == 1 and self.Iq_max is not None:
                    self.Iq_min = self.Iq_max
                else:
                    self.Iq_min = -self.Irms_max
            if self.Iq_max is None:
                if self.n_Iq == 1 and self.Iq_min is not None:
                    self.Iq_max = self.Iq_min
                else:
                    self.Iq_max = self.Irms_max

            # Run method to calculate LUT
            LUT = self.comp_LUTdq()

            # LUT.save(save_path=r"C:\Users\LAP10\Documents\Loss\LUT_eff.h5")

            # Store LUT
            output.simu.elec.LUT_enforced = LUT

        if OP.Pem_av_ref is not None or OP.Pem_av_in is not None:
            out_dict = self.solve_power(LUT, Rs)
        else:
            out_dict = self.solve_MTPA(LUT, Rs)

        # Store electrical quantities
        if "P_out" in out_dict:
            output.elec.P_out = out_dict["P_out"]
        if "P_in" in out_dict:
            output.elec.P_in = out_dict["P_in"]
        if "efficiency" in out_dict:
            output.elec.OP.efficiency = out_dict["efficiency"]
        if "Tem_av" in out_dict:
            output.elec.Tem_av = out_dict["Tem_av"]

        # Store voltage and currents
        output.elec.OP.Id_ref = out_dict["Id"]
        output.elec.OP.Iq_ref = out_dict["Iq"]
        output.elec.OP.Ud_ref = out_dict["Ud"]
        output.elec.OP.Uq_ref = out_dict["Uq"]

        # Store EEC parameters
        output.elec.eec = EEC_PMSM(
            Phid=out_dict["Phid"],
            Phiq=out_dict["Phiq"],
            Phid_mag=out_dict["Phid_mag"],
            Phiq_mag=out_dict["Phiq_mag"],
            R1=Rs,
            Tsta=self.Tsta,
            Trot=self.Trot,
            type_skin_effect=self.type_skin_effect,
            Xkr_skinS=kr_skin,
        )
        if "Ld" in out_dict:
            output.elec.eec.Ld = out_dict["Ld"]
        if "Lq" in out_dict:
            output.elec.eec.Lq = out_dict["Lq"]

        if "Pjoule" in out_dict:
            output.elec.Pj_losses = out_dict["Pjoule"]

        if "Pstator" in out_dict:
            # Store losses
            output.loss = OutLoss(
                Pjoule=out_dict["Pjoule"],
                Pstator=out_dict["Pstator"],
                Pmagnet=out_dict["Pmagnet"],
                Protor=out_dict["Protor"],
                Pprox=out_dict["Pprox"],
            )

        # Calculate slot current density
        output.elec.get_Jrms()

        # Calculate linear current density along airgap
        Irms = np.sqrt(output.elec.OP.Id_ref**2 + output.elec.OP.Iq_ref**2)
        Irms_slot = Irms * machine.stator.winding.Ntcoil / machine.stator.winding.Npcp
        slot_pitch = 2 * np.pi / machine.stator.get_Zs() * machine.stator.Rint
        output.elec.Arms = Irms_slot / slot_pitch

        if "Erms" in out_dict:
            # Store back-emf rms value
            output.elec.Erms = out_dict["Erms"]

        if "Tem_rip_pp" in out_dict:
            # Store torque ripple
            output.mag.Tem_rip_pp = out_dict["Tem_rip_pp"]
            output.mag.Tem_rip_norm = out_dict["Tem_rip_norm"]

    # cf Methods.Simulation.ElecLUTdq.solve_MTPA
    def solve_MTPA(self, LUT, Rs):
        """Solve EEC using Maximum Torque Per Ampere strategy with respect to voltage and current constraints

        Parameters
        ----------
        self : ElecLUTdq
            a ElecLUTdq object
        LUT : LUTdq
            Calculated look-up table
        Rs: float
            Stator phase resistance [Ohm]

        Returns
        ----------
        out_dict: dict
            Dict containing all output quantities

        """

        # Get output, machine and OP
        output = self.parent.parent

        machine = output.simu.machine
        OP = output.elec.OP

        # Maximum voltage
        Urms_max = self.Urms_max
        # Maximum current
        Irms_max = self.Irms_max
        # Electrical frequency
        felec = OP.get_felec()
        # Electrical pulsation
        ws = 2 * np.pi * felec
        # Stator winding number of phases
        qs = machine.stator.winding.qs
        # Number of pole pair
        p = machine.get_pole_pair_number()

        # iteration until convergence is reached, and max number of iterations on EEC
        delta_Tem = 1e10
        delta_Tem_max = 0.1
        Nmax = 20
        niter_Tem = 1
        Tem_max_old = 0
        Id_old = 0
        Id_min = self.Id_min
        Id_max = self.Id_max
        Iq_min = self.Iq_min
        Iq_max = self.Iq_max
        Nd = (
            self.n_Id
            if self.n_Id == 1
            else int(self.n_Id * self.n_interp / (self.n_Id + self.n_Iq))
        )
        Nq = (
            self.n_Iq
            if self.n_Iq == 1
            else int(self.n_Iq * self.n_interp / (self.n_Id + self.n_Iq))
        )

        # Check if there is a loss model
        is_loss_model = LUT.simu.loss is not None

        while abs(delta_Tem) > delta_Tem_max and niter_Tem < Nmax:
            # Refine Id/Iq mesh
            Id_vect = np.linspace(Id_min, Id_max, Nd)
            Iq_vect = np.linspace(Iq_min, Iq_max, Nq)
            Id, Iq = np.meshgrid(Id_vect, Iq_vect)
            Id, Iq = Id.ravel(), Iq.ravel()

            # Calculate maximum current
            Imax_interp = np.sqrt(Id**2 + Iq**2)

            # Interpolate Phid/Phiq on the refined mesh
            (Phid, Phiq, Phih) = LUT.interp_Phi_dqh(Id, Iq)

            # Calculate voltage (Ud/Uq) for the refined mesh
            Ud = Rs * Id - Phiq * ws
            Uq = Rs * Iq + Phid * ws
            Umax_interp = np.sqrt(Ud**2 + Uq**2)

            # Calculate electromagnetic torque
            Tem_interp = qs * p * (Phid * Iq - Phiq * Id)

            # Set maximum voltage condition
            U_cond = Umax_interp <= Urms_max

            if is_loss_model:
                # Interpolate losses from LUT
                Ploss_dqh = LUT.interp_Ploss_dqh(Id, Iq, N0=OP.N0)
                Ploss_ovl = np.sum(Ploss_dqh, axis=1)
                Ploss_dqh_wo_Joule = LUT.interp_Ploss_dqh(
                    Id, Iq, N0=OP.N0, exclude_models=["LossModelWinding"]
                )
                # The input power must cover electrical power + additional losses
                P_in = qs * (Ud * Id + Uq * Iq) + np.sum(Ploss_dqh_wo_Joule, axis=1)
            else:
                # Only consider stator Joule losses
                Ploss_ovl = qs * Rs * (Id**2 + Iq**2)
                # The input power must cover electrical power + Joule losses
                P_in = qs * (Ud * Id + Uq * Iq)

            # The output power is the input power minus all losses
            P_out = P_in - Ploss_ovl

            if self.load_rate == 0:
                # Finding indices of operating points satisfying voltage constraint for no torque production
                i0 = np.logical_and(U_cond, Iq == 0)

                # Finding index of operating point for lowest current
                imin = np.argmin(np.abs(Imax_interp[i0]))

                # Transform target from reaching torque to reach minimum Id
                delta_Tem = Id[i0][imin] - Id_old

            else:
                # Set maximum current condition
                I_cond = Imax_interp <= Irms_max

                # Finding indices of operating points satisfying voltage and current constraints
                i0 = np.logical_and(U_cond, I_cond)

                # Finding index of operating point giving maximum positive torque among feasible operating points
                imin = np.argmax(Tem_interp[i0])

                # Maximum torque achieved for N0
                Tem_max = Tem_interp[i0][imin]

                if self.load_rate < 1:
                    # Finding indices of operating points satisfying maximum voltage and torque level
                    i0 = np.logical_and(U_cond, Tem_interp >= self.load_rate * Tem_max)

                    # Finding index of operating points with lowest current among feasible operating points
                    imin = np.argmin(Imax_interp[i0])

                    # Check torque difference
                    delta_Tem = np.abs(self.load_rate * Tem_max - Tem_interp[i0][imin])

                else:
                    # Check if maximum torque changes depending on Id/Iq discretization
                    delta_Tem = Tem_max - Tem_max_old
                    Tem_max_old = Tem_max

            if abs(delta_Tem) > delta_Tem_max:
                # Zoom in Id / Iq grid to achieve better accuracy on output values
                jd = np.where(Id_vect == Id[i0][imin])[0][0]
                jq = np.where(Iq_vect == Iq[i0][imin])[0][0]

                jd_min = max([jd - 1, 0])
                jd_max = min([jd + 1, Nd - 1])
                jq_min = max([jq - 1, 0])
                jq_max = min([jq + 1, Nq - 1])

                Id_min = Id_vect[jd_min]
                Id_max = Id_vect[jd_max]
                Iq_min = Iq_vect[jq_min]
                Iq_max = Iq_vect[jq_max]

            niter_Tem = niter_Tem + 1

        # Launch warnings
        if Umax_interp[i0][imin] > Urms_max:
            self.get_logger().warning("Voltage constraint cannot be reached")

        if Imax_interp[i0][imin] > Irms_max:
            self.get_logger().warning("Current constraint cannot be reached")

        out_dict = dict()

        # Calculate efficiency
        out_dict["P_in"] = P_in[i0][imin]
        out_dict["P_out"] = P_out[i0][imin]
        eff = out_dict["P_out"] / out_dict["P_in"]
        out_dict["efficiency"] = eff if eff > 0 else 0
        # out_dict["efficiency"] = out_dict["P_out"] / out_dict["P_in"]

        # Calculate torque from output power
        out_dict["Tem_av"] = Tem_interp[i0][imin]

        # Store voltage and currents
        out_dict["Id"] = Id[i0][imin]
        out_dict["Iq"] = Iq[i0][imin]
        out_dict["Ud"] = Ud[i0][imin]
        out_dict["Uq"] = Uq[i0][imin]

        # Store dq fluxes
        out_dict["Phid"] = Phid[i0][imin]
        out_dict["Phiq"] = Phiq[i0][imin]

        # Calculate flux linkage and back-emf
        Phidqh_mag = LUT.get_Phi_dqh_mag_mean()
        out_dict["Phid_mag"] = Phidqh_mag[0]
        out_dict["Phiq_mag"] = Phidqh_mag[1]
        out_dict["Erms"] = ws * Phidqh_mag[0]

        # Calculate inductances
        if Id[i0][imin] != 0:
            out_dict["Ld"] = (Phid[i0][imin] - out_dict["Phid_mag"]) / Id[i0][imin]
        if Iq[i0][imin] != 0:
            out_dict["Lq"] = Phiq[i0][imin] / Iq[i0][imin]

        # Calculate torque ripple
        Tem_rip_pp = LUT.interp_Tem_rip_dqh(Id[i0][imin], Iq[i0][imin])
        if Tem_rip_pp is not None:
            out_dict["Tem_rip_pp"] = float(Tem_rip_pp)
            if out_dict["Tem_av"] == 0:
                out_dict["Tem_rip_norm"] = 0
            else:
                out_dict["Tem_rip_norm"] = np.abs(Tem_rip_pp / out_dict["Tem_av"])

        return out_dict

    # cf Methods.Simulation.ElecLUTdq.solve_power
    def solve_power(self, LUT, Rs):
        """Solve EEC to achieve given input / output power with respect to voltage and current constraints

        Parameters
        ----------
        self : ElecLUTdq
            a ElecLUTdq object
        LUT : LUTdq
            Calculated look-up table
        Rs: float
            Stator phase resistance [Ohm]

        Returns
        ----------
        out_dict: dict
            Dict containing all output quantities

        """

        # Get output, machine and OP
        output = self.parent.parent

        machine = output.simu.machine
        OP = output.elec.OP

        # Maximum voltage
        Urms_max = self.Urms_max
        # Maximum current
        Irms_max = self.Irms_max
        # Electrical frequency
        felec = OP.get_felec()
        # Electrical pulsation
        ws = 2 * np.pi * felec
        # Stator winding number of phases
        qs = machine.stator.winding.qs

        # Check if there is a loss model
        is_loss_model = LUT.simu.loss is not None

        # iteration until convergence is reached, and max number of iterations on EEC
        delta_Pem = 1e10
        delta_Pem_max = 0.1
        Nmax = 20
        niter_Pem = 1
        Id_min = self.Id_min
        Id_max = self.Id_max
        Iq_min = self.Iq_min
        Iq_max = self.Iq_max
        Nd = (
            self.n_Id
            if self.n_Id == 1
            else int(self.n_Id * self.n_interp / (self.n_Id + self.n_Iq))
        )
        Nq = (
            self.n_Iq
            if self.n_Iq == 1
            else int(self.n_Iq * self.n_interp / (self.n_Id + self.n_Iq))
        )
        while abs(delta_Pem) > delta_Pem_max and niter_Pem < Nmax:
            # Refine Id/Iq mesh
            Id_vect = np.linspace(Id_min, Id_max, Nd)
            Iq_vect = np.linspace(Iq_min, Iq_max, Nq)
            Id, Iq = np.meshgrid(Id_vect, Iq_vect)
            Id, Iq = Id.ravel(), Iq.ravel()

            # Calculate maximum current
            Imax_interp = np.sqrt(Id**2 + Iq**2)

            # Interpolate Phid/Phiq on the refined mesh
            (Phid, Phiq, Phih) = LUT.interp_Phi_dqh(Id, Iq)

            # Calculate voltage (Ud/Uq) for the refined mesh
            Ud = Rs * Id - Phiq * ws
            Uq = Rs * Iq + Phid * ws
            Umax_interp = np.sqrt(Ud**2 + Uq**2)

            if is_loss_model:
                # Interpolate losses from LUT:
                # - 1st column : Joule losses
                # - 2nd column : stator core losses
                # - 3rd column : magnet losses
                # - 4th column : rotor core losses
                # - 5th column : proximity losses
                Ploss_dqh = LUT.interp_Ploss_dqh(Id, Iq, N0=OP.N0)
                Ploss_ovl = np.sum(Ploss_dqh, axis=1)
            else:
                # Only consider stator Joule losses
                Ploss_ovl = qs * Rs * (Id**2 + Iq**2)

            if is_loss_model:
                # The input power must cover electrical power + additional losses
                P_in = qs * (Ud * Id + Uq * Iq) + np.sum(Ploss_dqh[:, 1:], axis=1)
            else:
                # The input power must cover electrical power + Joule losses
                P_in = qs * (Ud * Id + Uq * Iq)

            # The output power is the input power minus all losses
            P_out = P_in - Ploss_ovl

            # Set input/ouput power condition
            if OP.Pem_av_in is None:
                P_cond = P_out >= OP.Pem_av_ref
            else:
                P_cond = P_in >= OP.Pem_av_in

            # Set maximum voltage condition
            U_cond = Umax_interp <= Urms_max

            # Set maximum current condition
            I_cond = Imax_interp <= Irms_max

            # Finding indices of operating points satisfying voltage, current and power conditions
            i0 = np.logical_and.reduce((U_cond, I_cond, P_cond))

            if np.any(i0):
                # Finding index of operating point with lowest losses among feasible operating points
                imin = np.argmin(Ploss_ovl[i0])

                # Get error between calculated and requested powers
                if OP.Pem_av_in is None:
                    delta_Pem = P_out[i0][imin] - OP.Pem_av_ref
                else:
                    delta_Pem = P_in[i0][imin] - OP.Pem_av_in

                if abs(delta_Pem) > delta_Pem_max:
                    # Zoom in Id / Iq grid to achieve better accuracy on output values
                    jd = np.where(Id_vect == Id[i0][imin])[0][0]
                    jq = np.where(Iq_vect == Iq[i0][imin])[0][0]

                    jd_min = max([jd - 1, 0])
                    jd_max = min([jd + 1, Nd - 1])
                    jq_min = max([jq - 1, 0])
                    jq_max = min([jq + 1, Nq - 1])

                    Id_min = Id_vect[jd_min]
                    Id_max = Id_vect[jd_max]
                    Iq_min = Iq_vect[jq_min]
                    Iq_max = Iq_vect[jq_max]

                niter_Pem = niter_Pem + 1

            else:
                # Find strategy to get closest to requested power although violating voltage / current constraints
                i1 = np.logical_and(P_cond, U_cond)
                i2 = np.logical_and(P_cond, I_cond)

                if np.any(i1):
                    # Only consider requested power and voltage constraint
                    i0 = i1
                elif np.any(i2):
                    # Only consider requested power and current constraint
                    i0 = i2
                else:
                    # Only consider requested power
                    i0 = P_cond

                if np.any(i0):
                    # Find indices of operating points that reaches power
                    if OP.Pem_av_in is None:
                        P_min = np.min(P_out[i0])
                        P_cond = P_out == P_min
                    else:
                        P_min = np.min(P_in[i0])
                        P_cond = P_out == P_min

                    if np.where(P_cond)[0].size == 1:
                        # Take the only point that reaches requested power
                        imin = 0
                    else:
                        # Take the operating point that minimizes voltage
                        imin = np.argmin(Umax_interp[i0])

                    # Get error between calculated and requested powers
                    if OP.Pem_av_in is None:
                        delta_Pem = P_out[i0][imin] - OP.Pem_av_ref
                    else:
                        delta_Pem = P_in[i0][imin] - OP.Pem_av_in

                    if abs(delta_Pem) > delta_Pem_max:
                        # Zoom in Id / Iq grid to achieve better accuracy on output values
                        jd = np.where(Id_vect == Id[i0][imin])[0][0]
                        jq = np.where(Iq_vect == Iq[i0][imin])[0][0]

                        jd_min = max([jd - 1, 0])
                        jd_max = min([jd + 1, Nd - 1])
                        jq_min = max([jq - 1, 0])
                        jq_max = min([jq + 1, Nq - 1])

                        Id_min = Id_vect[jd_min]
                        Id_max = Id_vect[jd_max]
                        Iq_min = Iq_vect[jq_min]
                        Iq_max = Iq_vect[jq_max]

                    niter_Pem = niter_Pem + 1

                else:
                    # Find operating point that get closest to requested power
                    if OP.Pem_av_in is None:
                        P_max = np.max(P_out)
                        i0 = P_out == P_max
                    else:
                        P_max = np.max(P_in)
                        i0 = P_out == P_max

                    if np.where(i0)[0].size == 1:
                        # Take the closest point to requested power
                        imin = 0
                    else:
                        # Take the operating point that minimizes voltage
                        imin = np.argmin(Umax_interp[i0])

                    # Stop loop
                    delta_Pem = delta_Pem_max

        # Launch warnings
        if OP.Pem_av_in is None and P_out[i0][imin] < OP.Pem_av_ref:
            self.get_logger().warning(
                "Output power cannot be reached within current and voltage constraints, taking maximum feasible power"
            )

        elif OP.Pem_av_in is not None and P_in[i0][imin] < OP.Pem_av_in:
            self.get_logger().warning(
                "Input power cannot be reached within current and voltage constraints, taking maximum feasible power"
            )

        if Umax_interp[i0][imin] > Urms_max:
            self.get_logger().warning("Voltage constraint cannot be reached")

        if Imax_interp[i0][imin] > Irms_max:
            self.get_logger().warning("Current constraint cannot be reached")

        out_dict = dict()
        out_dict["P_in"] = P_in[i0][imin]
        out_dict["P_out"] = P_out[i0][imin]
        out_dict["efficiency"] = out_dict["P_out"] / out_dict["P_in"]
        if output.simu.input.is_generator:
            # Calculate torque from input power
            out_dict["Tem_av"] = out_dict["P_in"] / (2 * np.pi * OP.N0 / 60)
        else:
            # Calculate torque from output power
            out_dict["Tem_av"] = out_dict["P_out"] / (2 * np.pi * OP.N0 / 60)

        # Store voltage and currents
        out_dict["Id"] = Id[i0][imin]
        out_dict["Iq"] = Iq[i0][imin]
        out_dict["Ud"] = Ud[i0][imin]
        out_dict["Uq"] = Uq[i0][imin]

        # Store dq fluxes
        out_dict["Phid"] = Phid[i0][imin]
        out_dict["Phiq"] = Phiq[i0][imin]

        # Calculate flux linkage and back-emf
        Phidqh_mag = LUT.get_Phi_dqh_mag_mean()
        out_dict["Phid_mag"] = Phidqh_mag[0]
        out_dict["Phiq_mag"] = Phidqh_mag[1]
        out_dict["Erms"] = ws * Phidqh_mag[0]

        if is_loss_model:
            # Store losses
            out_dict["Pjoule"] = Ploss_dqh[i0, 0][imin]
            out_dict["Pstator"] = Ploss_dqh[i0, 1][imin]
            out_dict["Pmagnet"] = Ploss_dqh[i0, 2][imin]
            out_dict["Protor"] = Ploss_dqh[i0, 3][imin]
            out_dict["Pprox"] = Ploss_dqh[i0, 4][imin]
        else:
            out_dict["Pjoule"] = Ploss_ovl[i0][imin]

        # Calculate inductances
        if Id[i0][imin] != 0:
            out_dict["Ld"] = (Phid[i0][imin] - out_dict["Phid_mag"]) / Id[i0][imin]
        if Iq[i0][imin] != 0:
            out_dict["Lq"] = Phiq[i0][imin] / Iq[i0][imin]

        # Calculate torque ripple
        Tem_rip_pp = LUT.interp_Tem_rip_dqh(Id[i0][imin], Iq[i0][imin])
        if Tem_rip_pp is not None:
            out_dict["Tem_rip_pp"] = float(Tem_rip_pp)
            if out_dict["Tem_av"] == 0:
                out_dict["Tem_rip_norm"] = 0
            else:
                out_dict["Tem_rip_norm"] = np.abs(Tem_rip_pp / out_dict["Tem_av"])

        return out_dict

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        n_interp=10,
        Id_min=None,
        Id_max=None,
        Iq_min=None,
        Iq_max=None,
        n_Id=1,
        n_Iq=1,
        LUT_simu=None,
        is_grid_dq=True,
        Urms_max=None,
        Jrms_max=None,
        Irms_max=None,
        load_rate=1,
        eec=None,
        logger_name="Pyleecan.Electrical",
        freq_max=40000,
        LUT_enforced=None,
        Tsta=20,
        Trot=20,
        type_skin_effect=1,
        is_skin_effect_inductance=True,
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
            if "n_interp" in list(init_dict.keys()):
                n_interp = init_dict["n_interp"]
            if "Id_min" in list(init_dict.keys()):
                Id_min = init_dict["Id_min"]
            if "Id_max" in list(init_dict.keys()):
                Id_max = init_dict["Id_max"]
            if "Iq_min" in list(init_dict.keys()):
                Iq_min = init_dict["Iq_min"]
            if "Iq_max" in list(init_dict.keys()):
                Iq_max = init_dict["Iq_max"]
            if "n_Id" in list(init_dict.keys()):
                n_Id = init_dict["n_Id"]
            if "n_Iq" in list(init_dict.keys()):
                n_Iq = init_dict["n_Iq"]
            if "LUT_simu" in list(init_dict.keys()):
                LUT_simu = init_dict["LUT_simu"]
            if "is_grid_dq" in list(init_dict.keys()):
                is_grid_dq = init_dict["is_grid_dq"]
            if "Urms_max" in list(init_dict.keys()):
                Urms_max = init_dict["Urms_max"]
            if "Jrms_max" in list(init_dict.keys()):
                Jrms_max = init_dict["Jrms_max"]
            if "Irms_max" in list(init_dict.keys()):
                Irms_max = init_dict["Irms_max"]
            if "load_rate" in list(init_dict.keys()):
                load_rate = init_dict["load_rate"]
            if "eec" in list(init_dict.keys()):
                eec = init_dict["eec"]
            if "logger_name" in list(init_dict.keys()):
                logger_name = init_dict["logger_name"]
            if "freq_max" in list(init_dict.keys()):
                freq_max = init_dict["freq_max"]
            if "LUT_enforced" in list(init_dict.keys()):
                LUT_enforced = init_dict["LUT_enforced"]
            if "Tsta" in list(init_dict.keys()):
                Tsta = init_dict["Tsta"]
            if "Trot" in list(init_dict.keys()):
                Trot = init_dict["Trot"]
            if "type_skin_effect" in list(init_dict.keys()):
                type_skin_effect = init_dict["type_skin_effect"]
            if "is_skin_effect_inductance" in list(init_dict.keys()):
                is_skin_effect_inductance = init_dict["is_skin_effect_inductance"]
        # Set the properties (value check and convertion are done in setter)
        self.n_interp = n_interp
        self.Id_min = Id_min
        self.Id_max = Id_max
        self.Iq_min = Iq_min
        self.Iq_max = Iq_max
        self.n_Id = n_Id
        self.n_Iq = n_Iq
        self.LUT_simu = LUT_simu
        self.is_grid_dq = is_grid_dq
        self.Urms_max = Urms_max
        self.Jrms_max = Jrms_max
        self.Irms_max = Irms_max
        self.load_rate = load_rate
        # Call Electrical init
        super(ElecLUTdq, self).__init__(
            eec=eec,
            logger_name=logger_name,
            freq_max=freq_max,
            LUT_enforced=LUT_enforced,
            Tsta=Tsta,
            Trot=Trot,
            type_skin_effect=type_skin_effect,
            is_skin_effect_inductance=is_skin_effect_inductance,
        )
        # The class is frozen (in Electrical init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ElecLUTdq_str = ""
        # Get the properties inherited from Electrical
        ElecLUTdq_str += super(ElecLUTdq, self).__str__()
        ElecLUTdq_str += "n_interp = " + str(self.n_interp) + linesep
        ElecLUTdq_str += "Id_min = " + str(self.Id_min) + linesep
        ElecLUTdq_str += "Id_max = " + str(self.Id_max) + linesep
        ElecLUTdq_str += "Iq_min = " + str(self.Iq_min) + linesep
        ElecLUTdq_str += "Iq_max = " + str(self.Iq_max) + linesep
        ElecLUTdq_str += "n_Id = " + str(self.n_Id) + linesep
        ElecLUTdq_str += "n_Iq = " + str(self.n_Iq) + linesep
        if self.LUT_simu is not None:
            tmp = self.LUT_simu.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            ElecLUTdq_str += "LUT_simu = " + tmp
        else:
            ElecLUTdq_str += "LUT_simu = None" + linesep + linesep
        ElecLUTdq_str += "is_grid_dq = " + str(self.is_grid_dq) + linesep
        ElecLUTdq_str += "Urms_max = " + str(self.Urms_max) + linesep
        ElecLUTdq_str += "Jrms_max = " + str(self.Jrms_max) + linesep
        ElecLUTdq_str += "Irms_max = " + str(self.Irms_max) + linesep
        ElecLUTdq_str += "load_rate = " + str(self.load_rate) + linesep
        return ElecLUTdq_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Electrical
        if not super(ElecLUTdq, self).__eq__(other):
            return False
        if other.n_interp != self.n_interp:
            return False
        if other.Id_min != self.Id_min:
            return False
        if other.Id_max != self.Id_max:
            return False
        if other.Iq_min != self.Iq_min:
            return False
        if other.Iq_max != self.Iq_max:
            return False
        if other.n_Id != self.n_Id:
            return False
        if other.n_Iq != self.n_Iq:
            return False
        if other.LUT_simu != self.LUT_simu:
            return False
        if other.is_grid_dq != self.is_grid_dq:
            return False
        if other.Urms_max != self.Urms_max:
            return False
        if other.Jrms_max != self.Jrms_max:
            return False
        if other.Irms_max != self.Irms_max:
            return False
        if other.load_rate != self.load_rate:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Electrical
        diff_list.extend(
            super(ElecLUTdq, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._n_interp != self._n_interp:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._n_interp)
                    + ", other="
                    + str(other._n_interp)
                    + ")"
                )
                diff_list.append(name + ".n_interp" + val_str)
            else:
                diff_list.append(name + ".n_interp")
        if (
            other._Id_min is not None
            and self._Id_min is not None
            and np.isnan(other._Id_min)
            and np.isnan(self._Id_min)
        ):
            pass
        elif other._Id_min != self._Id_min:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Id_min)
                    + ", other="
                    + str(other._Id_min)
                    + ")"
                )
                diff_list.append(name + ".Id_min" + val_str)
            else:
                diff_list.append(name + ".Id_min")
        if (
            other._Id_max is not None
            and self._Id_max is not None
            and np.isnan(other._Id_max)
            and np.isnan(self._Id_max)
        ):
            pass
        elif other._Id_max != self._Id_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Id_max)
                    + ", other="
                    + str(other._Id_max)
                    + ")"
                )
                diff_list.append(name + ".Id_max" + val_str)
            else:
                diff_list.append(name + ".Id_max")
        if (
            other._Iq_min is not None
            and self._Iq_min is not None
            and np.isnan(other._Iq_min)
            and np.isnan(self._Iq_min)
        ):
            pass
        elif other._Iq_min != self._Iq_min:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Iq_min)
                    + ", other="
                    + str(other._Iq_min)
                    + ")"
                )
                diff_list.append(name + ".Iq_min" + val_str)
            else:
                diff_list.append(name + ".Iq_min")
        if (
            other._Iq_max is not None
            and self._Iq_max is not None
            and np.isnan(other._Iq_max)
            and np.isnan(self._Iq_max)
        ):
            pass
        elif other._Iq_max != self._Iq_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Iq_max)
                    + ", other="
                    + str(other._Iq_max)
                    + ")"
                )
                diff_list.append(name + ".Iq_max" + val_str)
            else:
                diff_list.append(name + ".Iq_max")
        if other._n_Id != self._n_Id:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._n_Id) + ", other=" + str(other._n_Id) + ")"
                )
                diff_list.append(name + ".n_Id" + val_str)
            else:
                diff_list.append(name + ".n_Id")
        if other._n_Iq != self._n_Iq:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._n_Iq) + ", other=" + str(other._n_Iq) + ")"
                )
                diff_list.append(name + ".n_Iq" + val_str)
            else:
                diff_list.append(name + ".n_Iq")
        if (other.LUT_simu is None and self.LUT_simu is not None) or (
            other.LUT_simu is not None and self.LUT_simu is None
        ):
            diff_list.append(name + ".LUT_simu None mismatch")
        elif self.LUT_simu is not None:
            diff_list.extend(
                self.LUT_simu.compare(
                    other.LUT_simu,
                    name=name + ".LUT_simu",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if other._is_grid_dq != self._is_grid_dq:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_grid_dq)
                    + ", other="
                    + str(other._is_grid_dq)
                    + ")"
                )
                diff_list.append(name + ".is_grid_dq" + val_str)
            else:
                diff_list.append(name + ".is_grid_dq")
        if (
            other._Urms_max is not None
            and self._Urms_max is not None
            and np.isnan(other._Urms_max)
            and np.isnan(self._Urms_max)
        ):
            pass
        elif other._Urms_max != self._Urms_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Urms_max)
                    + ", other="
                    + str(other._Urms_max)
                    + ")"
                )
                diff_list.append(name + ".Urms_max" + val_str)
            else:
                diff_list.append(name + ".Urms_max")
        if (
            other._Jrms_max is not None
            and self._Jrms_max is not None
            and np.isnan(other._Jrms_max)
            and np.isnan(self._Jrms_max)
        ):
            pass
        elif other._Jrms_max != self._Jrms_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Jrms_max)
                    + ", other="
                    + str(other._Jrms_max)
                    + ")"
                )
                diff_list.append(name + ".Jrms_max" + val_str)
            else:
                diff_list.append(name + ".Jrms_max")
        if (
            other._Irms_max is not None
            and self._Irms_max is not None
            and np.isnan(other._Irms_max)
            and np.isnan(self._Irms_max)
        ):
            pass
        elif other._Irms_max != self._Irms_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._Irms_max)
                    + ", other="
                    + str(other._Irms_max)
                    + ")"
                )
                diff_list.append(name + ".Irms_max" + val_str)
            else:
                diff_list.append(name + ".Irms_max")
        if (
            other._load_rate is not None
            and self._load_rate is not None
            and np.isnan(other._load_rate)
            and np.isnan(self._load_rate)
        ):
            pass
        elif other._load_rate != self._load_rate:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._load_rate)
                    + ", other="
                    + str(other._load_rate)
                    + ")"
                )
                diff_list.append(name + ".load_rate" + val_str)
            else:
                diff_list.append(name + ".load_rate")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Electrical
        S += super(ElecLUTdq, self).__sizeof__()
        S += getsizeof(self.n_interp)
        S += getsizeof(self.Id_min)
        S += getsizeof(self.Id_max)
        S += getsizeof(self.Iq_min)
        S += getsizeof(self.Iq_max)
        S += getsizeof(self.n_Id)
        S += getsizeof(self.n_Iq)
        S += getsizeof(self.LUT_simu)
        S += getsizeof(self.is_grid_dq)
        S += getsizeof(self.Urms_max)
        S += getsizeof(self.Jrms_max)
        S += getsizeof(self.Irms_max)
        S += getsizeof(self.load_rate)
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

        # Get the properties inherited from Electrical
        ElecLUTdq_dict = super(ElecLUTdq, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        ElecLUTdq_dict["n_interp"] = self.n_interp
        ElecLUTdq_dict["Id_min"] = self.Id_min
        ElecLUTdq_dict["Id_max"] = self.Id_max
        ElecLUTdq_dict["Iq_min"] = self.Iq_min
        ElecLUTdq_dict["Iq_max"] = self.Iq_max
        ElecLUTdq_dict["n_Id"] = self.n_Id
        ElecLUTdq_dict["n_Iq"] = self.n_Iq
        if self.LUT_simu is None:
            ElecLUTdq_dict["LUT_simu"] = None
        else:
            ElecLUTdq_dict["LUT_simu"] = self.LUT_simu.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        ElecLUTdq_dict["is_grid_dq"] = self.is_grid_dq
        ElecLUTdq_dict["Urms_max"] = self.Urms_max
        ElecLUTdq_dict["Jrms_max"] = self.Jrms_max
        ElecLUTdq_dict["Irms_max"] = self.Irms_max
        ElecLUTdq_dict["load_rate"] = self.load_rate
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        ElecLUTdq_dict["__class__"] = "ElecLUTdq"
        return ElecLUTdq_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        n_interp_val = self.n_interp
        Id_min_val = self.Id_min
        Id_max_val = self.Id_max
        Iq_min_val = self.Iq_min
        Iq_max_val = self.Iq_max
        n_Id_val = self.n_Id
        n_Iq_val = self.n_Iq
        if self.LUT_simu is None:
            LUT_simu_val = None
        else:
            LUT_simu_val = self.LUT_simu.copy()
        is_grid_dq_val = self.is_grid_dq
        Urms_max_val = self.Urms_max
        Jrms_max_val = self.Jrms_max
        Irms_max_val = self.Irms_max
        load_rate_val = self.load_rate
        if self.eec is None:
            eec_val = None
        else:
            eec_val = self.eec.copy()
        logger_name_val = self.logger_name
        freq_max_val = self.freq_max
        if self.LUT_enforced is None:
            LUT_enforced_val = None
        else:
            LUT_enforced_val = self.LUT_enforced.copy()
        Tsta_val = self.Tsta
        Trot_val = self.Trot
        type_skin_effect_val = self.type_skin_effect
        is_skin_effect_inductance_val = self.is_skin_effect_inductance
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            n_interp=n_interp_val,
            Id_min=Id_min_val,
            Id_max=Id_max_val,
            Iq_min=Iq_min_val,
            Iq_max=Iq_max_val,
            n_Id=n_Id_val,
            n_Iq=n_Iq_val,
            LUT_simu=LUT_simu_val,
            is_grid_dq=is_grid_dq_val,
            Urms_max=Urms_max_val,
            Jrms_max=Jrms_max_val,
            Irms_max=Irms_max_val,
            load_rate=load_rate_val,
            eec=eec_val,
            logger_name=logger_name_val,
            freq_max=freq_max_val,
            LUT_enforced=LUT_enforced_val,
            Tsta=Tsta_val,
            Trot=Trot_val,
            type_skin_effect=type_skin_effect_val,
            is_skin_effect_inductance=is_skin_effect_inductance_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.n_interp = None
        self.Id_min = None
        self.Id_max = None
        self.Iq_min = None
        self.Iq_max = None
        self.n_Id = None
        self.n_Iq = None
        if self.LUT_simu is not None:
            self.LUT_simu._set_None()
        self.is_grid_dq = None
        self.Urms_max = None
        self.Jrms_max = None
        self.Irms_max = None
        self.load_rate = None
        # Set to None the properties inherited from Electrical
        super(ElecLUTdq, self)._set_None()

    def _get_n_interp(self):
        """getter of n_interp"""
        return self._n_interp

    def _set_n_interp(self, value):
        """setter of n_interp"""
        check_var("n_interp", value, "int", Vmin=1)
        self._n_interp = value

    n_interp = property(
        fget=_get_n_interp,
        fset=_set_n_interp,
        doc="""Number of id values used for interpolation

        :Type: int
        :min: 1
        """,
    )

    def _get_Id_min(self):
        """getter of Id_min"""
        return self._Id_min

    def _set_Id_min(self, value):
        """setter of Id_min"""
        check_var("Id_min", value, "float")
        self._Id_min = value

    Id_min = property(
        fget=_get_Id_min,
        fset=_set_Id_min,
        doc="""Minimum Id for LUT calculation

        :Type: float
        """,
    )

    def _get_Id_max(self):
        """getter of Id_max"""
        return self._Id_max

    def _set_Id_max(self, value):
        """setter of Id_max"""
        check_var("Id_max", value, "float")
        self._Id_max = value

    Id_max = property(
        fget=_get_Id_max,
        fset=_set_Id_max,
        doc="""Maximum Id for LUT calculation

        :Type: float
        """,
    )

    def _get_Iq_min(self):
        """getter of Iq_min"""
        return self._Iq_min

    def _set_Iq_min(self, value):
        """setter of Iq_min"""
        check_var("Iq_min", value, "float")
        self._Iq_min = value

    Iq_min = property(
        fget=_get_Iq_min,
        fset=_set_Iq_min,
        doc="""Minimum Iq for LUT calculation

        :Type: float
        """,
    )

    def _get_Iq_max(self):
        """getter of Iq_max"""
        return self._Iq_max

    def _set_Iq_max(self, value):
        """setter of Iq_max"""
        check_var("Iq_max", value, "float")
        self._Iq_max = value

    Iq_max = property(
        fget=_get_Iq_max,
        fset=_set_Iq_max,
        doc="""Maximum Iq for LUT calculation

        :Type: float
        """,
    )

    def _get_n_Id(self):
        """getter of n_Id"""
        return self._n_Id

    def _set_n_Id(self, value):
        """setter of n_Id"""
        check_var("n_Id", value, "int")
        self._n_Id = value

    n_Id = property(
        fget=_get_n_Id,
        fset=_set_n_Id,
        doc="""Number of Id for LUT calculation

        :Type: int
        """,
    )

    def _get_n_Iq(self):
        """getter of n_Iq"""
        return self._n_Iq

    def _set_n_Iq(self, value):
        """setter of n_Iq"""
        check_var("n_Iq", value, "int")
        self._n_Iq = value

    n_Iq = property(
        fget=_get_n_Iq,
        fset=_set_n_Iq,
        doc="""Number of Iq for LUT calculation

        :Type: int
        """,
    )

    def _get_LUT_simu(self):
        """getter of LUT_simu"""
        return self._LUT_simu

    def _set_LUT_simu(self, value):
        """setter of LUT_simu"""
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
                "pyleecan.Classes", value.get("__class__"), "LUT_simu"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Simulation = import_class("pyleecan.Classes", "Simulation", "LUT_simu")
            value = Simulation()
        check_var("LUT_simu", value, "Simulation")
        self._LUT_simu = value

        if self._LUT_simu is not None:
            self._LUT_simu.parent = self

    LUT_simu = property(
        fget=_get_LUT_simu,
        fset=_set_LUT_simu,
        doc="""Simulation object to run for LUT calculation

        :Type: Simulation
        """,
    )

    def _get_is_grid_dq(self):
        """getter of is_grid_dq"""
        return self._is_grid_dq

    def _set_is_grid_dq(self, value):
        """setter of is_grid_dq"""
        check_var("is_grid_dq", value, "bool")
        self._is_grid_dq = value

    is_grid_dq = property(
        fget=_get_is_grid_dq,
        fset=_set_is_grid_dq,
        doc="""True to build a n_Id*n_Iq grid, otherwise calculate n_Id+n_Iq simulations and extrapolate to the dq plane

        :Type: bool
        """,
    )

    def _get_Urms_max(self):
        """getter of Urms_max"""
        return self._Urms_max

    def _set_Urms_max(self, value):
        """setter of Urms_max"""
        check_var("Urms_max", value, "float", Vmin=0)
        self._Urms_max = value

    Urms_max = property(
        fget=_get_Urms_max,
        fset=_set_Urms_max,
        doc="""Maximum rms phase voltage

        :Type: float
        :min: 0
        """,
    )

    def _get_Jrms_max(self):
        """getter of Jrms_max"""
        return self._Jrms_max

    def _set_Jrms_max(self, value):
        """setter of Jrms_max"""
        check_var("Jrms_max", value, "float", Vmin=0)
        self._Jrms_max = value

    Jrms_max = property(
        fget=_get_Jrms_max,
        fset=_set_Jrms_max,
        doc="""Maximum rms current density in slot

        :Type: float
        :min: 0
        """,
    )

    def _get_Irms_max(self):
        """getter of Irms_max"""
        return self._Irms_max

    def _set_Irms_max(self, value):
        """setter of Irms_max"""
        check_var("Irms_max", value, "float", Vmin=0)
        self._Irms_max = value

    Irms_max = property(
        fget=_get_Irms_max,
        fset=_set_Irms_max,
        doc="""Maximum rms phase current

        :Type: float
        :min: 0
        """,
    )

    def _get_load_rate(self):
        """getter of load_rate"""
        return self._load_rate

    def _set_load_rate(self, value):
        """setter of load_rate"""
        check_var("load_rate", value, "float", Vmin=0, Vmax=1)
        self._load_rate = value

    load_rate = property(
        fget=_get_load_rate,
        fset=_set_load_rate,
        doc="""Load rate between 0 (no-load) and 1 (full-load) for MTPA calculation

        :Type: float
        :min: 0
        :max: 1
        """,
    )
