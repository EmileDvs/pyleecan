# -*- coding: utf-8 -*-
import pytest

from numpy import ndarray, arcsin, exp
from backend_classes.machine.lam_slot import LamSlot
from backend_classes.slot.slot_w_12 import SlotW12
from backend_classes.geometry.segment import Segment
from backend_classes.geometry.surf_line import SurfLine
from backend_classes.geometry.arc_1 import Arc1
from backend_classes.geometry.arc_3 import Arc3
from backend_classes.slot.slot import Slot
from pyleecan.classes_common.errors import S12_R20CheckError

# For AlmostEqual
DELTA = 1e-4

slotW12_test = list()

# Internal Slot
lam = LamSlot(is_internal=True, Rext=0.1325)
lam.slot = SlotW12(H0=1e-3, H1=6e-3, R1=0.5e-3, R2=2e-3)
slotW12_test.append(
    {
        "test_obj": lam,
        "S_exp": 3.91088e-5,
        "Aw": 0.0299276,
        "SW_exp": 3.028318e-5,
        "SO_exp": 8.82565e-06,
        "H_exp": 1.0015e-2,
    }
)

# Outward Slot
lam = LamSlot(is_internal=False, Rint=0.1325)
lam.slot = SlotW12(H0=1e-3, H1=6e-3, R1=0.5e-3, R2=2e-3)
slotW12_test.append(
    {
        "test_obj": lam,
        "S_exp": 3.90283e-5,
        "Aw": 0.0273343,
        "SW_exp": 3.02831853e-5,
        "SO_exp": 8.7451438e-06,
        "H_exp": 9.9849e-3,
    }
)


class Test_SlotW12_meth(object):
    """pytest for SlotW12 methods"""

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_schematics(self, test_dict):
        """Check that the schematics is correct"""
        test_obj = test_dict["test_obj"]
        point_dict = test_obj.slot._comp_point_coordinate(lam=test_obj)

        # Check width
        assert abs(point_dict["Z1"] - point_dict["Z8"]) == pytest.approx(
            2 * test_obj.slot.R2
        )
        assert abs(point_dict["Z2"] - point_dict["Z7"]) == pytest.approx(
            2 * test_obj.slot.R2
        )
        assert abs(point_dict["Z3"] - point_dict["Z6"]) == pytest.approx(
            2 * test_obj.slot.R2
        )
        assert abs(point_dict["Z4"] - point_dict["Z5"]) == pytest.approx(
            2 * test_obj.slot.R2
        )
        # Check height
        assert abs(point_dict["Z1"] - point_dict["Z2"]) == pytest.approx(
            test_obj.slot.H0
        )
        assert abs(point_dict["Z2"] - point_dict["Z3"]) == pytest.approx(
            2 * test_obj.slot.R1
        )
        assert abs(point_dict["Z3"] - point_dict["Z4"]) == pytest.approx(
            test_obj.slot.H1
        )
        assert abs(point_dict["Z8"] - point_dict["Z7"]) == pytest.approx(
            test_obj.slot.H0
        )
        assert abs(point_dict["Z7"] - point_dict["Z6"]) == pytest.approx(
            2 * test_obj.slot.R1
        )
        assert abs(point_dict["Z6"] - point_dict["Z5"]) == pytest.approx(
            test_obj.slot.H1
        )

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_build_geometry_active(self, test_dict):
        """Check that the active geometry is correctly split"""
        test_obj = test_dict["test_obj"]
        surf_list = test_obj.slot.build_geometry_active(Nrad=3, Ntan=2, lam=test_obj)

        # Check label
        assert surf_list[0].label == "Stator_Winding_R0-T0-S0"
        assert surf_list[1].label == "Stator_Winding_R1-T0-S0"
        assert surf_list[2].label == "Stator_Winding_R2-T0-S0"
        assert surf_list[3].label == "Stator_Winding_R0-T1-S0"
        assert surf_list[4].label == "Stator_Winding_R1-T1-S0"
        assert surf_list[5].label == "Stator_Winding_R2-T1-S0"
        # Check tangential position
        assert surf_list[0].point_ref.imag < 0
        assert surf_list[1].point_ref.imag < 0
        assert surf_list[2].point_ref.imag < 0
        assert surf_list[3].point_ref.imag > 0
        assert surf_list[4].point_ref.imag > 0
        assert surf_list[5].point_ref.imag > 0
        # Check radial position
        if test_obj.is_internal:
            # Tan=0
            assert surf_list[0].point_ref.real > surf_list[1].point_ref.real
            assert surf_list[1].point_ref.real > surf_list[2].point_ref.real
            # Tan=1
            assert surf_list[3].point_ref.real > surf_list[4].point_ref.real
            assert surf_list[4].point_ref.real > surf_list[5].point_ref.real
        else:
            # Tan=0
            assert surf_list[0].point_ref.real < surf_list[1].point_ref.real
            assert surf_list[1].point_ref.real < surf_list[2].point_ref.real
            # Tan=1
            assert surf_list[3].point_ref.real < surf_list[4].point_ref.real
            assert surf_list[4].point_ref.real < surf_list[5].point_ref.real

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_surface(self, test_dict):
        """Check that the computation of the surface is correct"""
        test_obj = test_dict["test_obj"]
        result = test_obj.slot.comp_surface(lam=test_obj)

        a = result
        b = test_dict["S_exp"]
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg
        # Check that the analytical method returns the same result as the numerical one
        b = Slot.comp_surface(test_obj.slot, lam=test_obj)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < 1e-5, msg

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_surface_active(self, test_dict):
        """Check that the computation of the winding surface is correct"""
        test_obj = test_dict["test_obj"]
        result = test_obj.slot.comp_surface_active(lam=test_obj)

        a = result
        b = test_dict["SW_exp"]
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg
        # Check that the analytical method returns the same result as the numerical one
        b = Slot.comp_surface_active(test_obj.slot, lam=test_obj)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < 1e-5, msg

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_surface_opening(self, test_dict):
        """Check that the computation of the opening surface is correct"""
        test_obj = test_dict["test_obj"]
        result = test_obj.slot.comp_surface_opening(lam=test_obj)

        a = result
        b = test_dict["SO_exp"]
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg

        # Check that the analytical method returns the same result as the numerical one
        b = Slot.comp_surface_opening(test_obj.slot, Ndisc=400, lam=test_obj)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_height(self, test_dict):
        """Check that the computation of the height is correct"""
        test_obj = test_dict["test_obj"]
        result = test_obj.slot.comp_height(lam=test_obj)

        a = result
        b = test_dict["H_exp"]
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg
        # Check that the analytical method returns the same result as the numerical one
        b = Slot.comp_height(test_obj.slot, lam=test_obj)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < 1e-5, msg

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_angle_opening(self, test_dict):
        """Check that the computation of the average opening angle iscorrect"""
        test_obj = test_dict["test_obj"]
        a = test_obj.slot.comp_angle_opening(lam=test_obj)
        assert a == 2 * arcsin(2 * test_obj.slot.R2 / (2 * 0.1325))
        # Check that the analytical method returns the same result as the numerical one
        b = Slot.comp_angle_opening(test_obj.slot, lam=test_obj)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg

    @pytest.mark.parametrize("test_dict", slotW12_test)
    def test_comp_angle_active_eq(self, test_dict):
        """Check that the computation of the average angle is correct"""
        test_obj = test_dict["test_obj"]
        result = test_obj.slot.comp_angle_active_eq(lam=test_obj)

        a = result
        b = test_dict["Aw"]
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < DELTA, msg

    def test_build_geometry(self):
        """Check if the build_geometry of the slot is correct"""
        test_obj = SlotW12(H0=1e-3, H1=6e-3, R1=0.5e-3, R2=2e-3)
        lam = LamSlot(is_internal=True, slot=test_obj, Rext=1)

        # Rbo = 1
        Z1 = exp(-1j * float(arcsin(2e-3)))
        Z2 = Z1 - 1e-3
        Z3 = Z2 - 1e-3
        Z4 = Z3 - 6e-3
        # symetry
        Z5 = Z4.conjugate()
        Z6 = Z3.conjugate()
        Z7 = Z2.conjugate()
        Z8 = Z1.conjugate()

        # creation of the curve
        curve_list = list()
        curve_list.append(Segment(begin=Z1, end=Z2))
        curve_list.append(Arc3(begin=Z2, end=Z3, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z3, end=Z4))
        curve_list.append(Arc3(begin=Z4, end=Z5, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z5, end=Z6))
        curve_list.append(Arc3(begin=Z6, end=Z7, is_trigo_direction=True))
        curve_list.append(Segment(begin=Z7, end=Z8))

        result = test_obj.build_geometry(lam=lam)
        assert len(result) == len(curve_list)
        for i in range(0, len(result)):
            a = result[i].begin
            b = curve_list[i].begin
            assert abs((a - b) / a - 0) < DELTA

            a = result[i].end
            b = curve_list[i].end
            assert abs((a - b) / a - 0) < DELTA

    def test_check_error(self):
        """Check that the check method is correctly raising an error"""
        lam = LamSlot(is_internal=True, Rext=0.1325)
        lam.slot = SlotW12(Zs=69, R2=0)

        with pytest.raises(S12_R20CheckError) as context:
            lam.slot.check(lam=lam)


if __name__ == "__main__":
    a = Test_SlotW12_meth()
    for ii, test_dict in enumerate(slotW12_test):
        print("Running test for Slot[" + str(ii) + "]")
        a.test_schematics(test_dict)
        a.test_comp_surface(test_dict)
        a.test_comp_surface_active(test_dict)
        a.test_comp_surface_opening(test_dict)
        a.test_comp_height(test_dict)
        a.test_build_geometry_active(test_dict)
        a.test_comp_angle_opening(test_dict)
        a.test_comp_angle_active_eq(test_dict)
        print("Done")
