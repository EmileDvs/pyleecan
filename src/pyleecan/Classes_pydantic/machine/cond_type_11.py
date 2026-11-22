# Experimental pydantic model generated from Generator/ClassesRef/Machine/CondType11.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import TYPE_CHECKING, ClassVar

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
from pydantic import Field

from ...Functions_pydantic.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
    TEXT_BOX,
)
from ...Functions_pydantic.utils.init_fig import init_fig
from ..geometry.segment import Segment
from .conductor import Conductor

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from .lamination import Lamination
    from .winding import Winding


class CondType11(Conductor):
    """parallel stranded conductor consisting of at least a single rectangular wire

    Attributes
    ----------
    Hwire : float
        cf schematics, single strand height without insulation
        Unit: m; Default: 0.01; Minimum: 0
    Wwire : float
        cf schematics, single strand width without insulation
        Unit: m; Default: 0.01; Minimum: 0
    Nwppc_rad : int
        number of form wound strands in parallel per conductor along radial (vertical) direction
        Default: 1; Minimum: 1
    Nwppc_tan : int
        number of form wound strands in parallel per conductor along tangential (horizontal) direction
        Default: 1; Minimum: 1
    Wins_wire : float
        (advanced) cf schematics, winding strand insulation thickness
        Unit: m; Default: 0; Minimum: 0
    Wins_coil : float
        (advanced) cf schematics, winding coil insulation  thickness
        Unit: m; Default: 0; Minimum: 0
    type_winding_shape : int
        type of winding shape for end winding length calculation\n0 for hairpin windings\n1 for normal windings
        Default: 0; Minimum: 0; Maximum: 1
    alpha_ew : float
        angle of winding overhang hairpin coils [deg]
        Unit: deg; Default: 58; Minimum: 0; Maximum: 180
    """

    Hwire: float = Field(default=0.01, ge=0, json_schema_extra={"unit": "m"})
    """cf schematics, single strand height without insulation"""
    Wwire: float = Field(default=0.01, ge=0, json_schema_extra={"unit": "m"})
    """cf schematics, single strand width without insulation"""
    Nwppc_rad: int = Field(default=1, ge=1)
    """number of form wound strands in parallel per conductor along radial (vertical) direction"""
    Nwppc_tan: int = Field(default=1, ge=1)
    """number of form wound strands in parallel per conductor along tangential (horizontal) direction"""
    Wins_wire: float = Field(default=0, ge=0, json_schema_extra={"unit": "m"})
    """(advanced) cf schematics, winding strand insulation thickness"""
    Wins_coil: float = Field(default=0, ge=0, json_schema_extra={"unit": "m"})
    """(advanced) cf schematics, winding coil insulation  thickness"""
    type_winding_shape: int = Field(default=0, ge=0, le=1)
    """type of winding shape for end winding length calculation\\n0 for hairpin windings\\n1 for normal windings"""
    alpha_ew: float = Field(default=58, ge=0, le=180, json_schema_extra={"unit": "deg"})
    """angle of winding overhang hairpin coils [deg]"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.CondType11.comp_height
    def comp_height(self) -> float:
        """Compute the height of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        H: float
            Height of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Hwire) * self.Nwppc_rad

    # Inlined from Methods.Machine.CondType11.comp_height_wire
    def comp_height_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return wire height

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        H: float
            Height of the wire [m]

        """

        return self.Hwire

    # Inlined from Methods.Machine.CondType11.comp_nb_circumferential_wire
    def comp_nb_circumferential_wire(self) -> int:
        """Return number of adjacent wires in circumferential direction

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in circumferential direction

        """

        return self.Nwppc_tan

    # Inlined from Methods.Machine.CondType11.comp_nb_radial_wire
    def comp_nb_radial_wire(self) -> int:
        """Return number of adjacent wires in radial direction

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Nwppc_tan: int
            Number of adjacent wires in radial direction

        """

        return self.Nwppc_rad

    # Inlined from Methods.Machine.CondType11.comp_surface
    def comp_surface(self) -> float:
        """Compute the surface of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        S: float
            Surface of the conductor (with insulation) [m**2]

        """

        S = self.comp_height() * self.comp_width()

        return S

    # Inlined from Methods.Machine.CondType11.comp_surface_active
    def comp_surface_active(self) -> float:
        """Compute the active surface of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        Sact: float
            Surface without insulation [m**2]

        """

        Sact = self.Hwire * self.Wwire * self.Nwppc_tan * self.Nwppc_rad

        return Sact

    # Inlined from Methods.Machine.CondType11.comp_width
    def comp_width(self) -> float:
        """Compute the width of the conductor

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        W: float
            Width of the conductor [m]

        """

        return (2 * self.Wins_wire + self.Wwire) * self.Nwppc_tan

    # Inlined from Methods.Machine.CondType11.comp_width_wire
    def comp_width_wire(
        self, winding: Winding | None = None, lam: Lamination | None = None
    ) -> float:
        """Return wire width

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        winding : Winding, optional
            Winding holding the object (default: the parent)
        lam : Lamination, optional
            Lamination of the winding (default: the parent of the winding)

        Returns
        -------
        W: float
            Width of the wire [m]

        """

        return self.Wwire

    # Inlined from Methods.Machine.CondType11.is_round_wire
    def is_round_wire(self) -> bool:
        """Return if wire is round

        Parameters
        ----------
        self : CondType11
            A CondType11 object

        Returns
        -------
        is_round_wire: bool
            is_round_wire is always False since wire is rectangular

        """

        return False

    # Inlined from Methods.Machine.CondType11.plot
    def plot(
        self,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
    ) -> tuple[Figure, Axes]:
        """Plot a Conductor in a matplotlib fig

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        is_show_fig : bool
            To call show at the end of the method
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
        patches_list.append(Rectangle((0, 0), Wcond, Hcond, color=self.INS_COLOR))

        # Wire conductor
        for ii in range(self.Nwppc_tan):
            for jj in range(self.Nwppc_rad):
                # Computation of bottom left corner coodinates
                x = self.Wins_wire + ii * (self.Wwire + 2 * self.Wins_wire)
                y = self.Wins_wire + jj * (self.Hwire + 2 * self.Wins_wire)
                patches_list.append(
                    Rectangle((x, y), self.Wwire, self.Hwire, color=self.COND_COLOR)
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
        if self.Wins_wire > 0:
            patch_leg.append(Patch(color=self.INS_COLOR))
            label_leg.append("Wire insulation")

        patch_leg.append(Patch(color=self.COND_COLOR))
        label_leg.append("Active wire section")

        ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Machine.CondType11.plot_schematics
    def plot_schematics(
        self,
        is_default: bool = False,
        is_add_schematics: bool = True,
        is_add_main_line: bool = True,
        save_path: str | None = None,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
        is_single: bool = False,
    ) -> tuple[Figure, Axes]:
        """Plot the schematics of the slot

        Parameters
        ----------
        self : CondType11
            A CondType11 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
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

        # Use some default parameter
        if is_default and is_single:
            cond = type(self)(
                Hwire=10e-3, Wwire=22e-3, Wins_wire=2e-3, Nwppc_rad=1, Nwppc_tan=1
            )
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
                is_single=is_single,
            )
        elif is_default:
            cond = type(self)(
                Hwire=10e-3, Wwire=22e-3, Wins_wire=2e-3, Nwppc_rad=3, Nwppc_tan=2
            )
            return cond.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
            )
        else:
            # Getting the main plot
            fig, ax = self.plot(
                is_show_fig=False, fig=fig, ax=ax
            )  # center slot on Ox axis

            # Adding schematics
            if is_add_schematics:
                if is_single:
                    # Wwire
                    line = Segment(
                        begin=self.Wins_wire + 1j * (self.Wins_wire + self.Hwire / 2),
                        end=self.Wins_wire
                        + self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor width",
                        offset_label=-4 * self.Wins_wire - 1j * 2 * self.Wins_wire / 3,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Hwire
                    line = Segment(
                        begin=1j * (self.Wins_wire) + (self.Wins_wire + self.Wwire / 2),
                        end=1j * (self.Wins_wire + self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Conductor height",
                        offset_label=self.Wins_wire / 3 + 1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        begin=2 * self.Wins_wire
                        + 1j * (2 * self.Wins_wire + self.Hwire),
                        end=2 * self.Wins_wire + 1j * (self.Wins_wire + self.Hwire),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                else:
                    # Wwire
                    line = Segment(
                        begin=3 * self.Wins_wire
                        + self.Wwire
                        + 1j * (3 * self.Wins_wire + self.Hwire * 3 / 2),
                        end=3 * self.Wins_wire
                        + 2 * self.Wwire
                        + 1j * (3 * self.Wins_wire + self.Hwire * 3 / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand width",
                        offset_label=1j * self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Hwire
                    line = Segment(
                        begin=1j * (3 * self.Wins_wire + self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                        end=1j * (3 * self.Wins_wire + 2 * self.Hwire)
                        + (self.Wins_wire + self.Wwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Strand height",
                        offset_label=self.Wins_wire / 2,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Wins_wire
                    line = Segment(
                        begin=2 * self.Wins_wire
                        + self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                        end=3 * self.Wins_wire
                        + 1 * self.Wwire
                        + 1j * (self.Wins_wire + self.Hwire / 2),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=ARROW_COLOR,
                        linewidth=ARROW_WIDTH,
                        label="Insulator thickness",
                        offset_label=self.Wins_wire,
                        is_arrow=True,
                        fontsize=SC_FONT_SIZE,
                    )
                    # Nwppc_rad/tan
                    ax.text(
                        -self.Wins_wire,
                        5 * self.Wins_wire + 2.5 * self.Hwire,
                        "Strands in radial direction: 3\nStrands in tangential direction: 2",
                        fontsize=SC_FONT_SIZE,
                        bbox=TEXT_BOX,
                    )

            if is_add_main_line:
                for ii in range(1, self.Nwppc_tan):
                    line = Segment(
                        begin=ii * (self.Wwire + 2 * self.Wins_wire),
                        end=ii * (self.Wwire + 2 * self.Wins_wire)
                        + 1j * self.comp_height(),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )
                for ii in range(1, self.Nwppc_rad):
                    line = Segment(
                        begin=1j * ii * (self.Hwire + 2 * self.Wins_wire),
                        end=1j * ii * (self.Hwire + 2 * self.Wins_wire)
                        + self.comp_width(),
                    )
                    line.plot(
                        fig=fig,
                        ax=ax,
                        color=MAIN_LINE_COLOR,
                        linestyle=MAIN_LINE_STYLE,
                        linewidth=MAIN_LINE_WIDTH,
                    )

            # Zooming and cleaning
            W = self.comp_width() * 1.1
            H = self.comp_height() * 1.1

            ax.axis("equal")
            ax.set_xlim(-W * 0.1, W)
            ax.set_ylim(-H * 0.1, H)
            manager = plt.get_current_fig_manager()
            if manager is not None:
                manager.set_window_title(type(self).__name__ + " Schematics")
            ax.set_title("")
            ax.get_legend().remove()
            ax.set_axis_off()

            # Save / Show
            if save_path is not None:
                fig.savefig(save_path)
                plt.close(fig=fig)

            if is_show_fig:
                fig.show()
            return fig, ax
