"""Methods added by hand to the frozen Methods_new (HAND_WRITTEN_METHODS).

HoleMLSRPM.comp_surface_magnet_id: the HoleMag magnet totals called it, the
legacy class did not define it (AttributeError in comp_masses of LSRPM_001).
"""

from os.path import isfile, join

import pytest

from pyleecan.definitions import DATA_DIR, MAIN_DIR
from pyleecan.Generator.ClassGenerator.New.moved_functions import (
    HAND_WRITTEN_METHODS,
    add_moved_methods,
    all_moved_targets,
)

from backend_functions.load import load


def test_hand_written_methods_added_to_the_classes():
    gen_dict = {target.class_name: {"methods": []} for _, target in all_moved_targets()}
    gen_dict.update({name: {"methods": []} for name in HAND_WRITTEN_METHODS})
    add_moved_methods(gen_dict)
    add_moved_methods(gen_dict)  # Idempotent
    for class_name, methods in HAND_WRITTEN_METHODS.items():
        assert gen_dict[class_name]["methods"] == list(methods)


def test_hand_written_methods_have_a_module():
    for class_name, methods in HAND_WRITTEN_METHODS.items():
        for method in methods:
            assert isfile(join(MAIN_DIR, "Methods_new", "slot", class_name, method + ".py"))


def test_hole_mlsrpm_magnet_totals():
    machine = load(join(DATA_DIR, "Machine", "LSRPM_001.json"))
    lam = machine.rotor
    hole = lam.hole[0]
    S = hole.comp_surface_magnet(lam=lam)
    assert S > 0
    assert hole.comp_surface_magnet_id(0, lam=lam) == pytest.approx(S)
    assert hole.comp_surface_magnet_id(1, lam=lam) == 0
    assert hole.comp_surface_magnets(lam=lam) == pytest.approx(S)
    assert hole.comp_volume_magnets(lam=lam) == pytest.approx(
        hole.comp_volume_magnet(lam=lam)
    )
    M_dict = machine.comp_masses()
    assert M_dict["Rotor-0"]["Mmag"] > 0
