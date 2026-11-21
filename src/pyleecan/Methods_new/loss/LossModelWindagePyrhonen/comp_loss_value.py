from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output


def comp_loss_value(self, loss: Loss | None = None, output: Output | None = None) -> float:
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
    Ploss : float
        overall windage loss value [W/m3]
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

    machine = output.simu.machine

    OP = output.elec.OP
    felec = OP.get_felec()

    Dr = machine.rotor.Rext * 2
    L = machine.rotor.L1
    p = machine.get_pole_pair_number()
    rho = 1.225  # air density
    k = 1
    omega = 2 * np.pi / p * felec
    delta = machine.comp_length_airgap_active()
    mu = 18.5e-6  # Dynamic viscosity of air
    # Couette Reynolds number
    Re_delta = rho * omega * Dr * delta / (2 * mu)
    # ------------------------------------------ Warning ---------------------------------------------
    # As C_M depends on Re_delta, which depends on the frequency, the coefficient that will be stored
    # in the coeff_dict below depends on frequency. So the coefficient may change with frequency and should be
    # computed again. But to build the coeff_dict, the assumption that C_M will not change must be made.
    # ------------------------------------------------------------------------------------------------
    if Re_delta < 64:
        C_M = 10 * (2 * delta / Dr) ** 0.3 / Re_delta
    elif Re_delta < 5e2:
        C_M = 2 * (2 * delta / Dr) ** 0.3 / Re_delta**0.6
    elif Re_delta < 1e4:
        C_M = 1.03 * (2 * delta / Dr) ** 0.3 / Re_delta**0.5
    else:
        C_M = 0.065 * (2 * delta / Dr) ** 0.3 / Re_delta**0.2

    P1 = 1 / 32 * k * C_M * np.pi * rho * omega**3 * Dr**4 * L

    Dri = machine.rotor.Rint

    # tip Reynolds number
    Re_r = rho * omega * Dr**2 / (4 * mu)

    if Re_r < 3e5:
        C_M = 3.87 / Re_r**0.5
    else:
        C_M = 0.146 / Re_r**0.2

    P2 = 1 / 64 * C_M * rho * omega**3 * (Dr**5 - Dri**5)

    Ploss = P1 + P2

    return Ploss
