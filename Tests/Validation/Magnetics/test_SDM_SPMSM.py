import numpy as np
import matplotlib.pyplot as plt
import time

import pytest

from os.path import join

from pyleecan.Classes.OPdq import OPdq

from pyleecan.Classes.Simu1 import Simu1
from pyleecan.Classes.InputCurrent import InputCurrent
from pyleecan.Classes.MagSDM import MagSDM
from pyleecan.Classes.SubdomainModel_SPMSM import SubdomainModel_SPMSM

from pyleecan.Functions.load import load
from pyleecan.definitions import DATA_DIR

from SciDataTool.Functions.Plot.plot_3D import plot_3D


# @pytest.mark.long_5s
@pytest.mark.MagSDM
@pytest.mark.periodicity
@pytest.mark.SIPMSM
@pytest.mark.SingleOP
def test_SDM_SPMSM_single_OP(is_periodicity_a=True):
    """Test to compute the Flux in SDM for the SPMSM 12s8p in"""

    SPMSM_001 = load(join(DATA_DIR, "Machine", "SPMSM_001.json"))
    simu = Simu1(name="test_SDM_SPMSM_single_OP", machine=SPMSM_001)

    simu.input = InputCurrent(
        OP=OPdq(N0=1200, Id_ref=0, Iq_ref=0),
        Ir=None,
        Na_tot=1024,
        Nt_tot=8 * 200,
        is_periodicity_a=is_periodicity_a,
        is_periodicity_t=True,
    )

    simu.mag = MagSDM(
        type_BH_stator=0,
        type_BH_rotor=0,
        is_periodicity_a=is_periodicity_a,
        is_periodicity_t=True,
        subdomain_model=SubdomainModel_SPMSM(),
        Nharm_coeff=2,
        is_mmfr=True,
    )

    out = simu.run()

    out.mag.B.plot_2D_Data("angle", "time[0]")
    out.mag.Tem.plot_2D_Data("time")

    return out


if __name__ == "__main__":
    out = test_SDM_SPMSM_single_OP()