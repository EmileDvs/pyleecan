from . import MagnetIndexError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.magnet import Magnet


def get_magnet_by_id(self, index: int) -> Magnet:
    """Return the magnet at the corresponding index
    returns None is the magnet is None
    Raise error if the hole doesn't have a magnet for the corresponding index

    Parameters
    ----------
    self : Hole
        A Hole object
    index : int
        Index of the magnet to return
    Returns
    -------
    magnet : Magnet
        Magnet object (or None)
    """

    label = "magnet_" + str(index)
    if hasattr(self, label):
        return getattr(self, label)
    elif hasattr(self, "magnet_dict") and label in self.magnet_dict:
        return self.magnet_dict[label]
    else:
        raise MagnetIndexError(
            "Hole of type " + str(type(self)) + " has no magnet " + label
        )
