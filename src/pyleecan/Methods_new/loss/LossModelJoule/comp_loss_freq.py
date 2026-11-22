from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output



def comp_loss_freq(self, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Calculate joule losses in stator windings

    Parameters
    ----------
    self: LossModelJoule
        a LossModelJoule object
    loss : Loss, optional
        Loss object holding the model (default: the parent)
    output : Output, optional
        Output of the simulation (default: the parent of the simulation)

    Returns
    -------
    Pjoule_density : ndarray
        Joule loss density function of frequency and elements [W/m3]
    freqs: ndarray
        frequency vector [Hz]
    """
    loss = container_or_parent(self, loss, "loss")
    output = container_or_parent(self, output, "output", depth=3)

    if output is None:
        raise ValueError("Cannot calculate joule losses if simu is not in an Output")

    if output.elec is None:
        raise ValueError("Cannot calculate joule losses if OutElec is None")

    if loss.is_get_meshsolution and output.mag is None:
        raise ValueError("Cannot calculate Joule losses if OutMag is None")

    # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
    meshsol, suffix = output.get_frame_meshsolution(self.group, "Joule losses")

    machine = output.simu.machine
    lam = machine.stator if "stator" in self.group else machine.rotor
    T_op = loss.Tsta if "stator" in self.group else loss.Trot
    Lst = lam.L1

    OP = output.elec.OP
    felec = OP.get_felec()

    Rs = lam.comp_resistance_wind(T=T_op)
    qs = lam.winding.qs

    if self.type_skin_effect > 0:
        # Account for skin effect
        k = self.comp_coeff(
            output=output,
            T_op=T_op,
        )
    else:
        k = 0

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    # Get stator currents over frequency and phases
    Is = output.elec.get_Is(output=output)
    result = Is.get_along("freqs", "phase[]")
    Is_val = result[Is.symbol]
    freqs = result["freqs"]

    # Calculate Joule losses over time (Assuming fundamental skin correction factor the same for all harmonics)
    Pjoule = (
        Rs * (1 + k * felec**2) * np.sum(0.5 * np.abs(Is_val) ** 2, axis=1)
    )  # Sum over phases

    # Get surface and number of all elements
    Se_all = meshsol.mesh.get_element_area()

    # Get element indices associated to group
    Igrp = meshsol.group[self.group]

    # Get element surface associated to group
    Se = Se_all[Igrp]

    # Calculate uniform element density and sum over frequencies to get average loss density value per element
    Pjoule_density = np.zeros((1, Se.size))
    Pjoule_val = Pjoule.sum()
    Pjoule_density[0, :] = Pjoule_val / (per_a * Lst * Se.sum())

    # Store losses contribution for each frequency in dict
    Pjoule_dict = {self.group + " losses": Pjoule}

    # Get eddy-current proximity loss polynomial coefficient
    A = Pjoule_val / (1 + k * felec**2) * k
    B = Pjoule_val / (1 + k * felec**2)
    self.coeff_dict = {"2": A, "0": B}

    return Pjoule_density, Pjoule_dict, freqs
