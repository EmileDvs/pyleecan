import numpy as np
from ....Classes_new.machine.lam_h import LamH


def comp_volumes(self) -> dict:
    """Compute the Lamination volumes

    Parameters
    ----------
    self : LamHoleNS
        A LamHoleNS object

    Returns
    -------
    V_dict: dict
        Lamination volume dictionary (Vlam, Vvent, Vmag, Vhole) [m**3]

    """

    V_dict = LamH.comp_volumes(self)

    # Magnets are counted twice (Zh = 2*p for both north and south)
    V_dict["Vmag"] = V_dict["Vmag"] / 2
    V_dict["Vhole"] = V_dict["Vhole"] / 2

    return V_dict
