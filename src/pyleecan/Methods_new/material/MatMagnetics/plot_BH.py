from ....Functions_new.utils.init_fig import init_fig
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def plot_BH(self, fig: Figure | None = None, grid: bool = True, color: str = "r", is_show_fig: bool = True) -> Figure:
    """Plot the curve B(H) at the specified frequency

    Parameters
    ----------
    self : MatMagnetics
        a MatMagnetics object
    fig :
        if None, open a new fig and plot, else add to the gcf (Default value = None)

    Returns
    -------
    None
    """
    (fig, axes, patch_leg, label_leg) = init_fig(fig)

    BH = self.get_BH()

    if BH is not None:
        axes.plot(BH[:, 0], BH[:, 1], color=color)
        axes.grid(visible=True)  # param "b" of grid was removed in MPL 3.7
        axes.set_xlabel("H [A/m]")
        axes.set_ylabel("B [T]")
        axes.set_title("B(H) curve")
        if is_show_fig:
            fig.show()

    return fig
