from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def get_loss_density_ag(self, output: Output | None = None) -> float:
    """Get loss density in the airgap

    Parameters
    ----------
    self : OutLoss
        an OutLoss object
    output : Output, optional
        Output of the simulation holding the object (default: the parent)

    Returns
    -------
    loss_density_ag : float
        airgap loss density [W/m^2]

    """
    output = container_or_parent(self, output, "output")

    loss = self.get_loss_overall()

    machine = output.simu.machine

    Rag = machine.comp_Rgap_mec()
    Sag = 2 * np.pi * Rag * machine.stator.L1

    loss_density_ag = loss / Sag

    return loss_density_ag
