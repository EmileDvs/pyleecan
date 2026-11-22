from ....Functions_new.utils.init_fig import init_fig
from ....definitions import config_dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch

ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]


def plot(self, fig: Figure | None = None, ax: Axes | None = None, is_show_fig: bool = True, lam: Lamination | Notch | None = None) -> tuple[Figure, Axes]:
    """Plot the Slot in a matplotlib fig

    Parameters
    ----------
    self : Slot
        A Slot object
    fig :
        if None, open a new fig and plot, else add to the current
        one (Default value = None)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

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
    ax.set_xlabel("[m]")
    ax.set_ylabel("[m]")
    ax.set_title("Slot")

    # Add the slot to the fig
    if self.get_is_stator:
        patches = surf.get_patches(color=STATOR_COLOR)
    else:
        patches = surf.get_patch(color=ROTOR_COLOR)
    for patch in patches:
        ax.add_patch(patch)

    # Axis Setup
    ax.axis("equal")
    if is_show_fig:
        fig.show()
    return fig, ax
