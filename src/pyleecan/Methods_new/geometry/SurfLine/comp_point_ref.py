import numpy as np


def comp_point_ref(self, is_set=False):
    """Compute the point ref of the Surface

    Parameters
    ----------
    self : SurfLine
        A SurfLine object
    is_set: bool
        True to update the point_ref property

    Returns
    -------
    point_ref : complex
        the reference point of the surface
    """

    middle_array = np.array([line.get_middle() for line in self.get_lines()])
    point_ref = np.sum(middle_array) / middle_array.size

    # Use another method if the point is not is the surface
    if not self.is_inside(Z=point_ref, if_online=False):
        middle_array_abs = abs(middle_array)
        # Find "min abs" middle
        mid_id = np.argmin(middle_array_abs)
        Zmid = middle_array[mid_id]
        H = np.max(middle_array_abs) - np.min(middle_array_abs)

        point_ref = (abs(Zmid) + H / 100) * np.exp(1j * np.angle(Zmid))

    if is_set:
        self.point_ref = point_ref
    return point_ref
