from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output



def comp_loss_freq(self, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Calculate Windage losses
    Equation from "Design of Rotating Electrical Machines", Second Edition, Pyrhönen, Jokinen, Hrabovcovà p528

    Parameters
    ----------
    self: LossModelWindagePyrhonen
        a LossModelWindagePyrhonen object
    loss : Loss, optional
        Loss object holding the model (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)

    Returns
    -------
    Pjoule_density : ndarray
        loss density function of frequency and elements [W/m3]
    freqs: ndarray
        frequency vector [Hz]
    """
    loss = container_or_parent(self, loss, "loss")
    output = container_or_parent(self, output, "output", depth=3)

    if output is None and self.parent.parent is None:
        raise ValueError("Cannot calculate losses if simu is not in an Output")
    else:
        pass

    if output.elec is None:
        raise ValueError("Cannot calculate losses if OutElec is None")

    if loss.is_get_meshsolution and output.mag is None:
        raise ValueError("Cannot calculate losses if OutMag is None")

    # Get magnetic meshsolution (airgap group contains elements of both stator and rotor frames)
    meshsol, _ = output.get_frame_meshsolution(self.group, "windage losses")

    # Get element indices associated to airgap group
    Igrp = list(meshsol.group[self.group])

    machine = output.simu.machine
    L = machine.rotor.L1
    OP = output.elec.OP
    felec = OP.get_felec()

    Ploss = self.comp_loss_value(loss=loss, output=output)

    power = 3

    coeff = Ploss / felec**power

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    # Get surface elements for airgap
    Se = meshsol.mesh.get_element_area()[Igrp]

    # Compute the loss density for each element
    # When distributing windage losses on airgap elements, missing area of sliding band
    freqs = np.array([felec])
    Pwindage_density = np.zeros((freqs.size, Se.size))
    Pwindage_density[0, :] = Ploss / (per_a * L * np.sum(Se))

    Pwindage_dict = {"Airgap windage losses": np.array([Ploss])}

    self.coeff_dict = {str(power): coeff}

    return Pwindage_density, Pwindage_dict, freqs
