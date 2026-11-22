"""Step 14 geometry review: default edge colors of get_patches, empty SurfLine,
missing FEMM_dict of Surface.draw_FEMM."""

import pytest
from matplotlib.colors import to_rgba

from pyleecan.Classes_new.geometry.circle import Circle
from pyleecan.Classes_new.geometry.surf_line import SurfLine
from pyleecan.definitions import config_dict

COLOR_DICT = config_dict["PLOT"]["COLOR_DICT"]


@pytest.mark.parametrize(
    "is_edge_only, key", [(False, "PATCH_EDGE"), (True, "PATCH_EDGE_ALPHA")]
)
def test_default_edgecolor(is_edge_only, key):
    (patch,) = Circle(center=0, radius=1).get_patches(is_edge_only=is_edge_only)
    assert patch.get_edgecolor() == to_rgba(COLOR_DICT[key])


def test_dashed_edgecolor():
    (patch,) = Circle(center=0, radius=1).get_patches(edgecolor="r--")
    assert patch.get_edgecolor() == to_rgba("r")
    assert patch.get_linestyle() == "--"


def test_surf_line_without_lines_has_no_patch():
    assert SurfLine(line_list=[]).get_patches() == []


def test_draw_femm_needs_femm_dict():
    with pytest.raises(ValueError, match="FEMM_dict"):
        Circle(center=0, radius=1).draw_FEMM(femm=None)
