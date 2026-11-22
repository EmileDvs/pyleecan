from ....classes_common.errors import FieldMissingError
from ....classes_common.logger_context import get_logger
import os
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.lut import LUT


def run(self, LUT: LUT) -> None:
    """PostProcessing to clean a LUT from un-necessary output
    after the corresponding simulation

    Parameters
    ----------
    self : PostLUT
        A PostLUT object
    LUT: LUT
        LUT object coming from LUT calculation workflow to cleanup
    """

    if LUT.simu is None or LUT.simu.var_simu is None:
        raise FieldMissingError("LUT.simu.var_simu is None: the LUT has no multi-simulation")
    assert LUT.simu.var_simu.is_keep_all_output is True

    # Clean all reference Output (only use output_list)
    LUT.elec = None
    LUT.mag = None
    LUT.struct = None
    LUT.force = None
    LUT.loss = None

    # Clean all un-necessary data from output_list
    for out in LUT.output_list:
        # out.elec is not cleaned
        out.mag.clean(clean_level=5)
        out.struct = None
        out.force = None
        # out.loss = None

    # Save/Store LUT object
    if self.is_save_LUT:
        save_path = os.path.join(LUT.get_path_result(), self.file_name)
        get_logger(self).info("Saving LUT at: " + save_path)
        LUT.save(save_path=save_path)
