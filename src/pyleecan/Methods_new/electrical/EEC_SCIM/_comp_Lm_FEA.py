import numpy as np
from multiprocessing import cpu_count

from ....Classes_new.import_data.import_gen_vect_lin import ImportGenVectLin
from ....Classes_new.import_data.import_matrix_val import ImportMatrixVal

from ....Functions_new.SciDataTool.dqh_transformation import abc2n

from ....Functions.Load.import_class import import_class
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def _comp_Lm_FEA(self, machine: Machine, K21Z: float, Xke_skinS: float) -> tuple[float, float]:
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
