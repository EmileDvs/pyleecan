import time
from multiprocessing import cpu_count
from os.path import join

import pytest
from numpy import array

from pyleecan.Classes_new.input_current import InputCurrent
from pyleecan.Classes_new.mag_femm import MagFEMM
from pyleecan.Classes_new.op_dq import OPdq
from pyleecan.Classes_new.simu_1 import Simu1
from pyleecan.Classes_new.var_load_current import VarLoadCurrent
from pyleecan.definitions import DATA_DIR
from pyleecan.Functions.load import load


@pytest.mark.MagFEMM
@pytest.mark.IPMSM
@pytest.mark.periodicity
def test_copy_out():
    """Test the compare method"""
    # Create reference object
    Toyota_Prius = load(join(DATA_DIR, "Machine", "Toyota_Prius.json"))
    simu = Simu1(name="test_copy_out", machine=Toyota_Prius)

    # Initialization of the simulation starting point
    simu.input = InputCurrent()
    # Set time and space discretization
    simu.input.Nt_tot = 8 * 4
    simu.input.Na_tot = 2048
    simu.input.OP = OPdq(N0=3000, Id_ref=0, Iq_ref=0)

    varload = VarLoadCurrent()
    simu.var_simu = varload
    varload.set_OP_array(
        array([[10, 0, 0], [100, 0, 0], [1000, 0, 0]], dtype=float), "N0", "I0", "Phi0"
    )

    # Definition of the magnetic simulation (no symmetry)
    simu.mag = MagFEMM(
        is_periodicity_a=True,
        is_periodicity_t=True,
        nb_worker=cpu_count(),
        Kmesh_fineness=0.2,
        Kgeo_fineness=0.2,
    )
    simu.force = None
    simu.struct = None

    out = simu.run()
    Nb_copy = 1

    # New copy method
    T_new = 0
    for ii in range(Nb_copy):
        T1 = time.time()
        out_3 = out.copy()
        T2 = time.time()
        T_new += T2 - T1

    # Old copy method
    T_old = 0
    for ii in range(Nb_copy):
        T1 = time.time()
        out_2 = type(out)(init_dict=out.as_dict())
        T2 = time.time()
        T_old += T2 - T1

    print("Old method: " + str(T_old / Nb_copy))
    print("New method: " + str(T_new / Nb_copy))

    assert len(out_3.compare(out_2, is_add_value=True)) == 0


if __name__ == "__main__":
    test_copy_out()
