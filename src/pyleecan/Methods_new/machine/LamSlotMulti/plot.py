from matplotlib.patches import Patch

from ....Functions_new.utils.init_fig import init_fig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.machine import Machine


def plot(
    self,
    fig: Figure | None = None,
    ax: Axes | None = None,
    is_lam_only: bool = False,
    sym: int = 1,
    alpha: float = 0,
    delta: complex = 0,
    is_edge_only: bool = False,
    edgecolor: str | None = None,
    is_add_arrow: bool = False,
    is_display: bool = True,
    is_show_fig: bool = True,
    is_clean_plot: bool = False,
    is_winding_connection: bool = False, machine: Machine | None = None,
) -> list | tuple[Figure, Axes]:
    """Plot the Lamination with empty Slots in a matplotlib fig

    Parameters
    ----------
    self : LamSlotMulti
        A LamSlotMulti object
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the data
    is_lam_only: bool
        True to plot only the lamination
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
    is_display : bool
        False to return the patches
    is_show_fig : bool
        To call show at the end of the method
    is_clean_plot : bool
        True to remove title, legend, axis (only machine on plot with white background)
    is_winding_connection : bool
        True to display winding connections (not used)
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    ax : Matplotlib.axes.Axes object
        Axis containing the plot
    """

    from ....Classes_new.machine.machine import Machine
    (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

    surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
    patches = list()
    for surf in surf_list:
        color, legend = Machine.get_color_legend_from_surface(surf, is_lam_only)

        if color is not None:
            patches.extend(
                surf.get_patches(
                    color=color,
                    is_edge_only=is_edge_only,
                    edgecolor=edgecolor,
                )
            )
        if not is_edge_only and legend is not None and legend not in label_leg:
            label_leg.append(legend)
            patch_leg.append(Patch(color=color))

    # Display the result
    if is_display:
        (fig, ax, patch_leg, label_leg) = init_fig(fig)
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        # Add the legend
        if not is_edge_only:
            if self.is_stator:
                ax.set_title("Stator with empty slot")
            else:
                ax.set_title("Rotor with empty slot")

            ax.legend(patch_leg, label_leg)
        # Clean figure
        if is_clean_plot:
            ax.set_axis_off()
            ax.axis("equal")
            if ax.get_legend() is not None:
                ax.get_legend().remove()
            ax.set_title("")
        if is_show_fig:
            fig.show()
        return fig, ax
    else:
        return patches
