from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def get_surfaces_closing(self, sym: int = 1, machine: Machine | None = None) -> list:
    """Return the surfaces needed to close the radii of the Lamination

    Parameters
    ----------
    self : Lamination
        A Lamination object
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    surf_list : list
        List of the closing surfaces
    """

    # No notch when bore shape
    if self.bore is None:
        return self.get_notches_surf(sym=sym, machine=machine)
    else:
        return list()
