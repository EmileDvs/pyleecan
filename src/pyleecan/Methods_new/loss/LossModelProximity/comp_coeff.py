from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING
import numpy as np


if TYPE_CHECKING:
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.simulation.simulation import Simulation


def comp_coeff(self, loss: Loss | None = None, simu: Simulation | None = None) -> None:
    """Compute the Proximity loss coefficient [W/kg]

    Parameters
    ----------
    self : LossModelProximity
        a LossModelProximity object
    loss : Loss, optional
        Loss object holding the model (default: the parent)
    simu : Simulation, optional
        Simulation of the loss model (default: the parent of the Loss object)
    """
    loss = container_or_parent(self, loss, "loss")
    simu = container_or_parent(self, simu, "simu", depth=2)
    T_op = loss.Tsta
    winding = simu.machine.stator.winding
    sigma = winding.conductor.cond_mat.elec.get_conductivity(T_op=T_op)
    d = winding.conductor.Wwire
    kf = simu.machine.stator.comp_fill_factor()

    # Proximity loss coefficient [W/kg]
    self.k_p = kf * np.pi**2 / 8 * sigma * d**2
