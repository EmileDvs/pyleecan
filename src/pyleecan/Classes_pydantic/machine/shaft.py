# Experimental pydantic model generated from Generator/ClassesRef/Machine/Shaft.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np
from matplotlib.patches import Patch
from pydantic import Field

from ...definitions import config_dict
from ...Functions_new.init_fig import init_fig
from ...Functions_new.labels import (
    BOUNDARY_PROP_LAB,
    NO_LAM_LAB,
    SHAFT_LAB,
    SHAFTR_LAB,
    SHAFTSL_LAB,
    SHAFTSR_LAB,
)
from .._legacy_model import LegacyModel
from ..geometry.arc_1 import Arc1
from ..geometry.circle import Circle
from ..geometry.segment import Segment
from ..geometry.surf_line import SurfLine
from ..material.material import Material


class Shaft(LegacyModel):
    """machine shaft

    Attributes
    ----------
    Lshaft : float
        length of the rotor shaft [m] (used for weight & cost estimation only)
        Unit: m; Default: 0.442; Minimum: 0
    mat_type : Material or None
        Shaft's Material
        Default: Material()
    Drsh : float
        diameter of the rotor shaft [m], used to estimate bearing diameter for friction losses
        Unit: m; Default: 0.045; Minimum: 0
    """

    SHAFT_COLOR: ClassVar = config_dict["PLOT"]["COLOR_DICT"]["SHAFT_COLOR"]

    Lshaft: float = Field(default=0.442, ge=0, json_schema_extra={"unit": "m"})
    """length of the rotor shaft [m] (used for weight & cost estimation only)"""
    mat_type: Material | None = Field(default_factory=lambda: Material())
    """Shaft's Material"""
    Drsh: float = Field(default=0.045, ge=0, json_schema_extra={"unit": "m"})
    """diameter of the rotor shaft [m], used to estimate bearing diameter for friction losses"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.Shaft.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0):
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
        surf_list = []

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
                    Segment(
                        begin=0, end=begin, prop_dict={BOUNDARY_PROP_LAB: SHAFTSR_LAB}
                    ),
                    Arc1(
                        begin=begin,
                        end=end,
                        radius=self.Drsh / 2,
                        prop_dict={BOUNDARY_PROP_LAB: SHAFTR_LAB},
                    ),
                    Segment(
                        begin=end, end=0, prop_dict={BOUNDARY_PROP_LAB: SHAFTSL_LAB}
                    ),
                ],
                label=NO_LAM_LAB + "_" + SHAFT_LAB,
                point_ref=0,
            )

            surf_list.append(surface)
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)
        return surf_list

    # Inlined from Methods.Machine.Shaft.comp_mass
    def comp_mass(self):
        """Computation of the Shaft mass

        Parameters
        ----------
        self: Shaft
            A Shaft object
        Returns
        -------
        M_shaft: float
            Mass of the Shaft [kg]

        """
        if self.Lshaft is None:
            return 0
        else:
            return (
                self.Lshaft * np.pi * ((self.Drsh / 2) ** 2) * self.mat_type.struct.rho
            )

    # Inlined from Methods.Machine.Shaft.plot
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
        """Plot the Shaft in a matplotlib fig

        Parameters
        ----------
        self : Shaft
            A Shaft object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
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

        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")
        # Get the shaft surface(s)
        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = []
        for surf in surf_list:
            patches.extend(
                surf.get_patches(
                    color=self.SHAFT_COLOR,
                    is_edge_only=is_edge_only,
                    edgecolor=edgecolor,
                )
            )
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        ax.set_title("Shaft")
        for patch in patches:
            ax.add_patch(patch)
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Drsh * 0.6
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Add legend
        if not is_edge_only:
            patch_leg.append(Patch(color=self.SHAFT_COLOR))
            label_leg.append("Shaft")

            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax
