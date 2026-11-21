from ....classes_common.logger_context import get_logger
import os

from ....Functions.Load.import_class import import_class
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_nd import DataND
    from ....Classes_new.machine.machine import Machine
    from ....Classes_new.simulation.op import OP
    import numpy as np


def comp_fluxlinkage(self, machine: Machine | None = None, OP: OP | None = None, Nt_tot=None) -> tuple[np.ndarray, DataND]:
    """Compute flux linkage using magnetic model in self.fluxlink

    Parameters
    ----------
    self : EEC
        an EEC object
    machine: Machine
        a Machine object
    OP: OP
        an OP object
    Nt_tot:
        Number of time steps for magnetic calculation

    Returns
    ----------
    Phi_dqh_mean: ndarray
        Flux linkage in dqh frame
    Phi_wind: DataND
        Stator flux linkage Data object
    """

    Simu1 = import_class("pyleecan.Classes", "Simu1")
    InputCurrent = import_class("pyleecan.Classes", "InputCurrent")
    MagFEMM = import_class("pyleecan.Classes", "MagFEMM")

    if self.fluxlink is None:
        mag_model = MagFEMM()
    else:
        mag_model = self.fluxlink.copy()

    get_logger(self).info("Compute flux linkage with FEMM")

    if machine is None:
        machine = self.get_machine_from_parent()

    # Get simulation name and result path
    if isinstance(machine.parent, Simu1) and machine.parent.name not in [None, ""]:
        simu_name = machine.parent.name + "_FluxLinkFEMM"
        path_result = (
            os.path.join(machine.parent.path_result, "FluxLinkFEMM")
            if machine.parent.path_result not in [None, ""]
            else None
        )
    elif machine.name not in [None, ""]:
        simu_name = machine.name + "_FluxLinkFEMM"
        path_result = None
    else:
        simu_name = "FluxLinkFEMM"
        path_result = None

    # Define simulation
    p = machine.get_pole_pair_number()
    simu = Simu1(elec=None, name=simu_name, path_result=path_result, machine=machine)

    simu.input = InputCurrent(OP=OP, Na_tot=200 * p)
    simu.mag = mag_model
    if Nt_tot is not None:
        simu.input.Nt_tot = Nt_tot
    else:
        simu.input.Nt_tot = int(max(simu.mag.nb_worker * 5, 10) * p)

    # Run Simulation
    out = simu.run()

    # Post-Process
    stator_label = machine.stator.get_label()

    Phi_wind = out.mag.Phi_wind[stator_label]

    Phidqh = Phi_wind.n2dqh(phase_dir=out.elec.phase_dir)
    Phi_dqh_mean = Phidqh.get_along("time=mean", "phase")[Phidqh.symbol]

    return Phi_dqh_mean, Phi_wind
