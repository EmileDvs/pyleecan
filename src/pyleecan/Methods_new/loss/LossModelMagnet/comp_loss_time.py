from ....classes_common.parents import container_or_parent
import numpy as np

from ....Classes_new.machine.lam_hole import LamHole
from ....Classes_new.machine.lam_slot_mag import LamSlotMag
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.loss.loss import Loss
    from ....Classes_new.output.output import Output


def comp_loss_time(self, axes_dict: dict[str, Data], is_mirror: bool, loss: Loss | None = None, output: Output | None = None) -> tuple[np.ndarray, dict[str, np.ndarray]]:
    """Calculate eddy-current losses in rotor permanent magnets in time domain assuming power density
    is given by (cf. https://www.femm.info/wiki/SPMLoss):

        Pmag = Jm^2/sigma_m with Jm = -sigma_m*dAz/dt + Jc where Jc=<Jm> on the magnet surface

    Parameters
    ----------
    self: LossModelMagnet
        a LossModelMagnet object
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
    Pmagnet_density : ndarray
        Magnet loss density function of time and elements [W/m3]
    Pmagnet_dict: {ndarray}
        Dict containing the array of magnet losses over time

    """
    loss = container_or_parent(self, loss, "loss")
    output = container_or_parent(self, output, "output", depth=3)

    if output is None:
        raise ValueError("Cannot calculate magnet losses if simu is not in an Output")
    else:
        pass

    machine = output.simu.machine

    if isinstance(machine.rotor, LamSlotMag):
        magnet = machine.rotor.magnet
    elif isinstance(machine.rotor, LamHole):
        hole0 = machine.rotor.hole[0]
        magnet = hole0.get_magnet_dict()["magnet_0"]

    # Get rotor length
    Lst = machine.rotor.L1

    # Get magnet electrical conductivity
    sigma_m = magnet.mat_type.elec.get_conductivity(T_op=loss.Trot)

    # Get magnet segmentation coefficient
    if magnet.Lmag is None or magnet.Nseg is None or magnet.Nseg == 1:
        kseg = 1
    else:
        kseg = self.comp_kseg(machine)

    # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
    meshsol, suffix = output.get_frame_meshsolution(self.group, "magnet losses")

    # Get magnetic vector potential over time and for each element center in current group
    if "A_z^{element}" + suffix in meshsol:
        Az = meshsol["A_z^{element}" + suffix].field
    else:
        raise ValueError(
            "Cannot calculate magnet losses if  A_z calculated on element center is not in meshsolution"
        )

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    # Get surface and number of all elements
    Se_all = meshsol.mesh.get_element_area()

    # Get list of element indices for each magnet
    list_Imag = []
    ind_list = []
    for key in meshsol.group:
        if self.group in key and key != self.group:
            ind = int(key.split("_")[-1])
            ind_list.append(ind)
            list_Imag.append(meshsol.group[key])
    Igrp = meshsol.group[self.group]

    # Calculate induced current density and loss density in each magnet
    time_val = axes_dict["time"].get_values(is_smallestperiod=True)
    Pmagnet_density = np.zeros((time_val.size, len(Igrp)))
    jj = 0
    for kmag in list_Imag:
        Se_mag = Se_all[kmag]

        # Compute magnetic vector potential derivative over time
        dAz_dt = Az.get_data_along("time=derivate", "indice=" + str(kmag), "z")

        if is_mirror:
            # Rebuild mesh quantities on time steps given by axes_dict
            dAz_dt_val = dAz_dt.get_along(
                "time=axis_data", "indice", "z=mean", axis_data={"time": time_val}
            )[dAz_dt.symbol]
        else:
            dAz_dt_val = dAz_dt.get_along("time[smallestperiod]", "indice", "z=mean")[
                dAz_dt.symbol
            ]

        # Calculate eddy-current current density in this magnet
        Jm = -sigma_m * dAz_dt_val

        # Ensure average current flowing through the surface is 0
        Jc = np.matmul(Jm, Se_mag)[:, None] / Se_mag.sum()
        Jm -= Jc

        # Calculate loss density due to eddy-current
        Pmagnet_density[:, jj : (jj + len(kmag))] = kseg * Jm**2 / sigma_m

        # Increment by the number elements of in this magnet
        jj += len(kmag)

    # Integrate volumic density over elements volume
    Pmagnet = Lst * per_a * np.matmul(Pmagnet_density, Se_all[Igrp])

    Pmagnet_dict = {self.group + " losses": Pmagnet}

    # Get fundamental frequency
    felec = output.elec.OP.get_felec()

    # Save coefficients to rebuild losses for same (Id,Iq) but at a different speed
    A = Pmagnet.mean() / felec**2
    self.coeff_dict = {"2": A}

    return Pmagnet_density, Pmagnet_dict
