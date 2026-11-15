import numpy as np
from . import WindingError


def comp_winding_factor(self, Harmonics=[1]):
    """Compute the winding factor of phase 1 (asuming symmetry)

    Parameters
    ----------
    self : Winding
        A: Winding object
    Harmonics : list of floats
        list of harmonics to calculate the winding factor

    Returns
    -------
    xi: numpy.ndarray
        winding factor

    Raises
    ------

    """
    if self.parent is None:
        raise WindingError("ERROR: The Winding object must be in a Lamination object.")

    if self.parent.slot is None:
        raise WindingError(
            "ERROR: The Winding object must be in a Lamination object with Slot."
        )

    Zs = self.parent.slot.Zs

    assert Zs > 0, "Zs must be >0"
    assert Zs % 1 == 0, "Zs must be an integer"

    wind_mat = self.get_connection_mat(Zs)
    p = self.p

    # slot electrical angle
    slot_ang = np.linspace(0, Zs, num=Zs, endpoint=False) * 2 * np.pi / Zs * p

    phase = 0
    wind_ph1 = np.sum(wind_mat[:, :, :, phase], (0, 1))
    wind_ref = np.sum(np.abs(wind_mat[:, :, :, phase]))

    xi = list()

    for harm in Harmonics:
        xi.append(np.abs(np.sum(np.exp(1j * slot_ang * harm) * wind_ph1)) / wind_ref)

    xi = np.array(xi)

    return xi
