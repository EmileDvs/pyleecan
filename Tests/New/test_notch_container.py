"""Step 16: the slot of a notch gets the notch's lamination as its container.

The Notch methods a slot calls on its container (get_Rbo, get_Ryoke,
is_outwards, get_label) only forward to the lamination of the notch, so the
NotchEvenDist methods give that lamination to their notch shape: no parent
read left, same results as with the notch as container (legacy path).
"""

import warnings
from os.path import join

import pytest

from pyleecan.classes_common.parents import ContainerFallbackWarning
from pyleecan.definitions import DATA_DIR

from backend_functions.load import load

NOTCH_MACHINES = ["Tesla_model_3", "SPMSM_LamSlotMultiWind"]


def _notched_laminations(machine):
    lam_list = [lam for lam in machine.get_lam_list() if lam.notch]
    assert lam_list
    return lam_list


@pytest.mark.parametrize("name", NOTCH_MACHINES)
def test_notch_machine_without_fallback(name):
    machine = load(join(DATA_DIR, "Machine", name + ".json"))
    with warnings.catch_warnings():
        warnings.simplefilter("error", ContainerFallbackWarning)
        machine.build_geometry(sym=1)
        machine.comp_masses()
        for lam in _notched_laminations(machine):
            for notch in lam.notch:
                notch.get_notch_desc_list(lam=lam)
                notch.comp_surface(lam=lam)


@pytest.mark.parametrize("name", NOTCH_MACHINES)
def test_same_result_as_the_notch_container(name):
    machine = load(join(DATA_DIR, "Machine", name + ".json"))
    for lam in _notched_laminations(machine):
        for notch in lam.notch:
            shape = notch.notch_shape
            with warnings.catch_warnings():
                # The notch as container falls back to its parent lamination
                warnings.simplefilter("ignore", ContainerFallbackWarning)
                S_notch = shape.comp_surface(lam=notch)
                lines_notch = shape.build_geometry(lam=notch)
            assert notch.comp_surface(lam=lam) == pytest.approx(shape.Zs * S_notch)
            lines_lam = shape.build_geometry(lam=lam)
            assert [line.get_begin() for line in lines_lam] == pytest.approx(
                [line.get_begin() for line in lines_notch]
            )
