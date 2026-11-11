# Experimental dataclass generated from Generator/ClassesRef/Machine/Frame.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass, field

import numpy as np
from matplotlib.patches import Patch

from ..definitions import config_dict
from ..Functions_new.init_fig import init_fig
from ._pyleecan_class import PyleecanClass
from .arc_1 import Arc1
from .circle import Circle
from .material import Material
from .segment import Segment
from .surf_line import SurfLine
from .surf_ring import SurfRing


@dataclass(eq=False)
class Frame(PyleecanClass):
    """machine frame

    Attributes
    ----------
    Lfra : float
        frame length [m]
        Unit: m; Default: 0.35; Minimum: 0
    Rint : float
        frame internal radius
        Unit: m; Default: 0.2; Minimum: 0
    Rext : float
        Frame external radius
        Unit: m; Default: 0.2; Minimum: 0
    mat_type : Material or None
        Frame material
        Default: Material()
    """

    FRAME_COLOR = config_dict["PLOT"]["COLOR_DICT"]["FRAME_COLOR"]
    Lfra: float = 0.35
    """frame length [m]"""
    Rint: float = 0.2
    """frame internal radius"""
    Rext: float = 0.2
    """Frame external radius"""
    mat_type: Material | None = field(
        default_factory=lambda: Material(), metadata={"default_class": "Material"}
    )
    """Frame material"""

    # Inlined from Methods.Machine.Frame.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
        """Build the geometry of the Frame

        Parameters
        ----------
        self : Frame
            Frame Object
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
        # If there is a frame...
        if self.comp_height_eq() != 0:
            if sym == 1:  # No symmetry / full frame
                out_surf = Circle(
                    radius=self.Rext,
                    label="Frame_Outter",
                    center=0,
                    point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                )
                in_surf = Circle(
                    radius=self.Rint, label="Frame_Inner", center=0, point_ref=0
                )
                surf_list = [
                    SurfRing(
                        out_surf=out_surf,
                        in_surf=in_surf,
                        label="Frame",
                        point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                    )
                ]
            else:  # Part of the frame
                Z0 = self.Rint
                Z3 = Z0 * np.exp(1j * 2 * np.pi / sym)
                Z1 = self.Rext
                Z2 = Z1 * np.exp(1j * 2 * np.pi / sym)
                curve_list = []
                curve_list.append(Segment(Z0, Z1))
                curve_list.append(Arc1(Z1, Z2, self.Rext))
                curve_list.append(Segment(Z2, Z3))
                curve_list.append(Arc1(Z3, Z0, -self.Rint, is_trigo_direction=False))
                surf_frame = SurfLine(
                    line_list=curve_list,
                    label="Frame",
                    point_ref=self.Rint + (self.Rext - self.Rint) / 2,
                )
                surf_list.append(surf_frame)

            # Apply the transformations
            for surf in surf_list:
                surf.rotate(alpha)
                surf.translate(delta)

        return surf_list

    # Inlined from Methods.Machine.Frame.comp_height_eq
    def comp_height_eq(self):
        """Computation of the Frame equivalent Height for the mechanical model

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Hfra: float
            Equivalent Height of the Frame [m]

        """

        return self.Rext - self.Rint

    # Inlined from Methods.Machine.Frame.comp_mass
    def comp_mass(self):
        """Compute the mass of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Mfra: float
            Mass of the Frame [kg]

        """

        Vfra = self.comp_volume()

        # Mass computation
        if Vfra == 0:
            return 0
        else:
            return Vfra * self.mat_type.struct.rho

    # Inlined from Methods.Machine.Frame.comp_surface
    def comp_surface(self):
        """Compute the surface of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Sfra: float
            Surface of the Frame [m**2]

        """

        # Surface of the external disk
        S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        S_int = (self.Rint**2) * np.pi

        return S_ext - S_int

    # Inlined from Methods.Machine.Frame.comp_volume
    def comp_volume(self):
        """Compute the volume of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        Vfra: float
            Volume of the Frame [m**3]

        """

        Sfra = self.comp_surface()
        if self.Lfra is None:
            return 0
        else:
            return Sfra * self.Lfra

    # Inlined from Methods.Machine.Frame.get_length
    def get_length(self):
        """Return the length of the Frame

        Parameters
        ----------
        self : Frame
            A Frame object

        Returns
        -------
        length: float
            Length of the frame

        """

        if self.comp_height_eq() > 0:
            return self.Lfra
        else:
            return 0

    # Inlined from Methods.Machine.Frame.plot
    def plot(
        self,
        fig=None,
        ax=None,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_show_fig=True,
    ):
        """Plot the Frame in a matplotlib fig

        Parameters
        ----------
        self : Frame
            A Frame object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        sym : int
            Symmetry factor (1= plot full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_show_fig : bool
            To call show at the end of the method

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # plot only if the frame has a height >0
        if self.comp_height_eq() != 0:
            (fig, ax, patch_leg, label_leg) = init_fig(
                fig=fig, ax=ax, shape="rectangle"
            )
            surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
            patches = []
            for surf in surf_list:
                patches.extend(
                    surf.get_patches(
                        color=self.FRAME_COLOR,
                        is_edge_only=is_edge_only,
                        edgecolor=edgecolor,
                    )
                )

            ax.set_xlabel("(m)")
            ax.set_ylabel("(m)")
            ax.set_title("Frame")
            for patch in patches:
                ax.add_patch(patch)
            ax.axis("equal")

            # The Lamination is centered in the figure
            Lim = self.Rext * 1.1
            ax.set_xlim(-Lim, Lim, auto=True)
            ax.set_ylim(-Lim, Lim, auto=True)

            if not is_edge_only:
                patch_leg.append(Patch(color=self.FRAME_COLOR))
                label_leg.append("Frame")
                ax.legend(patch_leg, label_leg)
            if is_show_fig:
                fig.show()
            return fig, ax
