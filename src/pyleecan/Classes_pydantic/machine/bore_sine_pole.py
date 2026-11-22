# Experimental pydantic model generated from Generator/ClassesRef/Machine/BoreSinePole.csv
"""Generated experimental pydantic model; do not edit by hand."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

import matplotlib.pyplot as plt
import numpy as np
from pydantic import Field
from scipy.optimize import fmin

from ...classes_common.errors import ParentMissingError
from ...classes_common.logger_context import get_logger
from ...classes_common.parents import container_or_parent
from ...definitions import config_dict
from ...Functions_pydantic.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    SC_FONT_SIZE,
)
from ..geometry.arc_1 import Arc1
from ..geometry.segment import Segment
from .bore import Bore
from .lamination import Lamination

if TYPE_CHECKING:
    from typing import Any

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure

    from .lamination import Lamination


class BoreSinePole(Bore):
    """Class for Sine Field Pole Bore shape adapted from 'Muller, Germar, et al. Berechnung Elektrischer Maschinen. Hoboken, NJ, United States, Wiley, 2008.'

    Attributes
    ----------
    N : int
        Number of Poles
        Default: 8; Minimum: 0
    k : float
        pole width modifier
        Default: 1; Minimum: 0
    delta_d : float
        d-axis air gap width
        Unit: m; Default: 0.001; Minimum: 0
    delta_q : float or None
        q-axis air gap width
        Unit: m; Default: None; Minimum: 0
    W0 : float or None
        Width of the pole
        Unit: m; Default: None; Minimum: 0
    """

    MAGNET_COLOR: ClassVar = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    N: int = Field(default=8, ge=0)
    """Number of Poles"""
    k: float = Field(default=1, ge=0)
    """pole width modifier"""
    delta_d: float = Field(default=0.001, ge=0, json_schema_extra={"unit": "m"})
    """d-axis air gap width"""
    delta_q: float | None = Field(default=None, ge=0, json_schema_extra={"unit": "m"})
    """q-axis air gap width"""
    W0: float | None = Field(default=None, ge=0, json_schema_extra={"unit": "m"})
    """Width of the pole"""

    _package: ClassVar[str] = "Machine"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Machine.BoreSinePole.comp_periodicity_spatial
    def comp_periodicity_spatial(self) -> tuple[int | None, bool]:
        """Compute the periodicity factor of the Bore

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the bore
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        return self.N, False

    # Inlined from Methods.Machine.BoreSinePole.get_bore_line
    def get_bore_line(
        self, prop_dict: dict | None = None, lam: Lamination | None = None, *, NN=30
    ) -> list:
        """Return the bore line description
        adapted sine field pole geometry from the text book:
        "Müller, Germar, et al. Berechnung Elektrischer Maschinen. Hoboken, NJ, United States, Wiley, 2008."
        ("Calculation of electric machines")

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
        prop_dict : dict
            Property dictionary to apply on the lines
        lam : Lamination, optional
            Lamination holding the bore (default: the parent)

        Returns
        -------
        bore_list : list
            List of bore lines
        """
        lam = container_or_parent(self, lam, "lam")

        if lam is not None:
            Rbo = lam.get_Rbo()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

        logger = get_logger(self)

        # Compute the shape
        alpha1 = np.pi / self.N  # Half bore pitch [rad]

        # Checking max width and W0
        w_max = self._get_pole_width_max(self)  # [m]
        if self.W0 is not None and self.W0 < w_max:
            w_max = self.W0
        elif self.W0 is not None and self.W0 > w_max:
            logger.warning("Enforcing permissible pole width (W0).")

        phi_max = self._get_phi(self, w_max)
        phi = np.linspace(-phi_max, phi_max, 2 * NN + 1)

        Zedge = self.get_pole_shape(-phi_max, lam=lam)
        xedge = (Zedge * np.exp(1j * alpha1)).real
        Rq = Rbo + self.delta_d - self.delta_q

        # Create the first pole bore line
        Z = [self.get_pole_shape(p, lam=lam) for p in phi]

        if self.delta_q is not None and Rq < xedge:
            line = Segment(
                begin=Zedge * np.exp(1j * alpha1),
                end=1j * Zedge.imag * np.exp(1j * alpha1),
            )
            inter = line.intersect_line(Rq, Rq + 1j * Rq)
            if len(inter) != 1:
                raise ValueError(
                    f"BoreSinePole: {len(inter)} q axis intersections, 1 expected"
                )

            if inter[0].imag <= 0:
                inter = line.intersect_line(0, Rq)
                if len(inter) != 1:
                    raise ValueError(
                        f"BoreSinePole: {len(inter)} q axis intersections, 1 expected"
                    )

                logger.warning("Enforcing permissible q axis air gap (delta_q).")
                Z.insert(0, inter[0] * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())

            else:
                Z.insert(0, inter[0] * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())
                Z.insert(0, Rq * np.exp(-1j * alpha1))
                Z.append(Z[0].conjugate())

        else:
            Z.append(xedge * np.exp(1j * alpha1))
            Z.insert(0, Z[-1].conjugate())

        # Create the lines
        bore_list = []
        for ii in range(self.N):
            for jj in range(len(Z) - 1):
                bore_list.append(
                    Segment(
                        begin=Z[jj]
                        * np.exp(1j * (2 * alpha1 * (ii - 1 / 2) + self.alpha)),
                        end=Z[jj + 1]
                        * np.exp(1j * (2 * alpha1 * (ii - 1 / 2) + self.alpha)),
                        prop_dict=prop_dict,
                    )
                )

        return bore_list

    @staticmethod
    def _get_phi(obj: BoreSinePole, w) -> float:
        """Return the angle of the pole width

        Parameters
        ----------
        obj : BoreSinePole
            a BoreSinePole object

        Returns
        -------
        phi : float
            angle of the pole width [rad]
        """
        phi_max = BoreSinePole._get_phi_max(obj)
        phi = fmin(
            lambda x: abs(obj.get_pole_shape(x).imag - w / 2) + max(x - phi_max, 0),
            0,
            disp=False,
        )[0]
        return phi

    @staticmethod
    def _get_phi_max(obj):
        """ "Internal method to get max. pole angle."""
        phi_max = fmin(lambda x: -obj.get_pole_shape(x).imag, 0, disp=False)[0]
        return min(np.pi / 2, phi_max)

    @staticmethod
    def _get_pole_width_max(obj: BoreSinePole) -> float:
        """Return the max. pole width and the angle of the max. pole width

        Parameters
        ----------
        obj : BoreSinePole
            a BoreSinePole object

        Returns
        -------
        w_max : float
            max. pole width [m]
        """
        phi_max = BoreSinePole._get_phi_max(obj)
        w_max = 2 * obj.get_pole_shape(phi_max).imag

        return w_max

    # Inlined from Methods.Machine.BoreSinePole.get_pole_shape
    def get_pole_shape(self, phi: float, lam: Lamination | None = None) -> complex:
        """Return the complex coordinates of the point at phi

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
        phi : float
            Angle where to compute the point [rad]
        lam : Lamination, optional
            Lamination holding the bore (default: the parent)

        Returns
        -------
        Z : complex
            Coordinates of the requested point
        """
        lam = container_or_parent(self, lam, "lam")

        if lam is not None:
            Rbo = lam.get_Rbo()
        else:
            raise ParentMissingError("Error: The slot is not inside a Lamination")

        # limit phi to valid values
        phi_max = np.arccos(self.delta_d / (self.delta_d + Rbo)) / self.k
        phi = max(-phi_max, phi)
        phi = min(phi_max, phi)

        # compute the point on the bore radius arc
        delta = self.delta_d / np.cos(phi * self.k)
        r = Rbo + self.delta_d - delta
        x = r * np.cos(2 * phi / self.N)
        y = r * np.sin(2 * phi / self.N)

        return x + 1j * y

    # Inlined from Methods.Machine.BoreSinePole.plot_schematics
    def plot_schematics(
        self,
        is_default: bool = False,
        is_add_schematics: bool = True,
        is_add_main_line: bool = True,
        save_path: str | None = None,
        is_show_fig: bool = True,
        fig: Figure | None = None,
        ax: Axes | None = None,
        lam: Lamination | None = None,
    ) -> tuple[Figure, Axes]:
        """Plot the schematics of the slot

        Parameters
        ----------
        self : BoreSinePole
            A BoreSinePole object
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
        lam : Lamination, optional
            Lamination holding the bore (default: the parent)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        """
        lam = container_or_parent(self, lam, "lam")

        # Use some default parameter
        if is_default:
            bore = type(self)(N=8, delta_d=10e-3, delta_q=50e-3, W0=165e-3, alpha=0)
            lam = Lamination(
                Rint=0.135, Rext=0.3, is_internal=True, is_stator=False, bore=bore
            )
            return bore.plot_schematics(
                is_default=False,
                is_add_schematics=is_add_schematics,
                is_add_main_line=is_add_main_line,
                save_path=save_path,
                is_show_fig=is_show_fig,
                fig=fig,
                ax=ax,
                lam=lam,
            )
        else:
            # Getting the main plot
            if lam is None:
                raise ParentMissingError("Error: The bore is not inside a Lamination")
            fig, ax = lam.plot(is_show_fig=False, fig=fig, ax=ax)

            # Comp point coordinates
            lines = self.get_bore_line(lam=lam)
            Zq1 = lines[0].get_end()
            Zq2 = lines[-1].get_begin()
            Rbo = lam.get_Rbo()
            alpha = np.pi / self.N
            # H = self.Rarc / 8  # Small distance for label placement

            # Adding schematics
            if is_add_schematics:
                # delta_q
                p1 = Rbo + self.delta_d - self.delta_q
                p2 = Rbo + self.delta_d
                line = Segment(
                    begin=p1 * np.exp(2j * alpha), end=p2 * np.exp(2j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="delta_q",
                    offset_label=self.delta_q / 2,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # W0
                line = Segment(
                    begin=Zq1 * np.exp(2 * 1j * alpha), end=Zq2 * np.exp(4 * 1j * alpha)
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W0",
                    offset_label=0,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )
                # Rbo + delta_d
                line = Segment(begin=0, end=Rbo + self.delta_d)
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="Rbo + delta_d",
                    offset_label=-Rbo / 4,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

            if is_add_main_line:
                plot_args: dict[str, Any] = dict(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                # Ox axis
                # line = Segment(0, lam.Rext * 1.5)
                # line.plot(**plot_args)
                # Rarc
                # line = Segment(Zc, Z1)
                # line.plot(
                #     fig=fig,
                #     ax=ax,
                #     color=MAIN_LINE_COLOR,
                #     linestyle=MAIN_LINE_STYLE,
                #     linewidth=MAIN_LINE_WIDTH,
                # )
                # line = Segment(Zc, Z2)
                # line.plot(
                #     fig=fig,
                #     ax=ax,
                #     color=MAIN_LINE_COLOR,
                #     linestyle=MAIN_LINE_STYLE,
                #     linewidth=MAIN_LINE_WIDTH,
                # )
                # Machine center
                line = Segment(begin=0, end=Rbo * np.exp(1j * alpha))
                line.plot(**plot_args)
                # Rbo circle arc
                Z1 = Rbo * np.exp(-1j * np.pi / 2)
                Z2 = Rbo * np.exp(1j * np.pi / 2)
                line = Arc1(begin=Z1, end=Z2, radius=Rbo, is_trigo_direction=True)
                line.plot(**plot_args)
                line = Arc1(begin=Z2, end=Z1, radius=Rbo, is_trigo_direction=True)
                line.plot(**plot_args)
                # Rbo + delta_d circle arc
                R = Rbo + self.delta_d
                Z1 = R * np.exp(-1j * np.pi / 2)
                Z2 = R * np.exp(1j * np.pi / 2)
                line = Arc1(begin=Z1, end=Z2, radius=R, is_trigo_direction=True)
                line.plot(**plot_args)
                line = Arc1(begin=Z2, end=Z1, radius=R, is_trigo_direction=True)
                line.plot(**plot_args)

            # Zooming and cleaning

            ax.axis("equal")
            ax.set_xlim(0, Rbo)
            ax.set_ylim(-Rbo / 10, Rbo * 1.1)
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
