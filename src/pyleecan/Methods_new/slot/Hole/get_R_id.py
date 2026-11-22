from ....classes_common.parents import container_or_parent
from ....Functions_new.utils.labels import HOLEV_LAB, VENT_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_R_id(self, lam: Lamination | None = None) -> tuple[int, str]:
    """Return the "Radial" index for label (index in lam.hole or lam.axial_vent)

    Parameters
    ----------
    self : Hole
        A Hole object
    lam : Lamination
        Lamination of the hole (default: the parent of the hole)

    Returns
    -------
    R_id : int
        "Radial" index of the hole in the lamination
    surf_type : str
        Label to use for the surface type (HoleV or Vent)
    """
    lam = container_or_parent(self, lam, "lam")

    if lam is None:  # Compatibility For plotting
        return (0, HOLEV_LAB)
    elif hasattr(lam, "get_hole_list") and self in lam.get_hole_list():
        return (lam.get_hole_list().index(self), HOLEV_LAB)
    elif lam.axial_vent is not None and self in lam.axial_vent:
        return (lam.axial_vent.index(self), VENT_LAB)
    else:
        raise Exception("Error, impossible to get Hole R-id")
