from ....classes_common.logger_context import get_logger
from . import WindingError


def comp_Ncps(self) -> float:
    """Compute the number of conductors per slot

    Parameters
    ----------
    self : Winding
        A Winding object

    Returns
    -------
    Ncps: float
        Number of conductors per slot

    """
    Ncps_ = abs(self.get_connection_mat().sum(axis=(0, 1))).sum(axis=1)
    Ncps = Ncps_.mean()

    if Ncps_.std() != 0:
        get_logger(self).warning(
            "LamSlotWind.comp_fill_factor: "
            "Uneven number of conductors per slot. "
            + "Max. number of conductors will be used to compute slot fill factor."
        )
        Ncps = Ncps_.max()

    return Ncps
