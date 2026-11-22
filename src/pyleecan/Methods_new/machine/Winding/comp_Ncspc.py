from ....classes_common.parents import container_or_parent
from . import WindingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_Ncspc(self, Zs: int | None = None, lam: Lamination | None = None) -> float:
    """Compute the number of coils in series per parallel circuit

    Parameters
    ----------
    self : Winding
        A Winding object
    Zs : int
        number of slot
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Returns
    -------
    Ncspc: float
        Number of coils in series per parallel circuit

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

    (Nrad, Ntan) = self.get_dim_wind(lam=lam)
    Ncspc = Zs * Nrad * Ntan / (2.0 * self.qs * self.Npcp)

    return Ncspc
