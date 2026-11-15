# -*- coding: utf-8 -*
from os.path import join
import pytest
from pyleecan.Classes_new.geometry.circle import Circle
from pyleecan.Classes_new.geometry.segment import Segment
from pyleecan.Classes_new.geometry.surf_line import SurfLine
from pyleecan.Functions_new.load import load
from Tests import TEST_DATA_DIR

# Configuring the test of is_inside
inside_test = list()

# Test 1 : checking if a point is inside a circle of radius 1 at 0 + 0j
C1 = Circle()
inside_test.append({"surf": C1, "Z": 0, "result": True})  # inside
inside_test.append({"surf": C1, "Z": 20, "result": False})  # outside
inside_test.append({"surf": C1, "Z": 1, "result": False})  # online not OK
inside_test.append({"surf": C1, "Z": 1, "if_online": True, "result": True})  # online OK

# Test 2 : checking if a point is inside a "C-shape" surface
A0 = 0
A1 = 0 + 4j
A2 = 3 + 4j
A3 = 3 + 3j
A4 = 1 + 3j
A5 = 1 + 1j
A6 = 3 + 1j
A7 = 3

line_list1 = list()
line_list1.append(Segment(begin=A0, end=A1))
line_list1.append(Segment(begin=A1, end=A2))
line_list1.append(Segment(begin=A2, end=A3))
line_list1.append(Segment(begin=A3, end=A4))
line_list1.append(Segment(begin=A4, end=A5))
line_list1.append(Segment(begin=A5, end=A6))
line_list1.append(Segment(begin=A6, end=A7))
line_list1.append(Segment(begin=A7, end=A0))

C2 = SurfLine(line_list=line_list1, point_ref=A0)

inside_test.append({"surf": C2, "Z": 0.5 + 2j, "result": True})  # inside
inside_test.append({"surf": C2, "Z": 2 + 2j, "result": False})  # outside
inside_test.append({"surf": C2, "Z": 2.03, "result": False})  # online not OK
inside_test.append(
    {"surf": C2, "Z": 2.03, "if_online": True, "result": True}
)  # online OK

# SlotCirc
SCirc = load(join(TEST_DATA_DIR, "test_surf.json"))
inside_test.append(
    {"surf": SCirc, "Z": SCirc.point_ref, "if_online": False, "result": True}
)


@pytest.mark.parametrize("test_dict", inside_test)
def test_is_inside(test_dict):
    "Check if the method is_inside is working correctly"
    surf = test_dict["surf"]
    Z = test_dict["Z"]
    result = test_dict["result"]

    if "if_online" in test_dict:
        if_online = test_dict["if_online"]
        assert result == surf.is_inside(Z, if_online)
    else:
        assert result == surf.is_inside(Z)


if __name__ == "__main__":
    for test_dict in inside_test:
        test_is_inside(test_dict)

    # test_is_inside(inside_test[-1])
    print("Done")
