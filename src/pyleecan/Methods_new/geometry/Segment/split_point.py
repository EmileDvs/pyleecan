import numpy as np

DELTA = 1e-9  # To remove computing noise


def split_point(self, Z1: complex, is_begin: bool = True):
    """Cut the Segment according to a point on the segment

    Parameters
    ----------
    self : Segment
        An Segment object
    Z1 : complex
        Cutting point on the line
    is_begin : bool
        True to keep the part begin=>Z1, False for the part Z1=>end

    Returns
    -------
    """

    if not self.is_on_line(Z1):
        raise Exception("Point is not on the line")

    if is_begin:
        self.end = Z1
    else:
        self.begin = Z1
