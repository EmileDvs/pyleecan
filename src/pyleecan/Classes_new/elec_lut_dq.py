# Experimental dataclass generated from Generator/ClassesRef/Simulation/ElecLUTdq.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ._error import InputError
from .eec_pmsm import EEC_PMSM
from .electrical import Electrical
from .lut_dq import LUTdq
from .out_loss import OutLoss
from .simulation import Simulation


@dataclass(eq=False)
class ElecLUTdq(Electrical):
    """Electric module object for electrical equivalent circuit simulation

    Attributes
    ----------
    n_interp : int
        Number of id values used for interpolation
        Default: 10; Minimum: 1
    Id_min : float or None
        Minimum Id for LUT calculation
        Unit: Arms; Default: None
    Id_max : float or None
        Maximum Id for LUT calculation
        Unit: Arms; Default: None
    Iq_min : float or None
        Minimum Iq for LUT calculation
        Unit: Arms; Default: None
    Iq_max : float or None
        Maximum Iq for LUT calculation
        Unit: Arms; Default: None
    n_Id : int
        Number of Id for LUT calculation
        Default: 1
    n_Iq : int
        Number of Iq for LUT calculation
        Default: 1
    LUT_simu : Simulation or None
        Simulation object to run for LUT calculation
        Default: None
    is_grid_dq : bool
        True to build a n_Id*n_Iq grid, otherwise calculate n_Id+n_Iq simulations and extrapolate to the dq plane
        Default: True
    Urms_max : float or None
        Maximum rms phase voltage
        Unit: Vrms; Default: None; Minimum: 0
    Jrms_max : float or None
        Maximum rms current density in slot
        Unit: A/m2; Default: None; Minimum: 0
    Irms_max : float or None
        Maximum rms phase current
        Unit: A; Default: None; Minimum: 0
    load_rate : float
        Load rate between 0 (no-load) and 1 (full-load) for MTPA calculation
        Default: 1; Minimum: 0; Maximum: 1
    """

    n_interp: int = 10
    """Number of id values used for interpolation"""
    Id_min: float | None = None
    """Minimum Id for LUT calculation"""
    Id_max: float | None = None
    """Maximum Id for LUT calculation"""
    Iq_min: float | None = None
    """Minimum Iq for LUT calculation"""
    Iq_max: float | None = None
    """Maximum Iq for LUT calculation"""
    n_Id: int = 1
    """Number of Id for LUT calculation"""
    n_Iq: int = 1
    """Number of Iq for LUT calculation"""
    LUT_simu: Simulation | None = None
    """Simulation object to run for LUT calculation"""
    is_grid_dq: bool = True
    """True to build a n_Id*n_Iq grid, otherwise calculate n_Id+n_Iq simulations and extrapolate to the dq plane"""
    Urms_max: float | None = None
    """Maximum rms phase voltage"""
    Jrms_max: float | None = None
    """Maximum rms current density in slot"""
    Irms_max: float | None = None
    """Maximum rms phase current"""
    load_rate: float = 1
    """Load rate between 0 (no-load) and 1 (full-load) for MTPA calculation"""

    # Inlined from Methods.Simulation.ElecLUTdq.comp_LUTdq
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

    # Inlined from Methods.Simulation.ElecLUTdq.run
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

    # Inlined from Methods.Simulation.ElecLUTdq.solve_MTPA
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

        out_dict = {}

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

    # Inlined from Methods.Simulation.ElecLUTdq.solve_power
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

        out_dict = {}
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
