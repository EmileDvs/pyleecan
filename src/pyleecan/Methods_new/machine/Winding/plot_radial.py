from ....classes_common.parents import container_or_parent
from ....Classes_new._swat_em import datamodel
from ....definitions import config_dict
from ....Functions_new._swat_em import plots
from ....Functions_new._swat_em.config import config
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def plot_radial(self, is_show_fig: bool = True, lam: Lamination | None = None) -> None:
    """Plots the winding radial pattern

    Parameters
    ----------
    self : Winding
        A Winding object
    is_show_fig : bool
        True to call fig.show
    lam : Lamination, optional
        Lamination holding the winding (default: the parent)

    """
    lam = container_or_parent(self, lam, "lam")
    Zs = lam.get_Zs()

    p = lam.get_pole_pair_number()

    # generate a datamodel for the winding
    wdg = datamodel()

    # generate winding from inputs
    wdg.genwdg(
        Q=Zs,
        P=2 * p,
        m=self.qs,
        layers=self.Nlayer,
        turns=self.Ntcoil,
        w=self.coil_pitch,
    )
    if (
        not isinstance(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0], str)
        and len(config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"][0]) == 4
    ):  # rgba to hex
        config["plt"]["phase_colors"] = [
            "#{:02x}{:02x}{:02x}".format(
                int(color[0] * 255 * (1 - color[3]) + 255 * color[3]),
                int(color[1] * 255 * (1 - color[3]) + 255 * color[3]),
                int(color[2] * 255 * (1 - color[3]) + 255 * color[3]),
            )
            for color in config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]
        ]
    else:
        config["plt"]["phase_colors"] = config_dict["PLOT"]["COLOR_DICT"][
            "PHASE_COLORS"
        ]
    plt = plots._polar_layout_plot(None, None, wdg)
    plt.plot(show=is_show_fig, optimize_overhang=False)
