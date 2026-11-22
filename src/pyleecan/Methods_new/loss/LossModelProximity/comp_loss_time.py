from ....classes_common.parents import container_or_parent
import numpy as np
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output



def comp_loss_time(self, axes_dict: dict[str, Data], is_mirror: bool, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Calculate proximity loss density over time

        Pprox_density = k_p * (dB/dt)^2

    Parameters
    ----------
    self: LossModelProximity
        a LossModelProximity object
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
    Pprox_density : ndarray
        Proximity loss density function of time and elements [W/m3]
    Pprox_dict: {ndarray}
        Dict containing the array of proximity losses over time
    """
    output = container_or_parent(self, output, "output", depth=3)

    if output is None:
        raise ValueError(
            "Cannot calculate proximity losses if simu is not in an Output"
        )
    else:
        pass

    machine = output.simu.machine

    lamination = machine.stator if "stator" in self.group else machine.rotor
    Lst = lamination.L1

    # Compute the Proximity loss coefficient (if not enforced)
    if self.k_p is None:
        self.comp_coeff(loss=loss, simu=output.simu)
    k_p = self.k_p

    # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
    meshsol, suffix = output.get_frame_meshsolution(self.group, "proximity losses")

    if "B" + suffix in meshsol:
        Bvect = meshsol["B" + suffix].field
    else:
        raise ValueError(
            "Cannot calculate proximity losses if B is not in meshsolution"
        )

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    # Get surface and number of all elements
    Se_all = meshsol.mesh.get_element_area()

    # Get element indices associated to group
    Igrp = meshsol.group[self.group]

    # Get element surface associated to group
    Se = Se_all[Igrp]

    # Compute magnetic flux density derivative over time
    dB_dt_v = Bvect.get_vectorfield_along("time=derivate", "indice", "z")

    if is_mirror:
        # Rebuild mesh quantities on time steps given by axes_dict
        time_val = axes_dict["time"].get_values(is_smallestperiod=True)
        dB_dt = dB_dt_v.get_xyz_along(
            "time=axis_data",
            "indice=" + str(Igrp),
            "z=mean",
            axis_data={"time": time_val},
        )
    else:
        dB_dt = dB_dt_v.get_xyz_along(
            "time[smallestperiod]", "indice=" + str(Igrp), "z=mean"
        )

    # Compute the loss density for each element function of time
    Pprox_density = k_p / (2 * np.pi**2) * (dB_dt["comp_x"] ** 2 + dB_dt["comp_y"] ** 2)

    # Integrate volumic density over core volume
    Pprox = Lst * per_a * np.matmul(Pprox_density, Se)

    Pprox_dict = {self.group + " losses": Pprox}

    # Get fundamental frequency
    felec = output.elec.OP.get_felec()

    # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
    A = Pprox.mean() / felec**2
    self.coeff_dict = {"2": A}

    return Pprox_density, Pprox_dict
