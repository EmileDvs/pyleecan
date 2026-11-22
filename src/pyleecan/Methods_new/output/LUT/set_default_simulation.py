from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine
    from ....Classes_new.simulation.op_matrix import OPMatrix
    import numpy as np


def set_default_simulation(self, machine: Machine, OP_matrix: OPMatrix | np.ndarray | None = None, name: str | None = None) -> None:
    """Set the default simulation to compute the LUT

    Parameters
    ----------
    self : LUT
        A LUT object
    machine : Machine
        The machine to use in the simulation
    OP_matrix : OP_matrix/ndarray
        OP_matrix to use for VarLoadCurrent
    name : str
        Name of the simulation
    """

    # Local import: avoids circular imports
    from ....Classes_new.simulation.simu_1 import Simu1
    from ....Classes_new.simulation.input_current import InputCurrent
    from ....Classes_new.simulation.var_load_current import VarLoadCurrent
    from ....Classes_new.simulation.op_dq import OPdq
    from ....Classes_new.magnetics.mag_femm import MagFEMM
    from ....Classes_new.post.post_lut import PostLUT


    if name is None:
        name = "comp_LUT_" + machine.name
    simu = Simu1(name=name, machine=machine)

    # Definition of the input
    simu.input = InputCurrent(
        Nt_tot=8 * 12,
        Na_tot=8 * 200,
        OP=OPdq(N0=1000, Id_ref=0, Iq_ref=0),  # Will be overwritten
    )

    # Set varspeed simulation
    simu.var_simu = VarLoadCurrent(
        is_keep_all_output=True,
        stop_if_error=True,
    )
    if OP_matrix is not None:
        simu.var_simu.OP_matrix = OP_matrix  # no set_OP_matrix_obj method

    # Define second simu for FEMM comparison
    simu.mag = MagFEMM(is_periodicity_a=True, is_periodicity_t=True, nb_worker=4)

    # Postprocessing
    simu.var_simu.postproc_list = [PostLUT(is_save_LUT=True)]

    # Set simu in LUT
    self.simu = simu
