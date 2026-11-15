import numpy as np

from ....Classes_new.output.lut_dq import LUTdq
from ....Classes_new.simulation.op_matrix import OPMatrix


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
