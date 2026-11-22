from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from ....Classes_new.machine.machine import Machine


def plot_mmf_unit(self, r_max=100, fig: Figure | None = None, save_path: str | None = None, is_show_fig: bool = True, machine: Machine | None = None) -> Figure:
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
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    fig : Matplotlib.figure.Figure
        Figure of the plot

    Notes
    -----
    r_max and fig are not used: LamSlotWind.plot_mmf_unit draws on its own
    figure (the legacy call passed them and raised a TypeError)
    """

    # Local import: avoids circular imports
    from ....Classes_new.machine.lam_slot_wind import LamSlotWind


    return LamSlotWind.plot_mmf_unit(
        self, save_path=save_path, is_show_fig=is_show_fig, machine=machine
    )
