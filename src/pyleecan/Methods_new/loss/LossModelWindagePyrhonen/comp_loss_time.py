from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output



def comp_loss_time(self, axes_dict: dict[str, Data], is_mirror: bool, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Calculate windage losses and assume they are constant over time

    Parameters
    ----------
    self: LossModelWindagePyrhonen
        a LossModelWindagePyrhonen object
    axes_dict: {Data}
        Dict containing Time (including (anti-)periodicties) and Indices axes used in any Loss module
    is_mirror : bool
        True to mirror magnetic mesh quantities calculate in stator and rotor frames to get the same Time axis
    loss : Loss, optional
        Loss object holding the model (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)

    Returns
    -------
    Pwindage_density : ndarray
        Windage loss density function of time and elements [W/m3]
    Pwindage_dict: {ndarray}
        Dict containing the array of windage losses over time
    """
    loss = container_or_parent(self, loss, "loss")
    output = container_or_parent(self, output, "output", depth=3)

    if output is None:
        raise ValueError("Cannot calculate windage losses if simu is not in an Output")

    if output.elec is None:
        raise ValueError("Cannot calculate windage losses if OutElec is None")

    if loss.is_get_meshsolution and output.mag is None:
        raise ValueError("Cannot calculate windage losses if OutMag is None")

    # Get magnetic meshsolution (airgap group contains elements of both stator and rotor frames)
    meshsol, _ = output.get_frame_meshsolution(self.group, "windage losses")

    Nt = axes_dict["time"].get_length(is_smallestperiod=True)

    # Get element indices associated to airgap group
    Igrp = list(meshsol.group[self.group])

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    machine = output.simu.machine
    Lst = machine.stator.L1

    # Get airgap windage losses
    Ploss = self.comp_loss_value(loss=loss, output=output)

    # Assign same airgap windage losses at every time step
    Pwindage = Ploss * np.ones(Nt, dtype=float)

    # Get surface and number of all elements
    Se_all = meshsol.mesh.get_element_area()

    # Get element surface associated to group
    Se = Se_all[Igrp]

    # Compute the loss density for each element
    # When distributing windage losses on airgap elements, missing area of sliding band
    Pwindage_density = Pwindage[:, None] / (per_a * Lst * Se.sum())

    Pwindage_dict = {"Airgap windage losses": Pwindage}

    # Get fundamental frequency
    felec = output.elec.OP.get_felec()

    # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
    self.coeff_dict = {"3": Ploss / felec**3}

    return Pwindage_density, Pwindage_dict
