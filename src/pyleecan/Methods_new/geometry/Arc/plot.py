import numpy as np
from ....Functions_new.utils.init_fig import init_fig
from ....Functions_new.Plot import TEXT_BOX
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure


def plot(
    self,
    fig: Figure | None = None,
    ax: Axes | None = None,
    linestyle: str = "solid",
    linewidth: int = 1,
    color: str = "black",
    label: str | None = None,
    offset_label: complex = 0,
    fontsize: int = 12,
) -> tuple[Figure, Axes]:
    """Plot the Arc

    Parameters
    ----------
    self : Arc
        An Arc object
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the data
    linestyle : str
        Line of the line (solid, dotted...)
    linewidth : int
        Line Width
    color : str
        Color of the line
    label : str
        To add a label at the middle of the line
    offset_label : complex
        Complex value to shift the label from the middle
    fontsize : int
        Size of the font for the label (if any)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure containing the plot
    ax : Matplotlib.axes.Axes object
        Axis containing the plot
    """

    # Init fig
    (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

    # Plot the line
    points = self.discretize(nb_point=10000)
    ax.plot(
        points.real, points.imag, linestyle=linestyle, linewidth=linewidth, color=color
    )

    # Add the label (if needed)
    if label is not None:
        Zmid = self.get_middle()
        ax.text(
            Zmid.real + offset_label.real,
            Zmid.imag + offset_label.imag,
            label,
            fontsize=fontsize,
            bbox=TEXT_BOX,
        )

    return fig, ax
