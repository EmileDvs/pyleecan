# Experimental dataclass generated from Generator/ClassesRef/Simulation/EEC_SCIM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from multiprocessing import cpu_count

import numpy as np
import scipy.interpolate as scp_int

from ..Functions.Electrical.dqh_transformation import abc2n, n2abc
from ..Functions.labels import ROTOR_LAB, STATOR_LAB
from ..Functions.Load.import_class import import_class
from .eec import EEC
from .import_gen_vect_lin import ImportGenVectLin
from .import_matrix_val import ImportMatrixVal


@dataclass(eq=False)
class EEC_SCIM(EEC):
    """Electric module: Electrical Equivalent Circuit for Squirrel Cage Induction Machine

    Attributes
    ----------
    Rfe : float or None
        Iron loss resistance
        Unit: Ohm; Default: None
    L1 : float or None
        Stator phase inductance
        Unit: H; Default: None
    R2 : float or None
        Rotor phase resistance
        Unit: Ohm; Default: None
    L2 : float or None
        Rotor phase inductance
        Unit: H; Default: None
    K21Z : float or None
        transformation ratio from secondary (2, rotor) to primary (1, stator) for impedance
        Default: None
    K21I : float or None
        transformation ratio from secondary (2, rotor) to primary (1, stator) for current
        Default: None
    Im_table : ndarray or None
        Array of magnetizing current
        Unit: Arms; Default: None
    Lm_table : ndarray or None
        Array of magnetizing inductance function of Im_table
        Unit: H; Default: None
    I1 : complex or None
        Stator phase current (after solve)
        Unit: Arms; Default: None
    I2 : complex or None
        Rotor phase current (after solve)
        Unit: Arms; Default: None
    U1 : complex or None
        Stator phase voltage (after solve)
        Unit: Vrms; Default: None
    U2 : complex or None
        Rotor phase voltage (after solve)
        Unit: Vrms; Default: None
    If : complex or None
        Iron loss current (after solve)
        Unit: Arms; Default: None
    Lm : float or None
        Magnetizing inductance (after solve)
        Unit: H; Default: None
    Im : complex or None
        Magnetizing current (after solve)
        Unit: Arms; Default: None
    """

    Rfe: float | None = None
    """Iron loss resistance"""
    L1: float | None = None
    """Stator phase inductance"""
    R2: float | None = None
    """Rotor phase resistance"""
    L2: float | None = None
    """Rotor phase inductance"""
    K21Z: float | None = None
    """transformation ratio from secondary (2, rotor) to primary (1, stator) for impedance"""
    K21I: float | None = None
    """transformation ratio from secondary (2, rotor) to primary (1, stator) for current"""
    Im_table: np.ndarray | None = None
    """Array of magnetizing current"""
    Lm_table: np.ndarray | None = None
    """Array of magnetizing inductance function of Im_table"""
    I1: complex | None = None
    """Stator phase current (after solve)"""
    I2: complex | None = None
    """Rotor phase current (after solve)"""
    U1: complex | None = None
    """Stator phase voltage (after solve)"""
    U2: complex | None = None
    """Rotor phase voltage (after solve)"""
    If: complex | None = None
    """Iron loss current (after solve)"""
    Lm: float | None = None
    """Magnetizing inductance (after solve)"""
    Im: complex | None = None
    """Magnetizing current (after solve)"""

    # Inlined from Methods.Simulation.EEC_SCIM._comp_flux_mean
    def _comp_flux_mean(self, out):
        """Calculate magnetizing flux (not used)

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        out: Output
            An Output object

        Returns
        ------
        Phi_s : float
            Stator flux linkage [Wb]
        Phi_r : float
            Rotor flux linkage [Wb]
        """

        # TODO add fix for single time value
        # TODO add option to calculate RMS instead of mean fluxlinkage

        # some readability
        logger = self.get_logger()
        machine = out.simu.machine
        p = machine.rotor.winding.p
        qsr = machine.rotor.winding.qs
        sym, is_anti_per = machine.comp_periodicity_spatial()

        # get the fluxlinkages
        Phi = out.mag.Phi_wind[ROTOR_LAB + "-0"].get_along("time", "phase")[
            "Phi_{wind}"
        ]

        # reconstruct fluxlinkage in case of (anti) periodicity
        if out.simu.mag.is_periodicity_a:
            # reconstruct anti periodicity
            if is_anti_per:
                qsr_eff = qsr // (sym * (1 + is_anti_per))
                for ii in range(qsr_eff):
                    if not all(np.isnan(Phi[:, ii + qsr_eff]).tolist()):
                        logger.warning(
                            f"{type(self).__name__}: "
                            + f"Rotor fluxlinkage of bar {ii + qsr_eff} will be overridden."
                        )
                    Phi[:, ii + qsr_eff] = -Phi[:, ii]
            # reconstruct periodicity
            if sym != 1:
                qsr_eff = qsr // sym
                if not all(np.isnan(Phi[:, qsr_eff:]).tolist()):
                    logger.warning(
                        f"{type(self).__name__}: "
                        + f"Rotor fluxlinkage of bar "
                        + "starting with {qsr_eff} will be overridden."
                    )
                for ii in range(sym - 1):
                    id0 = qsr_eff * (ii + 1)
                    id1 = qsr_eff * (ii + 2)
                    Phi[:, id0:id1] = Phi[:, :qsr_eff]

            # rescale
            Phi = Phi / (sym * (1 + is_anti_per))

        # compute mean value of periodic bar flux linkage
        Phi_ab = np.zeros([Phi.shape[0], 2])
        if (qsr % p) == 0:
            qsr_per_pole = qsr // p
            for ii in range(p):
                id0 = qsr_per_pole * ii
                id1 = qsr_per_pole * (ii + 1)
                Phi_ab += n2abc(Phi[:, id0:id1], n=qsr_per_pole) / p
        else:
            logger.warning(f"{type(self).__name__}: " + "Not Implemented Yet")

        # compute rotor and stator flux linkage
        Phi_r = abs(Phi_ab[:, 0] + 1j * Phi_ab[:, 1]).mean() / np.sqrt(2)
        Phi_ab = n2abc(
            out.mag.Phi_wind[STATOR_LAB + "-0"].get_along("time", "phase")["Phi_{wind}"]
        )
        Phi_s = abs(Phi_ab[:, 0] + 1j * Phi_ab[:, 1]).mean() / np.sqrt(2)

        return Phi_s, Phi_r

    # Inlined from Methods.Simulation.EEC_SCIM._comp_Lm_FEA
    def _comp_Lm_FEA(self, machine, K21Z, Xke_skinS):
        """Calculate magnetizing flux (not used)

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        machine: Machine
            A Machine object
        K21Z: float
            Stator to rotor impedance ratio
        Xke_skinS: float
            Skin effect on stator inductance

        Returns
        ------
        Phi_s : float
            Stator magnetizing flux [Wb]
        I_m : float
            Stator magnetizing current [A]
        """

        Simu1 = import_class("pyleecan.Classes", "Simu1")
        InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
        MagFEMM = import_class("pyleecan.Classes", "MagFEMM")

        p = machine.get_pole_pair_number()

        qsr = machine.rotor.winding.Zs

        par = self.parameters

        # setup a MagFEMM simulation to get the parameters
        # TODO maybe use IndMagFEMM or FluxlinkageFEMM
        #      but for now they are not suitable so I utilize 'normal' MagFEMM simu

        # set frequency, time and number of revolutions
        # TODO what will be the best settings to get a good average with min. samples
        if self.N0 is None and self.felec is None:
            N0 = 50 * 60 / p
            felec = 50
        elif self.N0 is None and self.felec is not None:
            N0 = self.felec * 60 / p
        elif self.N0 is not None and self.felec is None:
            N0 = self.N0
            felec = N0 / 60 * p
        else:
            N0 = self.N0
            felec = self.felec

        Nrev = self.Nrev

        T = Nrev / (N0 / 60)
        Ir = ImportMatrixVal(value=np.zeros((self.Nt_tot, qsr)))
        time = ImportGenVectLin(start=0, stop=T, num=self.Nt_tot, endpoint=False)

        # TODO estimate magnetizing current if self.I == None
        # TODO compute magnetizing curve as function of I

        # setup the simu object
        simu = Simu1(name="EEC_comp_parameter", machine=machine.copy())
        # Definition of the enforced output of the electrical module
        simu.input = InputCurrent(
            Is=None,
            Id_ref=self.I,
            Iq_ref=0,
            Ir=Ir,  # zero current for the rotor
            N0=N0,
            time=time,
            felec=felec,
        )

        # Definition of the magnetic simulation (no symmetry)
        nb_worker = self.nb_worker if self.nb_worker else cpu_count()

        simu.mag = MagFEMM(
            type_BH_stator=0,
            type_BH_rotor=0,
            is_periodicity_a=self.is_periodicity_a,
            is_periodicity_t=False,
            Kgeo_fineness=0.5,
            Kmesh_fineness=0.5,
            nb_worker=nb_worker,
        )
        simu.force = None
        simu.struct = None

        # --- compute the main inductance and stator stray inductance ---
        # set output and run first simulation
        out = simu.run()

        # compute average rotor and stator fluxlinkage
        # TODO check wind_mat that the i-th bars is in the i-th slots
        Phi_s, Phi_r = self._comp_flux_mean(out)

        par["Lm"] = (Phi_r * K21Z * qsr / 3) / self.I
        L1 = (Phi_s - (Phi_r * K21Z * qsr / 3)) / self.I
        par["L1"] = L1 * Xke_skinS

        # set current values
        Ir_ = np.zeros([self.Nt_tot, 2])
        Ir_[:, 0] = self.I * K21Z * np.sqrt(2)
        Ir = abc2n(Ir_, n=qsr // p)  # TODO no rotation for now

        Ir = ImportMatrixVal(value=np.tile(Ir, (1, p)))

        simu.input.Is = None
        simu.input.Id_ref = 0
        simu.input.Iq_ref = 0
        simu.input.Ir = Ir

        out2 = simu.run()

        # compute average rotor and stator fluxlinkage
        # TODO check wind_mat that the i-th bars is in the i-th slots
        Phi_s, Phi_r = self._comp_flux_mean(out2)
        K21Z = par["K21Z"]
        I_m = self.I
        Lm = Phi_s / I_m
        L2 = ((Phi_r * K21Z * qsr / 3) - Phi_s) / self.I

        return Phi_s, I_m

    # Inlined from Methods.Simulation.EEC_SCIM.clear_parameters
    def clear_parameters(self):
        """Clear all the parameters of an EEC_SCIM

        Parameters
        ----------
        self : EEC_SCIM
            An EEC_SCIM object
        """

        self.R1 = None
        self.R2 = None
        self.L1 = None
        self.L2 = None
        self.K21Z = None
        self.K21I = None
        self.Lm_table = None
        self.Im_table = None
        self.Xkr_skinS, self.Xke_skinS = 1, 1
        self.Xkr_skinR, self.Xke_skinR = 1, 1

    # Inlined from Methods.Simulation.EEC_SCIM.comp_joule_losses
    def comp_joule_losses(self, out_dict, machine):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in comp_parameters of EEC
        machine : Machine
            a Machine object

        Returns
        ------
        out_dict : dict
            Dict containing all magnetic quantities that have been calculated in EEC
        """

        # TODO utilize loss models instead here
        # compute stator joule losses
        qs = machine.stator.winding.qs

        P_joule_s = qs * self.R1 * abs(self.I1) ** 2
        P_joule_r = qs * self.R2 * abs(self.I2) ** 2

        out_dict["Pj_losses"] = P_joule_s + P_joule_r

        return out_dict

    # Inlined from Methods.Simulation.EEC_SCIM.comp_K21
    def comp_K21(self):
        """Compute and set winding transformation ratios

        Parameters
        ----------
        self : EEC_SCIM
            An EEC_SCIM objects
        """

        machine = self.get_machine_from_parent()
        Zr = machine.rotor.slot.Zs
        qs = machine.stator.winding.qs
        # change from rotor frame to stator frame
        xi = machine.stator.winding.comp_winding_factor()
        Ntspc = machine.stator.winding.comp_Ntsp()

        # winding transformation ratios
        K21 = (xi[0] * Ntspc) / (
            1 * 0.5
        )  # (xi1[0] * Ntspc1) / (xi2[0] * Ntspc2)  for DFIM
        # transformation ratio from secondary (2, rotor) to primary (1, stator) for impedance in SCIM case
        self.K21Z = (qs / Zr) * K21**2
        # transformation ratio from secondary (2, rotor) to primary (1, stator) for current  in SCIM case
        self.K21I = (qs / Zr) * K21

    # Inlined from Methods.Simulation.EEC_SCIM.comp_L1
    def comp_L1(self, L1_ref=None):
        """Compute and set the Stator phase inductance for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        L1_ref : float
            reference inductance

        """

        if L1_ref is None:
            raise Exception("L1 parameter for EEC_SCIM must be enforced !")
            if self.type_comp_Lr == 1:
                # analytic calculation
                # L10 = machine.stator.slot.comp_inductance_leakage_ANL() #TODO
                pass
            else:
                # FEA calculation
                # L1 = machine.rotor.slot.comp_inductance_leakage_FEA() #TODO
                pass

        self.L1 = L1_ref * self.Xke_skinS

    # Inlined from Methods.Simulation.EEC_SCIM.comp_L2
    def comp_L2(self, L2_ref=None):
        """Compute and set the Rotor phase inductance for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        L2_ref : float
            reference inductance

        """

        if L2_ref is None:
            raise Exception("L2 parameter for EEC_SCIM must be enforced !")
            if self.type_comp_Lr == 1:
                # analytic calculation
                # L2 = machine.rotor.slot.comp_inductance_leakage_ANL() #TODO
                pass
            else:
                # FEA calculation
                # L2 = machine.rotor.slot.comp_inductance_leakage_FEA() #TODO
                pass

        self.L2 = L2_ref * self.Xke_skinR

    # Inlined from Methods.Simulation.EEC_SCIM.comp_parameters
    def comp_parameters(self):
        """Compute and set the parameter attributes of the equivalent electrical circuit:
        resistance, skin effect factors and inductance according to OP/T

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        machine : Machine
            a Machine object
        OP : OP
            an OP object
        Tsta : float
            Average stator temperature
        Trot : float
            Average rotor temperature
        """

        # Check that OP and temperature are set
        assert self.OP is not None
        assert self.Tsta is not None
        assert self.Trot is not None

        if self.type_skin_effect:
            # Update skin effect
            self.comp_skin_effect()

        # Compute winding transformation ratios
        if self.K21I is None:
            self.comp_K21()

        # Compute stator winding resistance
        if self.R1 is None:
            self.comp_R1()

        # Compute stator winding inductance
        if self.L1 is None:
            self.comp_L1()

        # Iron loss resistance
        if self.Rfe is None:
            self.Rfe = 1e12  # TODO calculate (or estimate at least)

        # Compute rotor winding resistance
        if self.R2 is None:
            self.comp_R2()

        # Compute rotor winding inductance
        if self.L2 is None:
            self.comp_L2()

        # check if inductances have to be calculated
        if self.Lm_table is None or self.Im_table is None:
            raise Exception("Lm_table and Im_table must be enforced for EEC_SCIM")

    # Inlined from Methods.Simulation.EEC_SCIM.comp_R2
    def comp_R2(self, R2_ref=None, T_ref=None):
        """Compute and set the rotor phase resistance for the equivalent electrical circuit

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        R2_ref : float
            reference resistance
        T_ref : float
            reference temperature

        """

        if R2_ref is None:
            # Compute at correct temperature
            machine = self.get_machine_from_parent()
            R2_ref = machine.rotor.comp_resistance_wind(T=self.Trot)
            # putting resistance on stator side in EEC
            if self.K21Z is None:
                self.comp_K21()
            R2_ref = R2_ref * self.K21Z
        elif T_ref is None:
            # Assume that the reference match EEC temperature (should not happend)
            pass
        else:  # Adpat the temperature
            # Get rotor conductor
            machine = self.get_machine_from_parent()
            CondR = machine.rotor.winding.conductor

            # Compute temperature effect on stator side
            Tfact2 = CondR.comp_temperature_effect(T_op=self.Trot, T_ref=T_ref)
            R2_ref = R2_ref * Tfact2
        # Stator resistance
        self.R2 = R2_ref * self.Xkr_skinR

    # Inlined from Methods.Simulation.EEC_SCIM.comp_skin_effect
    def comp_skin_effect(self):
        """Compute and set the skin effect factors (update value in object)

        Parameters
        ----------
        self : EEC_SCIM
            An EEC_SCIM objects
        """

        assert self.OP is not None
        assert self.Tsta is not None
        assert self.Trot is not None
        machine = self.get_machine_from_parent()
        CondS = machine.stator.winding.conductor
        CondR = machine.rotor.winding.conductor
        felec = self.OP.get_felec()
        slip = self.OP.get_slip()

        # compute skin_effect on stator side
        self.Xkr_skinS = CondS.comp_skin_effect_resistance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

        self.Xke_skinS = CondS.comp_skin_effect_inductance(
            freq=felec, T_op=self.Tsta, T_ref=20
        )

        # compute skin_effect on rotor side
        if felec * slip != 0:
            self.Xkr_skinR = CondR.comp_skin_effect_resistance(
                freq=felec * slip, T_op=self.Trot, T_ref=20
            )

            self.Xke_skinR = CondR.comp_skin_effect_inductance(
                freq=felec * slip, T_op=self.Trot, T_ref=20
            )
        else:
            self.Xkr_skinR, self.Xke_skinR = 1, 1

    # Inlined from Methods.Simulation.EEC_SCIM.solve
    def solve(self):
        """Solve the equivalent electrical circuit of SCIM

                      --->                     ---->
         -----Rs------XsIs---- --- -----Rr'----XrIr----
        |                     |   |                       |
        |                     Rfe Xm                      Rr*(s-1)/s
        |                     |   |                       |
         ---------Is---------- --- ---------Ir------------

                 --->
                  Us

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object

        Returns
        ----------
        out_dict: dict
            Output dict containing EEC values
        """

        Lm_table = self.Lm_table
        Im_table = self.Im_table

        # solving elementary system, initial start with unsaturated inductance
        i_start = np.where(Im_table > 0)[0][0]
        self.Lm = Lm_table[i_start]
        delta_Lm = self.solve_elementary()
        if Lm_table.size > 1:
            # iteration until convergence is reached, and max number of iterations on EEC
            delta_Lm_max = 1e-6
            Nmax = 20
            niter_Lm = 1
            while abs(delta_Lm) > delta_Lm_max and niter_Lm < Nmax:
                delta_Lm = self.solve_elementary()
                niter_Lm = niter_Lm + 1

        out_dict = {}

        # remove Lm and Im (still in simulation.elec.eec)
        self.Lm_table = None
        self.Im_table = None

        out_dict["Ud"] = self.U1.real
        out_dict["Uq"] = self.U1.imag
        out_dict["Id"] = self.I1.real
        out_dict["Iq"] = self.I1.imag
        out_dict["Ir"] = self.I2 * self.K21I * np.sqrt(2)

        return out_dict

    # Inlined from Methods.Simulation.EEC_SCIM.solve_elementary
    def solve_elementary(self):
        """Solve the EEC, set the resulting currents and voltages and update the
        magnetizing inductance.

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object

        Returns
        ----------
        delta_Lm: float
            convergence criterion for magnetizing inductance calculation,
            i.e. relative difference between the recalculated magnetizing inductance
            and the current magnetizing inductance
        """

        felec = self.OP.get_felec()
        slip = self.OP.get_slip()
        ws = 2 * np.pi * felec

        Xm = ws * self.Lm
        X1 = ws * self.L1
        X2 = ws * self.L2
        Zm = 1j * Xm
        # magnetizing branch impedance, including iron loss resistance
        Zmf = 1 / (1 / Zm + 1 / self.Rfe)

        # rotor impedance
        if slip == 0:
            Z2 = np.inf
        else:
            Z2 = 1j * X2 + self.R2 / slip

        # stator impedance
        Z1 = 1j * X1 + self.R1

        # total impedance
        Ztot = Z1 + 1 / (1 / Zmf + 1 / Z2)

        U_dict, I_dict = self.OP.get_U0_UPhi0(), self.OP.get_I0_Phi0()
        if U_dict["U0"] is not None:  # Voltage driven
            UPhi0_ref = 0 if U_dict["UPhi0"] is None else U_dict["UPhi0"]
            U1 = U_dict["U0"] * np.exp(1j * UPhi0_ref)
            I1 = (U1 + 1j * 0) / Ztot
            E = U1 - Z1 * I1
            Im = E / Zm
        elif I_dict["I0"] is not None:  # Current driven
            IPhi0_ref = 0 if I_dict["Phi0"] is None else I_dict["Phi0"]
            I1 = I_dict["I0"] * np.exp(1j * IPhi0_ref)
            Im = I1 / (1 + Zm / Z2 + Zm / self.Rfe)
            E = Zm * Im
            U1 = E + Z1 * I1
        else:
            raise Exception("Either U0_ref or I0_ref must be set to solve EEC_SCIM")

        If = E / self.Rfe
        I2 = I1 - (Im + If)

        # recalculating magnetizing inductance
        # linear interpolation with linear extrapolation if Im is outside Im_table
        Lm1 = scp_int.interp1d(
            self.Im_table, self.Lm_table, kind="linear", fill_value="extrapolate"
        )(abs(Im))
        # linear interpolation with nearest extrapolation if Im is outside Im_table
        Lm2 = np.interp(abs(Im), self.Im_table, self.Lm_table)
        # magnetizing inductance is the average of both to simulate the saturation increase
        Lm = 0.5 * (Lm1 + Lm2)

        # calculation of non linearity effect (should be ->0 when Lm(Im)=self.Lm"])
        delta_Lm = abs((Lm - self.Lm) / self.Lm)

        # Update eec parameters
        self.I1 = I1
        self.I2 = I2
        self.Im = Im
        self.If = If
        self.U1 = U1
        self.U2 = E
        self.Lm = Lm

        return delta_Lm

    # Inlined from Methods.Simulation.EEC_SCIM.update_from_ref
    def update_from_ref(self, LUT_ref):
        """Update the equivalent circuit according to the LUT

        Parameters
        ----------
        self : EEC_SCIM
            an EEC_SCIM object
        LUT_ref : LUTslip
            reference LUTslip object
        """

        # Update skin effect to OP/T
        if self.type_skin_effect:
            self.comp_skin_effect()

        # Calculate transformation coefficients
        self.comp_K21()

        eec_ref = LUT_ref.get_eec()
        Tsta_ref, Trot_ref = eec_ref.Tsta, eec_ref.Trot
        Xkr_skinS_ref, Xke_skinS_ref = eec_ref.Xkr_skinS, eec_ref.Xke_skinS
        Xkr_skinR_ref, Xke_skinR_ref = eec_ref.Xkr_skinR, eec_ref.Xke_skinS

        # Compute stator winding resistance
        if eec_ref.R1 is None:
            self.comp_R1()
        else:
            self.comp_R1(R1_ref=eec_ref.R1 / Xkr_skinS_ref, T_ref=Tsta_ref)

        # Compute stator winding inductance
        if eec_ref.L1 is None:
            self.comp_L1()
        else:
            self.comp_L1(L1_ref=eec_ref.L1 / Xke_skinS_ref)

        # Iron loss resistance
        if self.Rfe is None:
            self.Rfe = 1e12  # TODO calculate (or estimate at least)

        # Compute rotor winding resistance
        if eec_ref.R2 is None:
            self.comp_R2()
        else:
            self.comp_R2(R2_ref=eec_ref.R2 / Xkr_skinR_ref, T_ref=Trot_ref)

        # Compute rotor winding inductance
        if eec_ref.L2 is None:
            self.comp_L2()
        else:
            self.comp_L2(L2_ref=eec_ref.L2 / Xke_skinR_ref)

        # Get Im/Lm tables from LUT
        if eec_ref.Lm_table is None or eec_ref.Im_table is None:
            raise Exception("LUT must contains Lm/Im tables to solve EEC_SCIM")
        self.Lm_table = eec_ref.Lm_table / Xke_skinS_ref * self.Xke_skinS
        self.Im_table = eec_ref.Im_table
