from ..Slot import SlotCheckError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def check(self, lam: Lamination | Notch | None = None) -> None:
    """Check that the SlotUD is correctly defined

    Parameters
    ----------
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    """

    if self.line_list is None:
        self.line_list = list()

    if len(self.line_list) == 0:
        raise SlotCheckError("SlotUD must have at least one line")

    for ii in range(len(self.line_list) - 1):
        if (
            abs(self.line_list[ii].get_end() - self.line_list[ii + 1].get_begin())
            > 1e-6
        ):
            raise SlotCheckError(
                "SlotUD line " + str(ii) + " and line " + str(ii + 1) + " doesn't match"
            )

    begin_id = self.wind_begin_index
    end_id = self.wind_end_index
    if begin_id is not None and end_id is not None:
        if begin_id > len(self.line_list):
            raise SlotCheckError(
                "SlotUD wind_begin_index is greater than line_list length"
            )
        if end_id > len(self.line_list):
            raise SlotCheckError(
                "SlotUD wind_end_index is greater than line_list length"
            )
        if begin_id > end_id:
            raise SlotCheckError(
                "SlotUD wind_begin_index is greater than wind_end_index"
            )
