# File generated according to Generator/ClassesRef/Simulation/EEC_SCIM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Simulation/EEC_SCIM"""

from multiprocessing import cpu_count
from os import linesep
from sys import getsizeof

import numpy as np
import scipy.interpolate as scp_int
from pyleecan.Classes.ImportGenVectLin import ImportGenVectLin
from pyleecan.Classes.ImportMatrixVal import ImportMatrixVal

from pyleecan.Classes._check import check_var
from pyleecan.Classes.EEC import EEC
from pyleecan.Functions.Electrical.dqh_transformation import abc2n, n2abc
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import ROTOR_LAB, STATOR_LAB
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.save import save


class EEC_SCIM(EEC):
    """Electric module: Electrical Equivalent Circuit for Squirrel Cage Induction Machine"""

    VERSION = 1

    # cf Methods.Simulation.EEC_SCIM._comp_flux_mean
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

    # cf Methods.Simulation.EEC_SCIM._comp_Lm_FEA
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

    # cf Methods.Simulation.EEC_SCIM.clear_parameters
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

    # cf Methods.Simulation.EEC_SCIM.comp_joule_losses
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

    # cf Methods.Simulation.EEC_SCIM.comp_K21
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

    # cf Methods.Simulation.EEC_SCIM.comp_L1
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

    # cf Methods.Simulation.EEC_SCIM.comp_L2
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

    # cf Methods.Simulation.EEC_SCIM.comp_parameters
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

    # cf Methods.Simulation.EEC_SCIM.comp_R2
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

    # cf Methods.Simulation.EEC_SCIM.comp_skin_effect
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

    # cf Methods.Simulation.EEC_SCIM.solve
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

        out_dict = dict()

        # remove Lm and Im (still in simulation.elec.eec)
        self.Lm_table = None
        self.Im_table = None

        out_dict["Ud"] = self.U1.real
        out_dict["Uq"] = self.U1.imag
        out_dict["Id"] = self.I1.real
        out_dict["Iq"] = self.I1.imag
        out_dict["Ir"] = self.I2 * self.K21I * np.sqrt(2)

        return out_dict

    # cf Methods.Simulation.EEC_SCIM.solve_elementary
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

    # cf Methods.Simulation.EEC_SCIM.update_from_ref
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        Rfe=None,
        L1=None,
        R2=None,
        L2=None,
        K21Z=None,
        K21I=None,
        Im_table=None,
        Lm_table=None,
        I1=None,
        I2=None,
        U1=None,
        U2=None,
        If=None,
        Lm=None,
        Im=None,
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
            if "Rfe" in list(init_dict.keys()):
                Rfe = init_dict["Rfe"]
            if "L1" in list(init_dict.keys()):
                L1 = init_dict["L1"]
            if "R2" in list(init_dict.keys()):
                R2 = init_dict["R2"]
            if "L2" in list(init_dict.keys()):
                L2 = init_dict["L2"]
            if "K21Z" in list(init_dict.keys()):
                K21Z = init_dict["K21Z"]
            if "K21I" in list(init_dict.keys()):
                K21I = init_dict["K21I"]
            if "Im_table" in list(init_dict.keys()):
                Im_table = init_dict["Im_table"]
            if "Lm_table" in list(init_dict.keys()):
                Lm_table = init_dict["Lm_table"]
            if "I1" in list(init_dict.keys()):
                I1 = init_dict["I1"]
            if "I2" in list(init_dict.keys()):
                I2 = init_dict["I2"]
            if "U1" in list(init_dict.keys()):
                U1 = init_dict["U1"]
            if "U2" in list(init_dict.keys()):
                U2 = init_dict["U2"]
            if "If" in list(init_dict.keys()):
                If = init_dict["If"]
            if "Lm" in list(init_dict.keys()):
                Lm = init_dict["Lm"]
            if "Im" in list(init_dict.keys()):
                Im = init_dict["Im"]
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
        self.Rfe = Rfe
        self.L1 = L1
        self.R2 = R2
        self.L2 = L2
        self.K21Z = K21Z
        self.K21I = K21I
        self.Im_table = Im_table
        self.Lm_table = Lm_table
        self.I1 = I1
        self.I2 = I2
        self.U1 = U1
        self.U2 = U2
        self.If = If
        self.Lm = Lm
        self.Im = Im
        # Call EEC init
        super(EEC_SCIM, self).__init__(
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

        EEC_SCIM_str = ""
        # Get the properties inherited from EEC
        EEC_SCIM_str += super(EEC_SCIM, self).__str__()
        EEC_SCIM_str += "Rfe = " + str(self.Rfe) + linesep
        EEC_SCIM_str += "L1 = " + str(self.L1) + linesep
        EEC_SCIM_str += "R2 = " + str(self.R2) + linesep
        EEC_SCIM_str += "L2 = " + str(self.L2) + linesep
        EEC_SCIM_str += "K21Z = " + str(self.K21Z) + linesep
        EEC_SCIM_str += "K21I = " + str(self.K21I) + linesep
        EEC_SCIM_str += (
            "Im_table = "
            + linesep
            + str(self.Im_table).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        EEC_SCIM_str += (
            "Lm_table = "
            + linesep
            + str(self.Lm_table).replace(linesep, linesep + "\t")
            + linesep
            + linesep
        )
        EEC_SCIM_str += "I1 = " + str(self.I1) + linesep
        EEC_SCIM_str += "I2 = " + str(self.I2) + linesep
        EEC_SCIM_str += "U1 = " + str(self.U1) + linesep
        EEC_SCIM_str += "U2 = " + str(self.U2) + linesep
        EEC_SCIM_str += "If = " + str(self.If) + linesep
        EEC_SCIM_str += "Lm = " + str(self.Lm) + linesep
        EEC_SCIM_str += "Im = " + str(self.Im) + linesep
        return EEC_SCIM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from EEC
        if not super(EEC_SCIM, self).__eq__(other):
            return False
        if other.Rfe != self.Rfe:
            return False
        if other.L1 != self.L1:
            return False
        if other.R2 != self.R2:
            return False
        if other.L2 != self.L2:
            return False
        if other.K21Z != self.K21Z:
            return False
        if other.K21I != self.K21I:
            return False
        if not np.array_equal(other.Im_table, self.Im_table):
            return False
        if not np.array_equal(other.Lm_table, self.Lm_table):
            return False
        if other.I1 != self.I1:
            return False
        if other.I2 != self.I2:
            return False
        if other.U1 != self.U1:
            return False
        if other.U2 != self.U2:
            return False
        if other.If != self.If:
            return False
        if other.Lm != self.Lm:
            return False
        if other.Im != self.Im:
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
            super(EEC_SCIM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._Rfe is not None
            and self._Rfe is not None
            and np.isnan(other._Rfe)
            and np.isnan(self._Rfe)
        ):
            pass
        elif other._Rfe != self._Rfe:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Rfe) + ", other=" + str(other._Rfe) + ")"
                )
                diff_list.append(name + ".Rfe" + val_str)
            else:
                diff_list.append(name + ".Rfe")
        if (
            other._L1 is not None
            and self._L1 is not None
            and np.isnan(other._L1)
            and np.isnan(self._L1)
        ):
            pass
        elif other._L1 != self._L1:
            if is_add_value:
                val_str = " (self=" + str(self._L1) + ", other=" + str(other._L1) + ")"
                diff_list.append(name + ".L1" + val_str)
            else:
                diff_list.append(name + ".L1")
        if (
            other._R2 is not None
            and self._R2 is not None
            and np.isnan(other._R2)
            and np.isnan(self._R2)
        ):
            pass
        elif other._R2 != self._R2:
            if is_add_value:
                val_str = " (self=" + str(self._R2) + ", other=" + str(other._R2) + ")"
                diff_list.append(name + ".R2" + val_str)
            else:
                diff_list.append(name + ".R2")
        if (
            other._L2 is not None
            and self._L2 is not None
            and np.isnan(other._L2)
            and np.isnan(self._L2)
        ):
            pass
        elif other._L2 != self._L2:
            if is_add_value:
                val_str = " (self=" + str(self._L2) + ", other=" + str(other._L2) + ")"
                diff_list.append(name + ".L2" + val_str)
            else:
                diff_list.append(name + ".L2")
        if (
            other._K21Z is not None
            and self._K21Z is not None
            and np.isnan(other._K21Z)
            and np.isnan(self._K21Z)
        ):
            pass
        elif other._K21Z != self._K21Z:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._K21Z) + ", other=" + str(other._K21Z) + ")"
                )
                diff_list.append(name + ".K21Z" + val_str)
            else:
                diff_list.append(name + ".K21Z")
        if (
            other._K21I is not None
            and self._K21I is not None
            and np.isnan(other._K21I)
            and np.isnan(self._K21I)
        ):
            pass
        elif other._K21I != self._K21I:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._K21I) + ", other=" + str(other._K21I) + ")"
                )
                diff_list.append(name + ".K21I" + val_str)
            else:
                diff_list.append(name + ".K21I")
        if not np.array_equal(other.Im_table, self.Im_table):
            diff_list.append(name + ".Im_table")
        if not np.array_equal(other.Lm_table, self.Lm_table):
            diff_list.append(name + ".Lm_table")
        if other._I1 != self._I1:
            if is_add_value:
                val_str = " (self=" + str(self._I1) + ", other=" + str(other._I1) + ")"
                diff_list.append(name + ".I1" + val_str)
            else:
                diff_list.append(name + ".I1")
        if other._I2 != self._I2:
            if is_add_value:
                val_str = " (self=" + str(self._I2) + ", other=" + str(other._I2) + ")"
                diff_list.append(name + ".I2" + val_str)
            else:
                diff_list.append(name + ".I2")
        if other._U1 != self._U1:
            if is_add_value:
                val_str = " (self=" + str(self._U1) + ", other=" + str(other._U1) + ")"
                diff_list.append(name + ".U1" + val_str)
            else:
                diff_list.append(name + ".U1")
        if other._U2 != self._U2:
            if is_add_value:
                val_str = " (self=" + str(self._U2) + ", other=" + str(other._U2) + ")"
                diff_list.append(name + ".U2" + val_str)
            else:
                diff_list.append(name + ".U2")
        if other._If != self._If:
            if is_add_value:
                val_str = " (self=" + str(self._If) + ", other=" + str(other._If) + ")"
                diff_list.append(name + ".If" + val_str)
            else:
                diff_list.append(name + ".If")
        if (
            other._Lm is not None
            and self._Lm is not None
            and np.isnan(other._Lm)
            and np.isnan(self._Lm)
        ):
            pass
        elif other._Lm != self._Lm:
            if is_add_value:
                val_str = " (self=" + str(self._Lm) + ", other=" + str(other._Lm) + ")"
                diff_list.append(name + ".Lm" + val_str)
            else:
                diff_list.append(name + ".Lm")
        if other._Im != self._Im:
            if is_add_value:
                val_str = " (self=" + str(self._Im) + ", other=" + str(other._Im) + ")"
                diff_list.append(name + ".Im" + val_str)
            else:
                diff_list.append(name + ".Im")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from EEC
        S += super(EEC_SCIM, self).__sizeof__()
        S += getsizeof(self.Rfe)
        S += getsizeof(self.L1)
        S += getsizeof(self.R2)
        S += getsizeof(self.L2)
        S += getsizeof(self.K21Z)
        S += getsizeof(self.K21I)
        S += getsizeof(self.Im_table)
        S += getsizeof(self.Lm_table)
        S += getsizeof(self.I1)
        S += getsizeof(self.I2)
        S += getsizeof(self.U1)
        S += getsizeof(self.U2)
        S += getsizeof(self.If)
        S += getsizeof(self.Lm)
        S += getsizeof(self.Im)
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
        EEC_SCIM_dict = super(EEC_SCIM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs,
        )
        EEC_SCIM_dict["Rfe"] = self.Rfe
        EEC_SCIM_dict["L1"] = self.L1
        EEC_SCIM_dict["R2"] = self.R2
        EEC_SCIM_dict["L2"] = self.L2
        EEC_SCIM_dict["K21Z"] = self.K21Z
        EEC_SCIM_dict["K21I"] = self.K21I
        if self.Im_table is None:
            EEC_SCIM_dict["Im_table"] = None
        else:
            if type_handle_ndarray == 0:
                EEC_SCIM_dict["Im_table"] = self.Im_table.tolist()
            elif type_handle_ndarray == 1:
                EEC_SCIM_dict["Im_table"] = self.Im_table.copy()
            elif type_handle_ndarray == 2:
                EEC_SCIM_dict["Im_table"] = self.Im_table
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        if self.Lm_table is None:
            EEC_SCIM_dict["Lm_table"] = None
        else:
            if type_handle_ndarray == 0:
                EEC_SCIM_dict["Lm_table"] = self.Lm_table.tolist()
            elif type_handle_ndarray == 1:
                EEC_SCIM_dict["Lm_table"] = self.Lm_table.copy()
            elif type_handle_ndarray == 2:
                EEC_SCIM_dict["Lm_table"] = self.Lm_table
            else:
                raise Exception(
                    "Unknown type_handle_ndarray: " + str(type_handle_ndarray)
                )
        if self.I1 is None:
            EEC_SCIM_dict["I1"] = None
        elif isinstance(self.I1, float):
            EEC_SCIM_dict["I1"] = self.I1
        else:
            EEC_SCIM_dict["I1"] = str(self.I1)
        if self.I2 is None:
            EEC_SCIM_dict["I2"] = None
        elif isinstance(self.I2, float):
            EEC_SCIM_dict["I2"] = self.I2
        else:
            EEC_SCIM_dict["I2"] = str(self.I2)
        if self.U1 is None:
            EEC_SCIM_dict["U1"] = None
        elif isinstance(self.U1, float):
            EEC_SCIM_dict["U1"] = self.U1
        else:
            EEC_SCIM_dict["U1"] = str(self.U1)
        if self.U2 is None:
            EEC_SCIM_dict["U2"] = None
        elif isinstance(self.U2, float):
            EEC_SCIM_dict["U2"] = self.U2
        else:
            EEC_SCIM_dict["U2"] = str(self.U2)
        if self.If is None:
            EEC_SCIM_dict["If"] = None
        elif isinstance(self.If, float):
            EEC_SCIM_dict["If"] = self.If
        else:
            EEC_SCIM_dict["If"] = str(self.If)
        EEC_SCIM_dict["Lm"] = self.Lm
        if self.Im is None:
            EEC_SCIM_dict["Im"] = None
        elif isinstance(self.Im, float):
            EEC_SCIM_dict["Im"] = self.Im
        else:
            EEC_SCIM_dict["Im"] = str(self.Im)
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        EEC_SCIM_dict["__class__"] = "EEC_SCIM"
        return EEC_SCIM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        Rfe_val = self.Rfe
        L1_val = self.L1
        R2_val = self.R2
        L2_val = self.L2
        K21Z_val = self.K21Z
        K21I_val = self.K21I
        if self.Im_table is None:
            Im_table_val = None
        else:
            Im_table_val = self.Im_table.copy()
        if self.Lm_table is None:
            Lm_table_val = None
        else:
            Lm_table_val = self.Lm_table.copy()
        I1_val = self.I1
        I2_val = self.I2
        U1_val = self.U1
        U2_val = self.U2
        If_val = self.If
        Lm_val = self.Lm
        Im_val = self.Im
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
            Rfe=Rfe_val,
            L1=L1_val,
            R2=R2_val,
            L2=L2_val,
            K21Z=K21Z_val,
            K21I=K21I_val,
            Im_table=Im_table_val,
            Lm_table=Lm_table_val,
            I1=I1_val,
            I2=I2_val,
            U1=U1_val,
            U2=U2_val,
            If=If_val,
            Lm=Lm_val,
            Im=Im_val,
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

        self.Rfe = None
        self.L1 = None
        self.R2 = None
        self.L2 = None
        self.K21Z = None
        self.K21I = None
        self.Im_table = None
        self.Lm_table = None
        self.I1 = None
        self.I2 = None
        self.U1 = None
        self.U2 = None
        self.If = None
        self.Lm = None
        self.Im = None
        # Set to None the properties inherited from EEC
        super(EEC_SCIM, self)._set_None()

    def _get_Rfe(self):
        """getter of Rfe"""
        return self._Rfe

    def _set_Rfe(self, value):
        """setter of Rfe"""
        check_var("Rfe", value, "float")
        self._Rfe = value

    Rfe = property(
        fget=_get_Rfe,
        fset=_set_Rfe,
        doc="""Iron loss resistance

        :Type: float
        """,
    )

    def _get_L1(self):
        """getter of L1"""
        return self._L1

    def _set_L1(self, value):
        """setter of L1"""
        check_var("L1", value, "float")
        self._L1 = value

    L1 = property(
        fget=_get_L1,
        fset=_set_L1,
        doc="""Stator phase inductance

        :Type: float
        """,
    )

    def _get_R2(self):
        """getter of R2"""
        return self._R2

    def _set_R2(self, value):
        """setter of R2"""
        check_var("R2", value, "float")
        self._R2 = value

    R2 = property(
        fget=_get_R2,
        fset=_set_R2,
        doc="""Rotor phase resistance

        :Type: float
        """,
    )

    def _get_L2(self):
        """getter of L2"""
        return self._L2

    def _set_L2(self, value):
        """setter of L2"""
        check_var("L2", value, "float")
        self._L2 = value

    L2 = property(
        fget=_get_L2,
        fset=_set_L2,
        doc="""Rotor phase inductance

        :Type: float
        """,
    )

    def _get_K21Z(self):
        """getter of K21Z"""
        return self._K21Z

    def _set_K21Z(self, value):
        """setter of K21Z"""
        check_var("K21Z", value, "float")
        self._K21Z = value

    K21Z = property(
        fget=_get_K21Z,
        fset=_set_K21Z,
        doc="""transformation ratio from secondary (2, rotor) to primary (1, stator) for impedance

        :Type: float
        """,
    )

    def _get_K21I(self):
        """getter of K21I"""
        return self._K21I

    def _set_K21I(self, value):
        """setter of K21I"""
        check_var("K21I", value, "float")
        self._K21I = value

    K21I = property(
        fget=_get_K21I,
        fset=_set_K21I,
        doc="""transformation ratio from secondary (2, rotor) to primary (1, stator) for current

        :Type: float
        """,
    )

    def _get_Im_table(self):
        """getter of Im_table"""
        return self._Im_table

    def _set_Im_table(self, value):
        """setter of Im_table"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("Im_table", value, "ndarray")
        self._Im_table = value

    Im_table = property(
        fget=_get_Im_table,
        fset=_set_Im_table,
        doc="""Array of magnetizing current

        :Type: ndarray
        """,
    )

    def _get_Lm_table(self):
        """getter of Lm_table"""
        return self._Lm_table

    def _set_Lm_table(self, value):
        """setter of Lm_table"""
        if type(value) is int and value == -1:
            value = np.array([])
        elif type(value) is list:
            try:
                value = np.array(value)
            except:
                pass
        check_var("Lm_table", value, "ndarray")
        self._Lm_table = value

    Lm_table = property(
        fget=_get_Lm_table,
        fset=_set_Lm_table,
        doc="""Array of magnetizing inductance function of Im_table

        :Type: ndarray
        """,
    )

    def _get_I1(self):
        """getter of I1"""
        return self._I1

    def _set_I1(self, value):
        """setter of I1"""
        if isinstance(value, str):
            value = complex(value)
        check_var("I1", value, "complex")
        self._I1 = value

    I1 = property(
        fget=_get_I1,
        fset=_set_I1,
        doc="""Stator phase current (after solve)

        :Type: complex
        """,
    )

    def _get_I2(self):
        """getter of I2"""
        return self._I2

    def _set_I2(self, value):
        """setter of I2"""
        if isinstance(value, str):
            value = complex(value)
        check_var("I2", value, "complex")
        self._I2 = value

    I2 = property(
        fget=_get_I2,
        fset=_set_I2,
        doc="""Rotor phase current (after solve)

        :Type: complex
        """,
    )

    def _get_U1(self):
        """getter of U1"""
        return self._U1

    def _set_U1(self, value):
        """setter of U1"""
        if isinstance(value, str):
            value = complex(value)
        check_var("U1", value, "complex")
        self._U1 = value

    U1 = property(
        fget=_get_U1,
        fset=_set_U1,
        doc="""Stator phase voltage (after solve)

        :Type: complex
        """,
    )

    def _get_U2(self):
        """getter of U2"""
        return self._U2

    def _set_U2(self, value):
        """setter of U2"""
        if isinstance(value, str):
            value = complex(value)
        check_var("U2", value, "complex")
        self._U2 = value

    U2 = property(
        fget=_get_U2,
        fset=_set_U2,
        doc="""Rotor phase voltage (after solve)

        :Type: complex
        """,
    )

    def _get_If(self):
        """getter of If"""
        return self._If

    def _set_If(self, value):
        """setter of If"""
        if isinstance(value, str):
            value = complex(value)
        check_var("If", value, "complex")
        self._If = value

    If = property(
        fget=_get_If,
        fset=_set_If,
        doc="""Iron loss current (after solve)

        :Type: complex
        """,
    )

    def _get_Lm(self):
        """getter of Lm"""
        return self._Lm

    def _set_Lm(self, value):
        """setter of Lm"""
        check_var("Lm", value, "float")
        self._Lm = value

    Lm = property(
        fget=_get_Lm,
        fset=_set_Lm,
        doc="""Magnetizing inductance (after solve)

        :Type: float
        """,
    )

    def _get_Im(self):
        """getter of Im"""
        return self._Im

    def _set_Im(self, value):
        """setter of Im"""
        if isinstance(value, str):
            value = complex(value)
        check_var("Im", value, "complex")
        self._Im = value

    Im = property(
        fget=_get_Im,
        fset=_set_Im,
        doc="""Magnetizing current (after solve)

        :Type: complex
        """,
    )
