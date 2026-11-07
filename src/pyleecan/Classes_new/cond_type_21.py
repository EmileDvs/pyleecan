# Experimental dataclass generated from Generator/ClassesRef/Machine/CondType21.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from matplotlib.patches import Patch, Rectangle

from ..Functions.init_fig import init_fig
from .conductor import Conductor


@dataclass(eq=False)
class CondType21(Conductor):
    """single rectangular conductor \nhas to be used for LamSquirrelCages's conductor

    Attributes
    ----------
    Hbar : float
        Bar height
        Unit: m; Default: 0.01; Minimum: 0
    Wbar : float
        Bar width
        Unit: m; Default: 0.01; Minimum: 0
    Wins : float
        Width of insulation
        Unit: m; Default: 0; Minimum: 0
    """

    Hbar: float = 0.01
    """Bar height"""
    Wbar: float = 0.01
    """Bar width"""
    Wins: float = 0
    """Width of insulation"""

    # Inlined from Methods.Machine.CondType21.comp_height
    def comp_height(self):
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        H: float
            Height of the conductor (with insulation) [m]

        """

        return self.Hbar + 2 * self.Wins

    # Inlined from Methods.Machine.CondType21.comp_height_wire
    def comp_height_wire(self):
        """Return bar height

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        H: float
            Height of the bar [m]

        """

        return self.Hbar

    # Inlined from Methods.Machine.CondType21.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self):
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return 1

    # Inlined from Methods.Machine.CondType21.comp_nb_radial_wire
    def comp_nb_radial_wire(self):
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return 1

    # Inlined from Methods.Machine.CondType21.comp_surface
    def comp_surface(self):
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        S = self.comp_height() * self.comp_width()

        return S

    # Inlined from Methods.Machine.CondType21.comp_surface_active
    def comp_surface_active(self):
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = self.Hbar * self.Wbar

        return Sact

    # Inlined from Methods.Machine.CondType21.comp_width
    def comp_width(self):
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        W: float
            Width of the conductor (with insulation) [m]

        """

        return self.Wbar + 2 * self.Wins

    # Inlined from Methods.Machine.CondType21.comp_width_wire
    def comp_width_wire(self):
        """Return bar width

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        W: float
            Width of the bar [m]

        """

        return self.Wbar

    # Inlined from Methods.Machine.CondType21.is_round_wire
    def is_round_wire(self):
        """Return if wire is round

        Parameters
        ----------
        self : CondType21
            A CondType21 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always False since bar is rectangular

        """

        return False

    # Inlined from Methods.Machine.CondType21.plot
    def plot(self, fig=None, ax=None):
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType21
            A CondType21 object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        patches_list = []

        # Conductor insulation
        Wcond = self.comp_width()
        Hcond = self.comp_height()
        patches_list.append(Rectangle((0, 0), Wcond, Hcond, color="g"))

        # Conductor
        patches_list.append(
            Rectangle((self.Wins, self.Wins), self.Wbar, self.Hbar, color="r")
        )

        # Display
        (fig, ax, _, _) = init_fig(fig=fig, ax=ax)
        for patch in patches_list:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The conductor is centered
        ax.set_xlim(0 - Wcond / 10, Wcond * 11.0 / 10.0)
        ax.set_ylim(0 - Hcond / 10, Hcond * 11.0 / 10.0)

        # Legend
        patch_leg = []  # Symbol
        label_leg = []  # Text
        if self.Wins > 0:
            patch_leg.append(Patch(color="g"))
            label_leg.append("Conductor insulation")
        patch_leg.append(Patch(color="r"))
        label_leg.append("Active bar section")

        ax.legend(patch_leg, label_leg)
        fig.show()
        return fig, ax
