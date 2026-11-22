from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.slot.slot_ud_2 import SlotUD2


def convert_to_SlotUD2(self) -> SlotUD2:
    """Convert the slot to the equivalent SlotUD2

    Parameters
    ----------
    self : Slot
        a Slot object

    Returns
    -------
    new_slot : SlotUD2
        SlotUD2 version of the Slot
    """
    # Local import: avoids circular imports
    from ....Classes_new.slot.slot_ud_2 import SlotUD2

    new_slot = SlotUD2()
    new_slot.Zs = self.Zs
    new_slot.line_list = self.build_geometry()
    new_slot.active_surf = self.get_surface_active()
    new_slot.split_active_surf_dict = None

    return new_slot
