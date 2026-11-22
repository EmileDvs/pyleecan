from ....Functions_new.utils.init_fig import init_fig
from ....definitions import config_dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.lamination import Lamination

ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]


def plot(self, fig: Figure | None = None, ax: Axes | None = None, lam: Lamination | None = None) -> tuple[Figure, Axes]:
    """Plot the Bore in a matplotlib fig

    Parameters
    ----------
    self : Bore
        A Bore object
    fig :
        if None, open a new fig and plot, else add to the current
        one (Default value = None)
    lam : Lamination, optional
        Lamination holding the bore (default: the parent)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    ax : Matplotlib.axes.Axes object
        Axis containing the plot
    """
    surf = self.get_surface(lam=lam)

    # Display the result
    (fig, ax, patch_leg, label_leg) = init_fig(fig, ax)
    ax.set_xlabel("(m)")
    ax.set_ylabel("(m)")
    ax.set_title("Bore")

    # Add the Bore to the fig
    if self.get_is_stator:
        patches = surf.get_patches(color=STATOR_COLOR)
    else:
        patches = surf.get_patch(color=ROTOR_COLOR)
    for patch in patches:
        ax.add_patch(patch)

    # Axis Setup
    ax.axis("equal")
    fig.show()
    return fig, ax
