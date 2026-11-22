from ....classes_common.parents import container_or_parent
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def comp_height_gap(self, machine: Machine | None = None) -> float:
    """Computation of the Height of the gap between the Frame and Outer Lamination

    Parameters
    ----------
    self : FrameBar
        A FrameBar object
    machine : Machine, optional
        Machine holding the frame (default: the parent)

    Returns
    -------
    Hgap: float
        Height of the Gap [m]

    """
    machine = container_or_parent(self, machine, "machine")
    lam_outer = machine.get_lam_list()[-1]

    return self.Rint - lam_outer.Rext
