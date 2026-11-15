import numpy as np


MAXSEG_default = 5


def comp_maxseg(self, elementsize: float, maxseg_amp: float) -> float:
    """
    Computes the number of segments per arc degrees in
    function of the elementsize of the region

    Parameters
    ----------
    self : Arc
        An Arc object
    elementsize : float
        max element size parameter
    maxseg_amp : float
        amplifying factor

    Returns
    -------
    maxseg : float
        number of segments per arc degrees
    """

    if elementsize == 0:
        # taking default maximum segment value
        maxseg = MAXSEG_default

    else:
        angle = self.get_angle(is_deg=True)
        begin = self.get_begin()
        end = self.get_end()

        if np.abs(angle) == 180:
            l_arc = np.pi * np.abs(begin - end) / 2
        elif np.abs(angle) == 90:
            l_arc = np.pi / 2 * np.abs(begin - end) / np.sqrt(2)
        else:
            l_arc = np.abs((begin - end) / (2 * np.sin(angle / 2 * np.pi / 180))) * np.abs(
                angle * np.pi / 180
            )

        n_seg = l_arc / elementsize

        maxseg = np.abs(min(MAXSEG_default, np.abs(angle / n_seg * maxseg_amp)))

    return maxseg
