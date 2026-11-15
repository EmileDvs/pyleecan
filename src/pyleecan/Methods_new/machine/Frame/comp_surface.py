# -*- coding: utf-8 -*-

import numpy as np


def comp_surface(self):
    """Compute the surface of the Frame

    Parameters
    ----------
    self : Frame
        A Frame object

    Returns
    -------
    Sfra: float
        Surface of the Frame [m**2]

    """

    # Surface of the external disk
    S_ext = (self.Rext**2) * np.pi
    # Surface of the internal disk
    S_int = (self.Rint**2) * np.pi

    return S_ext - S_int
