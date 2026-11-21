import numpy as np

from ....Functions_new.utils.geometry import inter_line_circle


def intersect_line(self, Z1, Z2) -> list:
    """Return a list (0, 1 or 2 complex) of coordinates of the
    intersection of the arc with a line defined by two complex

    Parameters
    ----------
    self : Arc
        An Arc object

    Returns
    -------
    Z_list: list
        Complex coordinates of the intersection (if any)
    """

    Zc = self.get_center()
    R = self.comp_radius()

    # Get intersetion between line and the full circle
    Zlist = inter_line_circle(Z1=Z1, Z2=Z2, R=R, Zc=Zc)

    # Keep only the points actually on the arc
    Zlist = [Z for Z in Zlist if self.is_on_line(Z)]

    # Order the intersection points (begin=>intersect1=>intersection2=>end)
    if len(Zlist) == 2:
        begin = self.get_begin()
        if np.abs(Zlist[0] - begin) < 1e-6:
            # First point is begin
            return Zlist
        if np.abs(Zlist[1] - begin) < 1e-6:
            # Second point is begin
            return Zlist[::-1]

        # Go to the coordinate system Zc as center, begin on X > 0 axis
        Z1 = (Zlist[0] - Zc) * np.exp(-1j * np.angle(begin - Zc))
        Z2 = (Zlist[1] - Zc) * np.exp(-1j * np.angle(begin - Zc))

        alpha = self.get_angle()
        A1 = np.angle(Z1) % (2 * np.pi)
        A2 = np.angle(Z2) % (2 * np.pi)
        # Check if Zlist needs to be reversed
        if alpha > 0 and A1 > A2:
            return Zlist[::-1]
        if alpha < 0 and A2 > A1:
            return Zlist[::-1]
    return Zlist
