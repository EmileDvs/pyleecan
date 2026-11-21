import numpy as np

from ....Functions_new.MeshSolution.get_frame_meshsolution import get_frame_meshsolution


def comp_loss_freq(self) -> tuple[np.ndarray, dict[str, np.ndarray], np.ndarray]:
    """Calculate proximity loss density assuming it is given by an eddy-current loss model depending on frequency:

        P = k_p * f^2 * B^2

    Parameters
    ----------
    self: LossModelProximity
        a LossModelProximity object

    Returns
    -------
    Pprox_density : ndarray
        Average proximity loss density (frequency=0Hz) for all elements [W/m3]
    Pprox_dict: {ndarray}
        Dict containing the array of proximity losses by contribution and for all frequencies in magnetic flux density [W]
    freqs: ndarray
        frequency vector of magnetic flux density harmonics [Hz]
    """

    if self.parent.parent.parent is None:
        raise ValueError(
            "Cannot calculate proximity losses if simu is not in an Output"
        )
    else:
        output = self.parent.parent.parent

    machine = output.simu.machine

    lamination = machine.stator if "stator" in self.group else machine.rotor
    Lst = lamination.L1

    # Compute the Proximity loss coefficient (if not enforced)
    if self.k_p is None:
        self.comp_coeff()
    k_p = self.k_p

    # Get fundamental frequency
    felec = output.elec.OP.get_felec()

    # Get magnetic meshsolution and label suffix of the frame in which group quantities are calculated
    meshsol, suffix = get_frame_meshsolution(output, self.group, "proximity losses")

    if "B" + suffix in meshsol:
        Bvect = meshsol["B" + suffix].field
    else:
        raise ValueError(
            "Cannot calculate proximity losses if B is not in meshsolution"
        )

    # Get mesh spatial symmetries (including (anti)-periodicities)
    per_a = meshsol.mesh.sym

    # Get element indices associated to group
    Igrp = meshsol.group[self.group]

    # Get element surface associated to group
    Se = meshsol.mesh.get_element_area()[Igrp]

    # Compute magnetic flux density FFT
    Bfft = Bvect.get_xyz_along("freqs", "indice=" + str(Igrp), "z=mean")
    freqs = Bfft["freqs"]
    Bfft_square = np.abs(Bfft["comp_x"]) ** 2 + np.abs(Bfft["comp_y"]) ** 2

    # Compute the loss density for each frequency and element
    Pprox_density = k_p * freqs[:, None] ** 2 * Bfft_square

    # Integrate volumic density over core volume to get loss value
    Pprox = Lst * per_a * np.matmul(Pprox_density, Se)

    # Sum over frequencies to get average loss density value per element
    Pprox_density = np.sum(Pprox_density, axis=0, keepdims=True)

    # Store losses contribution for each frequency in dict
    Pprox_dict = {self.group + " losses": Pprox}

    # Get eddy-current proximity loss polynomial coefficient
    A = np.sum(Pprox) / felec**2
    self.coeff_dict = {"2.0": A}

    return Pprox_density, Pprox_dict, freqs
