"""Missing cases that returned None implicitly now raise an explicit error (Step 14)."""

import pytest

from pyleecan.Classes_new.machine.lam_hole import LamHole
from pyleecan.Classes_new.machine.lam_slot import LamSlot
from pyleecan.Classes_new.slot.hole_ud import HoleUD
from pyleecan.Classes_new.slot.slot_w_14 import SlotW14
from pyleecan.Classes_new.slot.slot_w_15 import SlotW15
from pyleecan.Classes_new.slot.slot_w_29 import SlotW29
from pyleecan.classes_common.errors import S15InnerError


@pytest.mark.parametrize(
    "slot",
    [
        SlotW14(Zs=6, H0=5e-3, H1=5e-3, H3=15e-3, W0=10e-3, W3=10e-3, wedge_type=2),
        SlotW29(Zs=6, H0=1e-3, H1=1e-3, H2=10e-3, W0=5e-3, W1=8e-3, W2=10e-3, wedge_type=2),
    ],
)
def test_unknown_wedge_type_raises(slot):
    LamSlot(Rint=0.1, Rext=0.2, is_internal=True, is_stator=False, slot=slot)
    with pytest.raises(NotImplementedError, match="wedge_type must be 0 or 1"):
        slot.comp_surface_opening()
    with pytest.raises(NotImplementedError, match="wedge_type must be 0 or 1"):
        slot.comp_surface_wedge()


def test_slot_w15_inward_opening_raises():
    slot = SlotW15(Zs=6, H0=5e-3, H1=5e-3, H2=20e-3, W0=5e-3, W3=10e-3, R1=1e-3)
    LamSlot(Rint=0.1, Rext=0.2, is_internal=True, is_stator=False, slot=slot)
    with pytest.raises(S15InnerError):
        slot.comp_surface_opening()


def test_hole_ud_unknown_magnet_index_raises():
    hole = HoleUD(Zh=4, magnet_dict={})
    LamHole(Rint=0.01, Rext=0.1, is_internal=True, is_stator=False, hole=[hole])
    with pytest.raises(ValueError, match="no magnet of index 0"):
        hole.comp_surface_magnet_id(0)
