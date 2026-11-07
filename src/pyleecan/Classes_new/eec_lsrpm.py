# Experimental dataclass generated from Generator/ClassesRef/Simulation/EEC_LSRPM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np
from scipy import linalg

from .eec import EEC


@dataclass(eq=False)
class EEC_LSRPM(EEC):
    """Electrical Equivalent Circuit for LSRPM

    Attributes
    ----------
    """

    # Inlined from Methods.Simulation.EEC_LSRPM.comp_joule_losses
    def comp_joule_losses(self, output):
        """Compute the electrical Joule losses

        Parameters
        ----------
        self : Electrical
            an Electrical object
        output : Output
            an Output object
        """

        qs = output.simu.machine.stator.winding.qs
        I_ds = output.elec.Ids_ref
        I_qs = output.elec.Iqs_ref
        I_da = output.elec.Ida_ref
        I_qa = output.elec.Iqa_ref

        R_s = self.parameters["R_s"]
        R_a = self.parameters["R_a"]

        # Id and Iq are in RMS
        Pj_losses = qs * (R_s * (I_ds**2 + I_qs**2) + R_a * (I_da**2 + I_qa**2))

        output.elec.Pj_losses = Pj_losses

    # Inlined from Methods.Simulation.EEC_LSRPM.comp_parameters
    def comp_parameters(self, output, Tsta=None, Trot=None):
        """Compute the parameters dict for the equivalent electrical circuit:
        resistance, inductance and back electromotive force
        Parameters
        ----------
        self : EEC_LSRPM
            an EEC_LSRPM object
        output : Output
            an Output object
        """
        machine = output.simu.machine
        p = machine.rotor.winding.p
        PAR = self.parameters

        if self.N0 is None and self.felec is None:
            N0 = 100 * 60 / p
            felec = 100
        elif self.N0 is None and self.felec is not None:
            N0 = self.felec * 60 / p
        elif self.N0 is not None and self.felec is None:
            N0 = self.N0
            felec = N0 / 60 * p
        else:
            N0 = self.N0
            felec = self.felec

        N_s = machine.stator.winding.comp_Ntspc()  # stator number of turns
        # TODO defind the method "comp_N_auxiliary"
        # N_a = machine.stator.winding.comp_N_auxiliary() # damper winding number of turns
        norm = 1  # rotor - stator transformation factor N_a=N_s

        self.parameters["norm"] = norm

        Tws = 20 if "Tws" not in self.parameters else self.parameter["Tws"]
        Twr = 20 if "Twr" not in self.parameters else self.parameter["Twr"]

        # TODO all methods should be verfied for PMSM with damper winding
        if "R_s" not in self.parameters or self.parameters["Rs"] is None:
            # 3 phase equivalent stator resistance
            self.parameters["Rs"] = machine.stator.comp_resistance_wind(T=Tws)

        if "R_a" not in self.parameters or self.parameters["R_a"] is None:
            # 3 phase equivalent damper resistance
            # TODO have to defind the method"comp_resistance_damper_winding"
            R_a = machine.rotor.comp_resistance_damper_winding(T=Twr, qs=3)
            self.parameters["R_a"] = norm**2 * R_a

        if "Phi_m" not in PAR:
            PAR["Phi_m"] = self.fluxlink.comp_fluxlinkage(output)

        if "C_a" not in PAR:
            self.parameters["C_a"] = 0  # Not sure

        is_comp_ind = False
        # check for complete parameter set
        # (there may be some redundancy here but it seems simplier to implement)
        # if not all(k in PAR for k in ("Phid", "Phiq", "Ld", "Lq")):
        #     is_comp_ind = True

        # check for d- and q-current (change)
        if "I_ds" not in PAR or PAR["I_ds"] != output.elec.Ids_ref:
            PAR["I_ds"] = output.elec.Ids_ref
            is_comp_ind = True

        if "I_qs" not in PAR or PAR["I_qs"] != output.elec.Iqs_ref:
            PAR["I_qs"] = output.elec.Iqs_ref
            is_comp_ind = True

        if "I_da" not in PAR or PAR["I_da"] != output.elec.Ida_ref:
            PAR["I_da"] = output.elec.Ida_ref
            is_comp_ind = True

        if "I_qa" not in PAR or PAR["I_qa"] != output.elec.Iqa_ref:
            PAR["I_qa"] = output.elec.Iqa_ref
            is_comp_ind = True

        if "L_dss" not in self.parameters or self.parameters["L_dss"] is None:
            is_comp_ind = True

        if "L_dmu" not in self.parameters or self.parameters["L_dmu"] is None:
            is_comp_ind = True

        if "L_dsa" not in self.parameters or self.parameters["L_dsa"] is None:
            is_comp_ind = True

        if "L_daa" not in self.parameters or self.parameters["L_daa"] is None:
            is_comp_ind = True

        if "L_qss" not in self.parameters or self.parameters["L_qss"] is None:
            is_comp_ind = True

        if "L_qmu" not in self.parameters or self.parameters["L_qmu"] is None:
            is_comp_ind = True

        if "Lr_qaa" not in self.parameters or self.parameters["Lr_qaa"] is None:
            is_comp_ind = True

        # compute inductance if necessary
        if is_comp_ind:
            print("We will return soon")
            print("Please input all variables")

    # Inlined from Methods.Simulation.EEC_LSRPM.solve
    def solve(self, output):
        """Compute the parameters dict for the equivalent electrical circuit
          cf PhD thesis of SIJIE NI
          "Damper winding for noise and vibration reductionof Permanent Magnet Synchronous Machine"


           -----R_s--L_dss--------------------------------            -----R_s-----L_qss----------------------------------------------------
          |                                   |           |         |                                                            |         |
        ^ |                                  L_dmu      L_daa     ^ |                                                            |        Lr_qaa
        | |                                   |           |       | |                                                            |         |
        | Uds                                L_dsa      R_a       | Uqs                                                        L_qmu      Rr_a
        | |                                   |           |       | |                                                            |         |
          |                                   |         C_a         |                                                            |         C_a
          |                                   |           |         |                                                            |         |
           --wsL_qssI_qs---wsL_qmu(I_qs-Ir_qa)------------            ---wsPhi_m---wsL_dssI_ds---ws(L_dss+L_dmu)(I_ds-Ir_da)----------------
              <--------   <----------------                              <------   <----------   <-------------------------
              <----------------------------                              <-------------------------------------------------
                      wsPhi_qs                                                wsPhi_ds

          Parameters
          ----------
          self : EEC_LSRPM
              an EEC_LSRPM object
          output : Output
              an Output object
        """

        felec = output.elec.felec
        ws = 2 * np.pi * felec

        R_s = self.parameters["R_s"]
        Rr_a = self.parameters["Rr_a"]
        C_a = self.parameters["C_a"]
        norm = self.parameters["norm"]
        Phi_m = self.parametrs["Phi_m"]

        # d-axis
        L_dss = self.parameters["L_dss"]
        L_dmu = self.parameters["L_dmu"]
        L_dsa = self.parameters["L_dsa"]
        L_daa = self.parameters["L_daa"]
        U_ds = self.parameters["U_ds"]
        I_ds = self.parameters["I_ds"]
        I_da = self.parameters["I_da"]

        # q-axis
        L_qss = self.parameters["L_qss"]
        L_qmu = self.parameters["L_qmu"]
        Lr_qaa = self.parameters["Lr_qaa"]
        U_qs = self.parameters["U_qs"]
        I_qs = self.parameters["I_qs"]
        I_qa = self.parameters["I_qa"]

        # Prepare linear system

        # Solve system
        if "U_ds" in self.parameters:
            XR = np.array(
                [
                    [R_s, -ws * (L_qss + L_qmu), 0, -ws * L_qmu],
                    [ws * (L_dss + L_dmu + L_dsa), R_s, -ws * (L_dmu + L_dsa), 0],
                    [0, -ws * L_qmu, Rr_a + 1 / (ws * C_a), ws * (Lr_qaa + L_qmu)],
                    [
                        ws * (L_dmu + L_dsa),
                        0,
                        -ws * (L_daa + L_dmu + L_dsa),
                        Rr_a + 1 / (ws * C_a),
                    ],
                ]
            )
            XE = np.array([0, ws * Phi_m, 0, ws * Phi_m])
            XU = np.array([U_ds, U_qs, 0, 0])
            XI = linalg.solve(XR, XU - XE)

            output.elec.Ids_ref = XI[0]
            output.elec.Iqs_ref = XI[1]
            output.elec.Ida_ref = XI[2]
            output.elec.Iqa_ref = XI[3]
        else:
            output.elec.Uds_ref = (
                I_ds * (R_s + ws * L_dss)
                + (I_ds - I_da) * ws * (L_dmu + L_dsa)
                - ws * L_qmu * (I_qs - I_qa)
                - ws * L_qss * I_qs
            )
            output.elec.Uqs_ref = (
                I_qs * (R_s + ws * L_qss)
                + (I_qs - I_qa) * ws * L_qmu
                + ws * Phi_m
                + ws * L_dss * I_ds
                + ws * (L_dss + L_dmu) * (I_ds - I_da)
            )

        # Compute currents
        output.elec.Is = None
        output.elec.Is = output.elec.get_Is()

        # Compute voltage
        output.elec.Us = None
        output.elec.Us = output.elec.get_Us()
