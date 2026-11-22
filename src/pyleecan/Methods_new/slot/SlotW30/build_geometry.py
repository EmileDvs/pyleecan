from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def build_geometry(self, lam: Lamination | Notch | None = None) -> list:
    """Compute the curve (Line) needed to plot the Slot.
    The ending point of a curve is the starting point of the next curve in
    the list

    Parameters
    ----------
    self : SlotW30
        A SlotW15 object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)

    Returns
    -------
    curve_list: list
        A list of Segment and Arc

    """

    line_dict = self._comp_line_dict(lam=lam)

    if self.R1 != 0 and self.R2 != 0:
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-9"],
            line_dict["9-10"],
            line_dict["10-11"],
            line_dict["11-12"],
        ]

    elif self.R1 == 0 and self.R2 != 0:
        curve_list = [
            line_dict["1-2"],
            line_dict["2-40"],
            line_dict["40-5"],
            line_dict["5-6"],
            line_dict["6-7"],
            line_dict["7-8"],
            line_dict["8-100"],
            line_dict["100-11"],
            line_dict["11-12"],
        ]

    elif self.R1 != 0 and self.R2 == 0:
        curve_list = [
            line_dict["1-2"],
            line_dict["2-3"],
            line_dict["3-4"],
            line_dict["4-60"],
            line_dict["60-80"],
            line_dict["80-9"],
            line_dict["9-10"],
            line_dict["10-11"],
            line_dict["11-12"],
        ]

    elif self.R1 == 0 and self.R2 == 0:
        curve_list = [
            line_dict["1-2"],
            line_dict["2-40"],
            line_dict["40-60"],
            line_dict["60-80"],
            line_dict["80-100"],
            line_dict["100-11"],
            line_dict["11-12"],
        ]

    return [line for line in curve_list if line is not None]
