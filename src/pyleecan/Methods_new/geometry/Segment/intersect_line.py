import numpy as np

from ....Functions_new.utils.geometry import inter_line_line


def intersect_line(self, Z1, Z2) -> list:
    """Return a list (0, 1 or 2 complex) of coordinates of the
    intersection of the segment with a line defined by two complex

    Parameters
    ----------
    self : Segment
        A Segment object

    Returns
    -------
    Z_list: list
        Complex coordinates of the intersection (if any,
        return [begin, end] if the segment is part of the line)
    """

    Z3 = self.begin
    Z4 = self.end

    Z_list = inter_line_line(Z1, Z2, Z3, Z4)
    if len(Z_list) == 0:
        # No intersection
        return []
    elif len(Z_list) == 1:
        # One intersect. Is it between begin and end or not ?
        Z_int = Z_list[0]
        Seg_len = self.comp_length()
        if np.abs(Z_int - Z3) <= Seg_len and np.abs(Z_int - Z4) <= Seg_len:
            return [Z_int]
        elif np.abs(Z_int - Z3) <= 1e-6 or np.abs(Z_int - Z4) <= 1e-6:
            # Zint is begin or end
            return [Z_int]
        else:
            return []
    elif len(Z_list) == 2:
        # The segment is on the line
        return [Z3, Z4]
