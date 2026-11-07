# Experimental dataclass generated from Generator/ClassesRef/Machine/FrameBar.csv
"""Generated experimental dataclass; do not edit by hand."""

from copy import deepcopy
from dataclasses import dataclass

import numpy as np

from .arc_1 import Arc1
from .arc_2 import Arc2
from .frame import Frame
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class FrameBar(Frame):
    """machine frame with polar structural bars between frame and outer lamination

    Attributes
    ----------
    Nbar : int
        Number of bars
        Unit: m; Default: 8; Minimum: 1
    wbar : float
        Width of bars
        Unit: m; Default: 0.01; Minimum: 0
    """

    Nbar: int = 8
    """Number of bars"""
    wbar: float = 0.01
    """Width of bars"""

    # Inlined from Methods.Machine.FrameBar.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the Frame with structural Bars

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

        # Build Frame Geometry
        surf_list_frame = Frame.build_geometry(self, sym, alpha, delta)
        # Build Bar Geometry
        surf_list_bar = self.build_geometry_bar(sym, alpha, delta)

        surf_list = surf_list_frame + surf_list_bar
        return surf_list

    # Inlined from Methods.Machine.FrameBar.build_geometry_bar
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
        surf_list = []
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
            curve_list = []
            curve_list.append(Segment(Z1, Z2))
            curve_list.append(Arc1(Z2, Z3, self.Rint))
            curve_list.append(Segment(Z3, Z4))
            curve_list.append(Arc2(Z4, 0, angle=-rot_angle))
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

    # Inlined from Methods.Machine.FrameBar.comp_height_gap
    def comp_height_gap(self):
        """Computation of the Height of the gap between the Frame and Outer Lamination

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Hgap: float
            Height of the Gap [m]

        """
        lam_outer = self.parent.get_lam_list()[-1]

        return self.Rint - lam_outer.Rext

    # Inlined from Methods.Machine.FrameBar.comp_surface
    def comp_surface(self):
        """Compute the surface of the Frame including the structural bars

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sfra: float
            Surface of the Frame [m**2]

        """

        # Outer Frame Surface
        S_ext = (self.Rext**2) * np.pi
        S_int = (self.Rint**2) * np.pi
        S_outer = S_ext - S_int

        # Bar Surface
        S_bar = self.comp_surface_bar()

        return S_outer + S_bar

    # Inlined from Methods.Machine.FrameBar.comp_surface_bar
    def comp_surface_bar(self):
        """Compute the surface of the structural Bars

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sbar: float
            Surface of the structural Bars [m**2]

        """
        # #Calculation for rectangular shape
        # n_bar = self._get_Nbar()
        # w_bar = self._get_wbar()
        # h_gap = self.comp_height_gap()
        # Sbar = n_bar * w_bar * h_gap

        # Calculation for circular shape
        r_out = self._get_Rint()
        h_gap = self.comp_height_gap()
        r_in = r_out - h_gap
        rot_angle = 2 * np.arcsin(self.wbar / 2.0 / r_in)
        Sbar = self.Nbar * np.pi * (r_out**2 - r_in**2) * rot_angle / (2 * np.pi)

        return Sbar

    # Inlined from Methods.Machine.FrameBar.comp_surface_gap
    def comp_surface_gap(self):
        """Compute the surface of the Gap between the Frame and outer Lamination

        Parameters
        ----------
        self : FrameBar
            A FrameBar object

        Returns
        -------
        Sgap: float
            Surface of the Gap [m**2]

        """

        # Surface of the external disk
        S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        S_int = (self.Rint**2) * np.pi
        # Surface of the bars
        S_bar = self.comp_surface_bar()

        Sgap = S_ext - S_int - S_bar

        return Sgap
