from ....Classes_new.geometry.circle import Circle
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
import numpy as np
from ....Functions_new.labels import SHAFT_LAB, NO_LAM_LAB, BOUNDARY_PROP_LAB, SHAFTSR_LAB, SHAFTSL_LAB, SHAFTR_LAB


def build_geometry(self, sym: int = 1, alpha: float = 0, delta: complex = 0) -> list:
    """Build the geometry of the shaft

    Parameters
    ----------
    self : Shaft
        Shaft Object
    sym : int
        Symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation

    Returns
    -------
    surf_list : list
        list of surfaces needed to draw the lamination

    """
    surf_list = list()

    if sym == 1:
        surf_list.append(
            Circle(
                radius=self.Drsh / 2,
                label=NO_LAM_LAB + "_" + SHAFT_LAB,
                center=0,
                point_ref=0,
            )
        )
    else:
        begin = self.Drsh / 2
        end = begin * np.exp(1j * 2 * np.pi / sym)
        surface = SurfLine(
            line_list=[
                Segment(begin=0, end=begin, prop_dict={BOUNDARY_PROP_LAB: SHAFTSR_LAB}),
                Arc1(
                    begin=begin, end=end, radius=self.Drsh / 2, prop_dict={BOUNDARY_PROP_LAB: SHAFTR_LAB}
                ),
                Segment(begin=end, end=0, prop_dict={BOUNDARY_PROP_LAB: SHAFTSL_LAB}),
            ],
            label=NO_LAM_LAB + "_" + SHAFT_LAB,
            point_ref=0,
        )

        surf_list.append(surface)
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)
    return surf_list
