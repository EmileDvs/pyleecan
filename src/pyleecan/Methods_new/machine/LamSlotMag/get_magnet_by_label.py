from ....Functions_new.utils.labels import decode_label
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.magnet import Magnet


def get_magnet_by_label(self, label: str | None = None, label_dict: dict | None = None) -> Magnet:
    """Return the magnet corresponding to the label

    Parameters
    ----------
    self : LamSlotMag
        A LamSlotMag object
    label : str
        A surface id (ex Rotor-0_Magnet_R0-T0-S0)
    label_dict : dict
        Split dict of the label (to avoid decoding twice)

    Returns
    -------
    mag : Magnet
        The corresponding magnet object
    """

    # Usual case, all magnets are the same
    if self.mur_lin_matrix is None and self.Brm20_matrix is None:
        return self.magnet

    # Decode the magnet label
    if label_dict is None and label is None:
        raise Exception("label_dict and label can't be both at None")
    if label_dict is None:
        label_dict = decode_label(label)

    # Find the correct magnet to return
    mag_list = self.get_all_mag_obj()
    if self.mur_lin_matrix is not None:
        mur = self.mur_lin_matrix[
            label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
        ]
        mur_list = [mag.mat_type.mag.mur_lin for mag in mag_list]
        return mag_list[mur_list.index(mur)]
    elif self.Brm20_matrix is not None:
        Brm20 = self.Brm20_matrix[
            label_dict["R_id"], label_dict["T_id"], label_dict["S_id"]
        ]
        Brm20_list = [mag.mat_type.mag.Brm20 for mag in mag_list]
        return mag_list[Brm20_list.index(Brm20)]
