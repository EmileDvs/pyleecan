# -*- coding: utf-8 -*-
from ....Classes_new.geometry.circle import Circle
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.arc_2 import Arc2
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.surf_line import SurfLine
from ....Classes_new.geometry.surf_ring import SurfRing
import numpy as np
from copy import deepcopy


def build_geometry_bar(self, sym=1, alpha=0, delta=0):
    """Build the geometry of the structural bars

    Parameters
    ----------
    self : FrameBar
        FrameBar Object
    sym : int
        symmetry factor (1= full machine, 2= half of the machine...)
    alpha : float
        Angle for rotation [rad]
    delta : complex
        Complex value for translation

    Returns
    -------
    surf_list : list
        list of surface

    """
    surf_list = list()
    h_gap = self.comp_height_gap()
    if h_gap > 0:
        lam_outer = self.parent.get_lam_list()[-1]
        ###Rectangular Shape
        # #Define Points
        # Z0 = lam_outer.Rext
        # Z1 = Z0 + self.wbar * 1j / 2.0
        # Z2 = Z1 + h_gap
        # Z3 = Z2 - self.wbar * 1j
        # Z4 = Z0 - self.wbar * 1j / 2.0
        # #Define Lines
        # curve_list = list()
        # curve_list.append(Segment(Z1, Z2))
        # curve_list.append(Segment(Z2, Z3))
        # curve_list.append(Segment(Z3, Z4))
        # curve_list.append(Segment(Z4, Z1))

        ###Circular Shape
        # Define Points
        Z0 = lam_outer.Rext
        rot_angle = np.arcsin(self.wbar / 2.0 / Z0)
        Z1 = Z0 * np.exp(rot_angle * -1j)
        Z2 = (Z0 + h_gap) * np.exp(rot_angle * -1j)
        Z3 = (Z0 + h_gap) * np.exp(rot_angle * 1j)
        Z4 = Z0 * np.exp(rot_angle * 1j)
        # Define Lines
        curve_list = list()
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(Arc1(begin=Z2, end=Z3, radius=self.Rint))
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(Arc2(begin=Z4, center=0, angle=-rot_angle))
        # Define Surface
        surf_bar = SurfLine(
            line_list=curve_list,
            label="Bar",
            point_ref=self.Rext - h_gap / 2,
        )
        # Rotate surface so bars are evenly distributed
        surf_list.append(deepcopy(surf_bar))
        bar_angle = 2 * np.pi / self.Nbar
        for i in range(1, self.Nbar):
            surf_bar.rotate(bar_angle)
            surf_list.append(deepcopy(surf_bar))

    # Apply the transformations
    for surf in surf_list:
        surf.rotate(alpha)
        surf.translate(delta)

    return surf_list
