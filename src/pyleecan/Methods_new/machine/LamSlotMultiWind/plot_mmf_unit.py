from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure


def plot_mmf_unit(self, r_max=100, fig: Figure | None = None, save_path: str | None = None, is_show_fig: bool = True) -> None:
    """Plot the winding unit mmf as a function of space
    Parameters
    ----------

    self : LamSlotMultiWind
        an LamSlotMultiWind object
    Na : int
        Space discretization
    fig : Matplotlib.figure.Figure
        existing figure to use if None create a new one
    is_show_fig : bool
        To call show at the end of the method
    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


    LamSlotWind.plot_mmf_unit(
        self, r_max=r_max, fig=fig, save_path=save_path, is_show_fig=is_show_fig
    )
