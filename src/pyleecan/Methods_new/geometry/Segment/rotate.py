# -*- coding: utf-8 -*-
import numpy as np
from . import AngleRotationSegmentError


def rotate(self, angle):
    """Rotation of the Segment of angle

    Parameters
    ----------
    self : Segment
        An Segment Object

    angle : float
        the angle of rotation [rad]

    Returns
    -------
    None

    """
    if not isinstance(angle, float) and not isinstance(angle, int):
        raise AngleRotationSegmentError("The angle must be a float or int ")

    # check if Segment is correct"
    self.check()

    # Modification from the rotation of the object
    self.begin = self.begin * np.exp(1j * angle)
    self.end = self.end * np.exp(1j * angle)
