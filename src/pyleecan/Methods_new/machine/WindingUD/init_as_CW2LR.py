from ....classes_common.parents import container_or_parent
import numpy as np

from ..Winding import WindingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def init_as_CW2LR(self, Zs: int | None = None, lam: Lamination | None = None) -> None:
    """Compute the Winding Matrix (for winding type 5) (Nlay_rad=1,Nlay_tan=1)
    type 5 : TOOTH WINDING, DOUBLE LAYER ALL TEETH WOUND, RADIAL SUPERPOSITION

    Parameters
    ----------
    self : WindingUD
        A: WindingUD object
    Zs : int
        Number of Slot (Integer >0)
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Raises
    ------
    WindingT5DefMsError
        You must have 0.25< Zs/2/p/qs <= 0.5

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

    # ex "Effect of Pole and Slot Combination on Noise and Vibration in Permanent
    # Magnet Synchronous Motor" creates highest harmonic at Zs/2+1 and Zs/2-1
    nlay = 2.0
    qs = float(self.qs)
    p = float(self.p)
    Ncgr = Zs / nlay / qs
    ms = Zs / 2.0 / p / qs
    # Ncspc= Zs/(2.0*qs*self.Npcp/nlay)  # number of coils in series per parallel circuit
    # Ntspc = self.Ntcoil * Ncspc #Number of turns in series per phase
    Ntcoil = self.Ntcoil  # Number of turns per coils

    wind_mat = np.zeros((2, 1, Zs, self.qs))
    # creates highest harmonic at Zs/2+1 and Zs/2-1
    if ms == 0.5:  # then Zs/qs is integer
        # traditional non overlapping all teeth wound winding
        for q in range(0, self.qs):
            for k in range(0, Zs // self.qs):  # number of Ncgr coils
                xenc = q + np.array([1, 0]) + k * qs
                wind_mat[0, 0, int(np.mod(xenc[0] - 1, Zs)), q] = +Ntcoil  # right/top/2
                wind_mat[1, 0, int(np.mod(xenc[1] - 1, Zs)), q] = -Ntcoil  # left/bottom/1
    elif (
        ms != 0.5 and Ncgr % 1 == 0
    ):  # ms!=0.5 and Ncgr is an integer (ms>0.25 && ms<0.5)
        # new algorithm to reverse the coils
        for q in range(0, self.qs):
            for k in range(0, int((Zs // self.qs) // Ncgr)):  # number of Ncgr coils
                for l in range(0, int(Ncgr)):
                    id0 = int(np.mod(q * Ncgr + 0 + k * qs * Ncgr - 1 + l, Zs))
                    id1 = int(np.mod(q * Ncgr + 1 + k * qs * Ncgr - 1 + l, Zs))
                    # left / bottom / 1
                    wind_mat[1, 0, id0, q] = -((-1) ** (l + q - 1 + k)) * Ntcoil
                    # right / top / 2
                    wind_mat[0, 0, id1, q] = +((-1) ** (l + q - 1 + k)) * Ntcoil

        wind_mat = wind_mat[:, :, ::-1, :]
    else:
        raise WindingT5DefMsError(
            "Winding geometry not handled yet, enter "
            "your own winding matrix with "
            "type_winding=0 and contact EOMYS"
        )

    # Set default values
    if self.is_reverse_wind is None:
        self.is_reverse_wind = False
    if self.Nslot_shift_wind is None:
        self.Nslot_shift_wind = 0
    self.Nlayer = 2
    # Apply the transformations
    if self.is_reverse_wind:
        wind_mat = self.reverse_wind_mat(wind_mat)
    if self.Nslot_shift_wind > 0:
        wind_mat = self.shift_wind_mat(wind_mat, self.Nslot_shift_wind)

    self.wind_mat = wind_mat
    # Matrix changed, compute again periodicity
    self.per_a = None
    self.is_aper_a = None


class WindingT5DefMsError(WindingError):
    """

    Parameters
    ----------

    Returns
    -------

    Raises
    ------
    must
        be 0

    """

    pass
