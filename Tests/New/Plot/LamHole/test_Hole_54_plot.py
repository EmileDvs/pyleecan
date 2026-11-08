# -*- coding: utf-8 -*-

import pytest

from os.path import join
import matplotlib.pyplot as plt
from numpy import pi

from pyleecan.Classes_new.frame import Frame
from pyleecan.Classes_new.lam_hole import LamHole
from pyleecan.Classes_new.lam_slot_wind import LamSlotWind
from pyleecan.Classes_new.machine_ipmsm import MachineIPMSM
from pyleecan.Classes_new.magnet import Magnet
from pyleecan.Classes_new.shaft import Shaft
from pyleecan.Classes_new.hole_m_54 import HoleM54
from Tests.New._test_paths import save_plot_path as save_path


class Test_Hole_54_plot(object):
    """pytest for Lamination with Hole plot"""

    def test_Lam_Hole_54_plot(self):
        """Test machine plot hole 54"""

        plt.close("all")
        test_obj = MachineIPMSM()
        test_obj.rotor = LamHole(
            is_internal=True, Rint=0.1, Rext=0.2, is_stator=False, L1=0.7
        )
        test_obj.rotor.hole = list()
        test_obj.rotor.hole.append(
            HoleM54(Zh=8, W0=pi / 4, H0=50e-3, H1=10e-3, R1=100e-3)
        )
        test_obj.rotor.hole.append(
            HoleM54(Zh=8, W0=pi / 6, H0=25e-3, H1=10e-3, R1=100e-3)
        )

        test_obj.rotor.plot(is_show_fig=False)
        fig = plt.gcf()
        fig.savefig(join(save_path, "test_Lam_Hole_s54-Rotor.png"))
        assert len(fig.axes[0].patches) == 18

        test_obj.rotor.hole[0].plot(is_show_fig=False)
        fig = plt.gcf()
        fig.savefig(join(save_path, "test_Lam_Hole_s54-Rotor hole.png"))
        assert len(fig.axes[0].patches) == 1
