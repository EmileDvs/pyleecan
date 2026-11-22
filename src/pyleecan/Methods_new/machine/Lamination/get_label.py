from ....classes_common.parents import container_or_parent
from ....Functions_new.utils.labels import STATOR_LAB, ROTOR_LAB
from ....classes_common.errors import ParentMissingError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.machine.machine import Machine


def get_label(self, is_add_id: bool = True, machine: Machine | None = None) -> str:
    """Return the label of the lamination (Stator-0 for instance)

    Parameters
    ----------
    self : Lamination
        a Lamination object
    is_add_id : bool
        True to add the "-X" part
    machine : Machine, optional
        Machine holding the lamination (default: the parent)

    Returns
    -------
    label : str
        Label of the lamination

    """
    machine = container_or_parent(self, machine, "machine")

    if self.is_stator:
        label = STATOR_LAB
    else:
        label = ROTOR_LAB

    if is_add_id:
        if machine is not None:
            try:
                lam_list = machine.get_lam_list(is_int_to_ext=True, key=label)
                label += "-" + str(lam_list.index(self))
            except:
                pass
        # else:
        #     raise ParentMissingError("Error: The slot is not inside a Lamination")

    return label
