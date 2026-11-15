# Multisimulation objects
from backend_classes.simulation.op_dq import OPdq
from backend_classes.simulation.var_param_sweep import VarParamSweep
from backend_classes.simulation.param_explorer_set import ParamExplorerSet
from backend_classes.simulation.data_keeper import DataKeeper
import numpy as np

## Reference simulation
from backend_classes.simulation.simu_1 import Simu1
from numpy import pi, ones, zeros, linspace
from os.path import join
import matplotlib.pyplot as plt
from Tests.New._test_paths import save_validation_path as save_path

from backend_classes.simulation.simu_1 import Simu1

from backend_classes.simulation.input_current import InputCurrent
from backend_classes.import_data.import_gen_vect_lin import ImportGenVectLin
from backend_classes.import_data.import_gen_vect_sin import ImportGenVectSin
from backend_classes.import_data.import_gen_matrix_sin import ImportGenMatrixSin
from backend_classes.import_data.import_matrix_val import ImportMatrixVal
from backend_classes.magnetics.mag_femm import MagFEMM
from backend_classes.force.force_mt import ForceMT
from backend_classes.electrical.eec_pmsm import EEC_PMSM
from backend_classes.electrical.drive_wave import DriveWave
from backend_classes.output.output import Output

# Load the machine
from os.path import join
from backend_functions.load import load
from pyleecan.definitions import DATA_DIR

import pytest


@pytest.mark.MagFEMM
@pytest.mark.long_5s
@pytest.mark.IPMSM
@pytest.mark.VarParam
@pytest.mark.periodicity
def test_slot_scale():
    Toyota_Prius = load(join(DATA_DIR, "Machine", "Toyota_Prius.json"))
    ref_simu = Simu1(name="test_slot_scale", machine=Toyota_Prius)

    # Definition of the enforced output of the electrical module
    Is_mat = zeros((1, 3))
    Is_mat[0, :] = np.array([0, 12.2474, -12.2474])
    Is = ImportMatrixVal(value=Is_mat)
    time = ImportGenVectLin(start=0, stop=0, num=1, endpoint=False)
    Na_tot = 2048

    ref_simu.input = InputCurrent(
        Is=Is,
        Ir=None,  # No winding on the rotor
        OP=OPdq(N0=2504),
        time=time,
        Na_tot=Na_tot,
        angle_rotor_initial=0.86,
    )

    # Definition of the magnetic simulation
    ref_simu.mag = MagFEMM(
        type_BH_stator=0,
        type_BH_rotor=0,
        is_periodicity_a=True,
        Kgeo_fineness=0.2,
        Kmesh_fineness=0.2,
    )

    # Multi-simulation to variate the slot size
    multisim = VarParamSweep(
        stop_if_error=True,
        is_reuse_femm_file=False,
    )

    ref_simu.var_simu = multisim

    def slot_scale(simu, scale_factor):
        """
        Edit stator slot size according to a percentage

        Parameters
        ----------
        simu: Simulation
            simulation to modify
        scale_factor: float
            stator slot scale factor
        """
        simu.machine.stator.slot.W0 *= scale_factor
        simu.machine.stator.slot.W1 *= scale_factor
        simu.machine.stator.slot.W2 *= scale_factor
        simu.machine.stator.slot.H0 *= scale_factor
        simu.machine.stator.slot.H1 *= scale_factor
        simu.machine.stator.slot.H2 *= scale_factor
        simu.machine.stator.slot.R1 *= scale_factor

    # List of ParamExplorer to define multisimulation input values
    paramexplorer_list = [
        ParamExplorerSet(
            name="Stator slot scale factor",
            symbol="stat_slot",
            unit="",
            setter=slot_scale,
            value=linspace(0.1, 1.1, 11).tolist(),
        )
    ]

    multisim.paramexplorer_list = paramexplorer_list

    error_keeper_mag_flux = "lambda simu: np.nan * np.zeros(len(simu.mag.B.Time.get_values()), len(simu.mag.B.Angle.get_values()))"

    # List of DataKeeper to store results
    datakeeper_list = [
        DataKeeper(
            name="Average Torque",
            unit="N.m",
            symbol="Tem_av",
            keeper="lambda output: output.mag.Tem_av",
            error_keeper="lambda simu: np.nan",
        ),
        DataKeeper(
            name="Radial Airgap flux density",
            unit="H",
            symbol="B",
            keeper="lambda output: output.mag.B.components['radial'].get_along('time','angle')['B_{rad}']",
            error_keeper=error_keeper_mag_flux,
        ),
    ]

    multisim.datakeeper_list = datakeeper_list

    # Execute every simulation
    results = ref_simu.run()

    results.plot_multi(
        x_symbol="stat_slot",
        y_symbol="Tem_av",
        title="Average torque in function of the stator slot scale factor ",
        is_show_fig=False,
        save_path=join(save_path, "test_slot_scale"),
    )


if __name__ == "__main__":
    test_slot_scale()
