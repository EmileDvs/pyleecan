from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination


def convert_to_UD(self, lam: Lamination | None = None, lam_label: str | None = None):
    """Convert the hole to HoleUD

    Parameters
    ----------
    lam : Lamination, optional
        Lamination holding the hole (default: the parent)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)
    """
    # Local import: avoids circular imports
    from ....Classes_new.slot.hole_ud import HoleUD

    surf_list = self.build_geometry(lam=lam, lam_label=lam_label)
    magnet_dict = self.get_magnet_dict()
    magnetization_dict = self.comp_magnetization_dict(lam=lam)

    return HoleUD(
        surf_list=surf_list,
        magnet_dict=magnet_dict,
        Zh=self.Zh,
        mat_void=self.mat_void,
        magnetization_dict_offset=magnetization_dict,
    )
