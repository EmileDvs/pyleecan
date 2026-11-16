from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.slot.hole import Hole
def get_hole_list(self) -> list[Hole]:
    """Return the list of all the holes

    Parameters
    ----------
    self : LamHole
        A LamHole object

    Returns
    -------
    hole_list : [Hole]
        List of all the holes
    """
    if self.hole is None:
        self.hole = list()
    return self.hole
