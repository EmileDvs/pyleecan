"""The Tests/New tests pass the containers (PLAN.md Step 16)."""

import pytest

from pyleecan.classes_common.parents import ContainerFallbackWarning

from backend_classes.machine.lam_slot import LamSlot
from backend_classes.slot.slot_w_10 import SlotW10


def test_fallback_from_a_test_is_an_error():
    lam = LamSlot(is_stator=True, Rint=0.1, Rext=0.2, slot=SlotW10())
    assert lam.slot.get_Rbo(lam=lam) == 0.2
    with pytest.raises(ContainerFallbackWarning, match="the lam argument is not given"):
        lam.slot.get_Rbo()
