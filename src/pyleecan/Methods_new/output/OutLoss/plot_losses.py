from ....classes_common.parents import container_or_parent
import numpy as np

from ....Functions_new.SciDataTool.Plot.plot_2d import plot_2D
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.output.output import Output


def plot_losses(self, N0_array: np.ndarray | None = None, save_path: str | None = None, is_show_fig: bool = True, output: Output | None = None) -> None:
    """Plot the losses as a fct of speed

    Parameters
    ----------
    self : OutLoss
        An OutLoss object
    N0_array : ndarray
        speed array to use as X axis [rpm]
    save_path : str
        full path including folder, name and extension of the file to save if save_path is not None
    is_show_fig : bool
        True to show figure after plot
    output : Output, optional
        Output of the simulation holding the object (default: the parent)
    """
    output = container_or_parent(self, output, "output")

    if N0_array is None:
        N0_array = np.linspace(10, 8000, 100)
    if output is None:
        raise Exception("Error: OutLoss is not in Output object")

    p = output.simu.machine.get_pole_pair_number()

    array_list = [
        np.array([out_loss.get_loss_scalar(speed / 60 * p, output=output) for speed in N0_array])
        for out_loss in self.loss_dict.values()
    ]

    plot_2D(
        [N0_array],
        array_list,
        xlabel="Speed [rpm]",
        ylabel="Losses [W]",
        legend_list=[out_loss.name for out_loss in self.loss_dict.values()],
        is_show_fig=is_show_fig,
        save_path=save_path,
    )
