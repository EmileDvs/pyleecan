from ....classes_common.parents import ancestor_with
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def get_machine_from_parent(self) -> Machine | None:
    """Get machine object from parent

    Parameters
    ----------
    self : EEC
        an EEC object

    Returns
    ----------
    machine : Machine
        a Machine object
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
