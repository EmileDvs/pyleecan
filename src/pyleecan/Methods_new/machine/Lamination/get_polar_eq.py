from ....Methods import NotImplementedYetError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def get_polar_eq(self) -> Lamination:
    """Returns a polar equivalent of the lamination

    Parameters
    ----------
    self : Lamination
        Lamination object

    Returns
    -------
    polar_eq: Lamination
        The polar equivalent of the lamination
    """

    raise NotImplementedYetError("get_polar_eq available only for LamSlotWind for now")

    # A lamination object is already polar (plain cylinder)
    # return type(self)(init_dict=self.as_dict())
