from ....Classes_new.geometry.surf_line import SurfLine
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.surface import Surface


def get_surface(self) -> Surface:
    """Returns the bore shape as a Surface object

    Parameters
    ----------
    self : Bore
        A Bore object

    Returns
    -------
    Sbore : Surface
        Surface object to draw the bore
    """

    line_list = self.get_bore_line()

    return SurfLine(line_list=line_list, point_ref=0, label="Bore")
