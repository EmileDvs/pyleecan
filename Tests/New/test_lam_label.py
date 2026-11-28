"""Step 16, option (b): the lamination gives its label to the slot geometry.

The surface builders of the slots and holes take ``lam_label`` (the
laminations pass ``self.get_label(machine=machine)``), so the slot geometry no
longer reads the machine holding the lamination; the computations that only
need numbers use the lamination type (``get_label(is_add_id=False)``).
"""

import warnings
from os.path import join

import pytest

from pyleecan.classes_common.parents import ContainerFallbackWarning
from pyleecan.definitions import DATA_DIR

from backend_classes.machine.lam_slot_wind import LamSlotWind
from backend_classes.slot.slot_w_10 import SlotW10
from backend_functions.load import load


def _lamination():
    return LamSlotWind(
        Rint=0.1, Rext=0.2, is_internal=False, is_stator=True, slot=SlotW10(Zs=12)
    )


def test_given_label_used():
    lam = _lamination()
    surf = lam.slot.get_surface_active(lam=lam, lam_label="Stator-1")
    assert surf.label.startswith("Stator-1_")


def test_default_label_from_lamination():
    lam = _lamination()
    surf = lam.slot.get_surface_active(lam=lam)
    assert surf.label.startswith("Stator_")


def test_type_label_does_not_read_the_machine():
    machine = load(join(DATA_DIR, "Machine", "Toyota_Prius.json"))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ContainerFallbackWarning)
        assert machine.stator.get_label(is_add_id=False) == "Stator"
        assert machine.stator.get_label(machine=machine) == "Stator-0"
        with pytest.raises(ContainerFallbackWarning):
            machine.stator.get_label()


@pytest.mark.parametrize("name", ["Toyota_Prius", "SCIM_006", "SPMSM_003"])
def test_machine_geometry_without_fallback(name):
    machine = load(join(DATA_DIR, "Machine", name + ".json"))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ContainerFallbackWarning)
        surf_list = machine.build_geometry(sym=1)
        machine.comp_masses()
    labels = {surf.label.split("_")[0] for surf in surf_list}
    assert {"Stator-0", "Rotor-0"} <= labels
