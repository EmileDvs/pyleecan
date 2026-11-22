# -*- coding: utf-8 -*-

from os.path import join
import pytest

from backend_classes.machine.lamination import Lamination
from backend_classes.slot.ventilation_circ import VentilationCirc
from pyleecan.classes_common.errors import CircleBuildGeometryError
from backend_classes.slot.hole import Hole

"""unittest for VentilationCirc"""


class Test_VentilationCirc(object):
    @pytest.fixture
    def lam(self):
        """Run at the begining of every test to setup the VentilationCirc"""
        test_obj = VentilationCirc(Zh=8, Alpha0=0, D0=5e-3, H0=40e-3)
        return Lamination(is_stator=True, axial_vent=[test_obj])

    @pytest.fixture
    def vent(self, lam):
        return lam.axial_vent[0]

    def test_build_geometry_errors(self, vent, lam):
        """Test that build_geometry can raise some errors"""
        with pytest.raises(CircleBuildGeometryError) as context:
            vent.build_geometry(alpha="dz", lam=lam)
        with pytest.raises(CircleBuildGeometryError) as context:
            vent.build_geometry(alpha=1, delta="dz", lam=lam)

    def test_build_geometry(self, vent, lam):
        """Test that build_geometry works"""
        result = vent.build_geometry(lam=lam)

        assert len(result) == 1

    def test_comp_surface(self, vent, lam):
        """Check that the computation of the surface is correct"""
        # Check that the analytical method returns the same result as the numerical one
        a = vent.comp_surface(lam=lam)
        b = Hole.comp_surface(vent, lam=lam)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < 1e-4, msg
