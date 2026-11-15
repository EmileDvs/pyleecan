import pytest
from os.path import join
from backend_classes.simulation.op_dq import OPdq

from backend_classes.simulation.simu_1 import Simu1
from backend_classes.simulation.input_current import InputCurrent
from backend_classes.magnetics.mag_femm import MagFEMM

from backend_functions.load import load
from pyleecan.definitions import DATA_DIR


@pytest.mark.long_5s
@pytest.mark.MagFEMM
@pytest.mark.LamSlotMulti
def test_FEMM_LamSlotMultiWind():
    """Test to compute the Flux in FEMM with LamSlotMultiWind."""

    SPMSM_LamSlotMultiWind = load(
        join(DATA_DIR, "Machine", "SPMSM_LamSlotMultiWind.json")
    )
    simu = Simu1(name="test_FEMM_LamSlotMultiWind", machine=SPMSM_LamSlotMultiWind)

    # SPMSM_LamSlotMultiWind.stator.sym_dict_enforced = {
    #     "per_a": 1,
    #     "is_antiper_a": True,
    #     "per_t": 1,
    #     "is_antiper_t": False,
    # }
    simu.input = InputCurrent(
        OP=OPdq(N0=1200, Id_ref=0, Iq_ref=0),
        Ir=None,
        Na_tot=2**6,
        Nt_tot=1,
    )

    simu.mag = MagFEMM(
        type_BH_stator=0,
        type_BH_rotor=0,
        is_periodicity_a=True,
        is_periodicity_t=False,
        is_fast_draw=False,
    )
    simu.elec = None
    simu.force = None

    out = simu.run()
    # out.mag.Tem.plot_2D_Data("time")


# To run it without pytest
if __name__ == "__main__":
    out = test_FEMM_LamSlotMultiWind()
