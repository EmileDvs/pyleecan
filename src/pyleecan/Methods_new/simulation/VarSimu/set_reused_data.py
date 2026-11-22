from ....classes_common.errors import FieldMissingError
from ....classes_common.logger_context import get_logger
from ....Classes_new.magnetics.mag_femm import MagFEMM
from ....Classes_new.electrical.elec_lut_dq import ElecLUTdq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output
    from ....Classes_new.simulation.simulation import Simulation


def set_reused_data(self, simu: Simulation, output: Output, is_log: bool = True, simu_type: str = "VarSimu") -> None:
    """Resuse some data from the reference simulation to skip computation

    Parameters
    ----------
    self : VarSimu
        a VarSimu object
    simu : Simulation
        The simulation to update
    output : Output
        Output from the reference simulation to enforce
    is_log : bool
        True to log the changes
    simu_type : str
        Name of the multi-simulation kind
    """

    if simu.layer == 2:
        TAB = "    "
    else:
        TAB = ""

    if self.is_reuse_femm_file and isinstance(simu.mag, MagFEMM):
        if output.mag.internal is None:
            raise FieldMissingError("OutMag.internal is None: the reference output has no FEMM file to reuse")
        if is_log:
            get_logger(self).info(
                TAB
                + simu_type
                + ": Using same FEMM file for all simulations ("
                + output.mag.internal.FEMM_dict["path_save"]
                + ")"
            )
        simu.mag.import_file = output.mag.internal.FEMM_dict["path_save"]
        simu.mag.FEMM_dict_enforced = output.mag.internal.FEMM_dict

    if self.is_reuse_LUT and isinstance(simu.elec, ElecLUTdq):
        if is_log:
            get_logger(self).info(
                TAB + simu_type + ": Using same LUT for all simulations"
            )
        if output.simu.elec is None:
            raise FieldMissingError("Simulation.elec is None: the reference simulation has no electrical model")
        simu.elec.LUT_enforced = output.simu.elec.LUT_enforced
