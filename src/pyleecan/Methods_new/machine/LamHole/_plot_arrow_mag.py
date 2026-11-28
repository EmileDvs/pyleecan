import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

from ....definitions import config_dict
from ....Functions_new.utils.init_fig import init_fig
from ....Functions_new.utils.labels import decode_label, HOLEM_LAB, LAM_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.axes import Axes


def _plot_arrow_mag(
    self,
    ax: Axes | None = None,
    sym: int = 1,
    alpha: float = 0,
    delta: complex = 0,
) -> None:
    """Plot the magnetization direction as arrow on top of the lamination
    (meant to be called by LamHole.plot)

    Parameters
    ----------
    self : LamHole
        A LamHole object
    ax : Matplotlib.axes.Axes object
        Axis on which to plot the arrow
    sym : int
        Symmetry factor (1= plot full machine, 2= half of the machine...)
    alpha : float
        angle for rotation (Default value = 0) [rad]
    delta : complex
        complex for translation (Default value = 0)
    """
    if ax is None:
        ax = plt.gca()

    for hole in self.hole:
        H = hole.comp_height(lam=self)
        mag_dict = hole.comp_magnetization_dict(lam=self)
        for magnet_name, mag_dir in mag_dict.items():
            # Get the correct surface
            mag_surf = None
            mag_id = int(magnet_name.split("_")[-1])
            mag = hole.get_magnet_by_id(mag_id)
            if mag is not None:
                for surf in hole.build_geometry(lam=self, lam_label=self.get_label(is_add_id=False)):
                    label_dict = decode_label(surf.label)
                    if (
                        HOLEM_LAB in label_dict["surf_type"]
                        and label_dict["T_id"] == mag_id
                    ):
                        mag_surf = surf
                        break
                if mag_surf is None:
                    raise ValueError(
                        f"{type(self).__name__}: no surface of {magnet_name} in the "
                        "geometry of its hole"
                    )
                # Create arrow coordinates
                Zh = hole.Zh
                for ii in range(int(Zh / sym)):
                    off = np.pi if ii % 2 == 1 else 0
                    if mag is not None and mag.type_magnetization == 3:
                        off -= np.pi / 2
                    Z1 = (mag_surf.point_ref + delta) * np.exp(
                        1j * (ii * 2 * np.pi / Zh + np.pi / Zh + alpha)
                    )
                    Z2 = (
                        mag_surf.point_ref + delta + H / 5 * np.exp(1j * (mag_dir + off))
                    ) * np.exp(1j * (ii * 2 * np.pi / Zh + np.pi / Zh + alpha))
                    ax.annotate(
                        text="",
                        xy=(Z2.real, Z2.imag),
                        xytext=(Z1.real, Z1.imag),
                        arrowprops=dict(arrowstyle="->", linewidth=1, color="b"),
                    )
