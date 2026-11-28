from ....classes_common.parents import container_or_parent
from ....Classes_new.geometry.segment import Segment
from ....Classes_new.geometry.arc_1 import Arc1
from ....Classes_new.geometry.surf_line import SurfLine
from ....Functions_new.utils.labels import SOP_LAB, DRAW_PROP_LAB
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.geometry.line import Line
    from ....Classes_new.machine.notch import Notch


def get_surface_opening(self, alpha: float = 0, delta: complex = 0, lam: Lamination | Notch | None = None, lam_label: str | None = None) -> list:
    """Return the list of surfaces defining the opening area of the Slot

    Parameters
    ----------
    self : SlotW10
        A SlotW10 object
    alpha : float
        float number for rotation (Default value = 0) [rad]
    delta : complex
        complex number for translation (Default value = 0)
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    surf_list : list
        list of surfaces objects
    """
    lam = container_or_parent(self, lam, "lam")

    # H0=H1=0 no opening
    H1 = self.get_H1(lam=lam)
    if self.H0 == 0 and H1 == 0:
        return []

    # Create curve list
    line_dict = self._comp_line_dict(lam=lam)
    curve_list: list[Line] = [
        line_dict["1-2"],
        line_dict["2-3"],
        line_dict["3-4"],
        line_dict["4-7"],
        line_dict["7-8"],
        line_dict["8-9"],
        line_dict["9-10"],
        line_dict["10-1"],
    ]
    curve_list = [line for line in curve_list if line is not None]

    # Only the closing arc (10-1) needs to be drawn (in FEMM)
    for curve in curve_list[:-1]:
        if curve.prop_dict is None:
            curve.prop_dict = dict()
        curve.prop_dict.update({DRAW_PROP_LAB: False})

    # Create surface
    if self.is_outwards(lam=lam):
        Zmid = self.get_Rbo(lam=lam) + (self.H0 + H1) / 2
    else:
        Zmid = self.get_Rbo(lam=lam) - (self.H0 + H1) / 2
    if lam_label is None:
        lam_label = lam.get_label()
    label = lam_label + "_" + SOP_LAB + "_R0-T0-S0"
    surface = SurfLine(line_list=curve_list, label=label, point_ref=Zmid)

    # Apply transformation
    surface.rotate(alpha)
    surface.translate(delta)

    return [surface]
