# -*- coding: utf-8 -*-

from os.path import join
import pytest

import matplotlib.pyplot as plt
from numpy import pi
from backend_classes.machine.lamination import Lamination
from backend_classes.slot.ventilation_circ import VentilationCirc
from backend_classes.slot.hole_ud import HoleUD
from backend_classes.geometry.segment import Segment
from backend_classes.geometry.surf_line import SurfLine
from backend_functions.utils.labels import HOLEV_LAB
from Tests.New._test_paths import save_plot_path as save_path


def test_HoleUD_vent_plot():
    plt.close("all")

    test_obj = Lamination(is_internal=True, Rint=0.1, Rext=0.2, is_stator=False, L1=0.7)
    # Square Vent as HoleUD align on Ox axis
    vent = HoleUD(Zh=8)
    line_list = list()
    W = 0.01
    C = 0.15
    line_list.append(Segment(begin=C - W - 1j * W, end=C + W - 1j * W))
    line_list.append(Segment(begin=C + W - 1j * W, end=C + W + 1j * W))
    line_list.append(Segment(begin=C + W + 1j * W, end=C - W + 1j * W))
    line_list.append(Segment(begin=C - W + 1j * W, end=C - W - 1j * W))
    vent.surf_list = [SurfLine(line_list=line_list, label=HOLEV_LAB)]
    # Circular Vent on "tooth" axis
    vent2 = VentilationCirc(Zh=8, H0=0.15, D0=0.02, Alpha0=pi / 8)

    test_obj.axial_vent = [vent, vent2]
    test_obj.plot(is_show_fig=False, save_path=join(save_path, "Vent_nosym.png"))
    test_obj.plot(is_show_fig=False, sym=2, save_path=join(save_path, "Vent_sym2.png"))
    test_obj.plot(is_show_fig=False, sym=4, save_path=join(save_path, "Vent_sym4.png"))


if __name__ == "__main__":
    test_HoleUD_vent_plot()
