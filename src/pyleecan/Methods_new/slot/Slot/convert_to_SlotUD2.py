from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.slot.slot_ud_2 import SlotUD2
    from ....Classes_new.machine.lamination import Lamination
    from ....Classes_new.machine.notch import Notch


def convert_to_SlotUD2(self, lam: Lamination | Notch | None = None, lam_label: str | None = None) -> SlotUD2:
    """Convert the slot to the equivalent SlotUD2

    Parameters
    ----------
    self : Slot
        a Slot object
    lam : Lamination or Notch, optional
        Lamination (or notch) holding the slot (default: the parent)
    lam_label : str, optional
        Label of the lamination (default: lam.get_label(), which reads
        the machine holding the lamination)

    Returns
    -------
    new_slot : SlotUD2
        SlotUD2 version of the Slot
    """
    # Local import: avoids circular imports
    from ....Classes_new.slot.slot_ud_2 import SlotUD2

    new_slot = SlotUD2()
    new_slot.Zs = self.Zs
    new_slot.line_list = self.build_geometry(lam=lam)
    new_slot.active_surf = self.get_surface_active(lam=lam, lam_label=lam_label)
    new_slot.split_active_surf_dict = None

    return new_slot
