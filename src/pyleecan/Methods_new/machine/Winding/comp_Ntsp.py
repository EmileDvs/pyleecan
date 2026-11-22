from ....classes_common.parents import container_or_parent
from ....classes_common.logger_context import get_logger
from . import WindingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def comp_Ntsp(self, Zs: int | None = None, lam: Lamination | None = None) -> float:
    """Compute the number of turns in series per phase

    Parameters
    ----------
    self : Winding
        A Winding object
    Zs : int
        Number of slot
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    Returns
    -------
    Ntspc: float
        Number of turns in series per phase

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

    # effective number of turns in series per phase from connection matrix
    Ntspc_eff_ = (
        abs(self.get_connection_mat(Zs, lam=lam).sum(axis=(0, 1))).sum(axis=0) / self.Npcp / 2
    )
    if Ntspc_eff_.std() != 0:
        get_logger(self).warning(
            "Winding.comp_Ntsp: "
            "Uneven number of turns in series per phase. "
            + "Mean number of turns will be used."
        )

    Ntspc_eff = Ntspc_eff_.mean()

    return Ntspc_eff
