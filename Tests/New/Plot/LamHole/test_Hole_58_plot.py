# -*- coding: utf-8 -*-

from os.path import join
import matplotlib.pyplot as plt
from numpy import pi

import pytest

from backend_classes.machine.frame import Frame
from backend_classes.machine.lam_hole import LamHole
from backend_classes.machine.lam_slot_wind import LamSlotWind
from backend_classes.machine.machine_ipmsm import MachineIPMSM
from backend_classes.machine.magnet import Magnet
from backend_classes.machine.shaft import Shaft
from backend_classes.slot.hole_m_58 import HoleM58
from Tests.New._test_paths import save_plot_path as save_path


class Test_Hole_58_plot(object):
    def test_Lam_Hole_58_plot(self):
        """Test machine plot hole 58"""

        plt.close("all")
        test_obj = LamHole(
            is_internal=True, Rint=0.021, Rext=0.075, is_stator=False, L1=0.7
        )
        test_obj.hole = list()
        test_obj.hole.append(
            HoleM58(
                Zh=8,
                W0=20e-3,
                W1=16e-3,
                W2=2e-3,
                W3=2 * pi / 8 * 0.6,
                H0=15e-3,
                H1=5e-3,
                H2=5e-3,
                R0=1e-3,
            )
        )

        test_obj.plot(is_show_fig=False)
        fig = plt.gcf()
        fig.savefig(join(save_path, "test_Lam_Hole_s58-Rotor.png"))
        assert len(fig.axes[0].patches) == 26

        test_obj.hole[0].plot(is_show_fig=False, lam=test_obj)
        fig = plt.gcf()
        fig.savefig(join(save_path, "test_Lam_Hole_s58-Rotor hole.png"))
        assert len(fig.axes[0].patches) == 3
