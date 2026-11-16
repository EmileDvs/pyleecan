from ....Functions_new.labels import decode_label
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.magnet import Magnet


def get_magnet_by_label(self, label: str | None = None, label_dict: dict | None = None) -> Magnet:
    """Return the magnet corresponding to the label

    Parameters
    ----------
    self : LamSlotMagNS
        A LamSlotMagNS object
    label : str
        A surface id (ex Rotor-0_Magnet_R0-T0-S0)
    label_dict : dict
        Split dict of the label (to avoid decoding twice)

    Returns
    -------
    mag : Magnet
        The corresponding magnet object
    """

    # Decode the magnet label
    if label_dict is None and label is None:
        raise Exception("label_dict and label can't be both at None")
    if label_dict is None:
        label_dict = decode_label(label)

    if label_dict["S_id"] % 2 == 0:
        return self.magnet_north
    else:
        return self.magnet_south
