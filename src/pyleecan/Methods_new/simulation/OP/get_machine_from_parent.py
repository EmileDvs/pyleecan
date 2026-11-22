from ....classes_common.parents import ancestor_with
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def get_machine_from_parent(self) -> Machine | None:
    """Search in the parent to find the machine

    Parameters
    ----------
    self : OP
        An OP object

    Returns
    -------
    machine : Machine
        Machine from the parent (or None)
    """

    # The closest container having the machine (a simulation), else the
    # closest one having a simulation (an output)
    holder = ancestor_with(self, "machine")
    if holder is not None:
        return holder.machine
    holder = ancestor_with(self, "simu")
    if holder is not None:
        return holder.simu.machine
    return None
