from ....classes_common.parents import container_or_parent
import numpy as np
from . import WindingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_phasor_angle(self, Zs: int | None = None, lam: Lamination | None = None) -> np.ndarray:
    """Compute the phasor angle of the winding phases related to the first slot

    Parameters
    ----------
    self : Winding
        A: Winding object
    Zs : int
        Number of Slot (Integer >0)
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Returns
    -------
    angle_vec: numpy.ndarray
        Phasor Angle Vector (qs)

    Raises
    ------

    """
    lam = container_or_parent(self, lam, "lam")
    if Zs is None:
        if lam is None:
            raise WindingError(
                "ERROR: The Winding object must be in a Lamination object."
            )

        if lam.slot is None:
            raise WindingError(
                "ERROR: The Winding object must be in a Lamination object with Slot."
            )

        Zs = lam.slot.Zs

    assert Zs > 0, "Zs must be >0"
    assert Zs % 1 == 0, "Zs must be an integer"

    wind_mat = self.get_connection_mat(Zs, lam=lam)
    p = self.p
    qs = self.qs  # number of phases

    slot_ang = (
        np.linspace(0, Zs, num=Zs, endpoint=False) * 2 * np.pi / Zs * p
    )  # slot electrical angle
    phasor = np.exp(1j * slot_ang)  # slot voltage phasor

    angle_vec = np.zeros(qs)

    for phase in range(qs):
        wind_sum = np.sum(wind_mat[:, :, :, phase], (0, 1))
        phasor_sum = np.sum(wind_sum * phasor)
        angle_vec[phase] = np.angle(phasor_sum)

    return angle_vec
