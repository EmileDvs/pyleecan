# -*- coding: utf-8 -*-

from os.path import join
import pytest
from numpy import pi

from backend_classes.machine.lamination import Lamination
from backend_classes.slot.ventilation_trap import VentilationTrap
from pyleecan.classes_common.errors import TrapezeBuildGeometryError
from backend_classes.slot.hole import Hole

"""unittest for VentilationTrap"""


class Test_VentilationTrap(object):
    @pytest.fixture
    def lam(self):
        """Run at the begining of every test to setup the VentilationTrap"""
        test_obj = VentilationTrap(
            Zh=6, Alpha0=pi / 6, W1=30e-3, W2=60e-3, D0=0.05, H0=0.3
        )
        return Lamination(is_stator=True, axial_vent=[test_obj])

    @pytest.fixture
    def vent(self, lam):
        return lam.axial_vent[0]

    def test_build_geometry_errors(self, vent, lam):
        """Test that build_geometry can raise some errors"""
        with pytest.raises(TrapezeBuildGeometryError) as context:
            vent.build_geometry(alpha="dz", lam=lam)
        with pytest.raises(TrapezeBuildGeometryError) as context:
            vent.build_geometry(alpha=1, delta="dz", lam=lam)

    def test_comp_surface(self, vent, lam):
        """Check that the computation of the surface is correct"""
        # Check that the analytical method returns the same result as the numerical one
        a = vent.comp_surface(lam=lam)
        b = Hole.comp_surface(vent, lam=lam)
        msg = "Return " + str(a) + " expected " + str(b)
        assert abs((a - b) / a - 0) < 1e-4, msg
