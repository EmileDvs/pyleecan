# Experimental dataclass generated from Generator/ClassesRef/Slot/HoleM61.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import matplotlib.pyplot as plt
import numpy as np

from . import ParentMissingError
from ..definitions import config_dict
from ..Functions.Geometry.inter_line_circle import inter_line_circle
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Functions.labels import HOLEM_LAB, decode_label
from ..Functions.Plot import (
    ARROW_COLOR,
    ARROW_WIDTH,
    MAIN_LINE_COLOR,
    MAIN_LINE_STYLE,
    MAIN_LINE_WIDTH,
    P_FONT_SIZE,
    SC_FONT_SIZE,
    TEXT_BOX,
    plot_quote,
)
from .arc_1 import Arc1
from .hole_mag import HoleMag
from .lam_hole import LamHole
from .magnet import Magnet
from .segment import Segment
from .surf_line import SurfLine


@dataclass(eq=False)
class HoleM61(HoleMag):
    """Hole M61

    Attributes
    ----------
    W0 : float or None
        Distance beetween two Hole
        Unit: m; Default: None; Minimum: 0
    W1 : float or None
        Magnet width
        Unit: m; Default: None; Minimum: 0
    W2 : float or None
        Magnet width
        Unit: m; Default: None; Minimum: 0
    W3 : float or None
        Tooth width
        Unit: m; Default: None; Minimum: 0
    H0 : float or None
        Distance from the lamination bore
        Unit: m; Default: None; Minimum: 0
    H1 : float or None
        Magnet height
        Unit: m; Default: None; Minimum: 0
    H2 : float or None
        Distance beetween the lamination bore and top of the slot
        Unit: m; Default: None; Minimum: 0
    magnet_0 : Magnet or None
        First Magnet
        Default: None
    magnet_1 : Magnet or None
        Second Magnet
        Default: None
    magnet_2 : Magnet or None
        Third Magnet
        Default: None
    magnet_3 : Magnet or None
        Fourth Magnet
        Default: None
    """

    IS_SYMMETRICAL: ClassVar = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]
    W0: float | None = None
    """Distance beetween two Hole"""
    W1: float | None = None
    """Magnet width"""
    W2: float | None = None
    """Magnet width"""
    W3: float | None = None
    """Tooth width"""
    H0: float | None = None
    """Distance from the lamination bore"""
    H1: float | None = None
    """Magnet height"""
    H2: float | None = None
    """Distance beetween the lamination bore and top of the slot"""
    magnet_0: Magnet | None = None
    """First Magnet"""
    magnet_1: Magnet | None = None
    """Second Magnet"""
    magnet_2: Magnet | None = None
    """Third Magnet"""
    magnet_3: Magnet | None = None
    """Fourth Magnet"""

    # Inlined from Methods.Slot.HoleM61._comp_point_coordinate
    def _comp_point_coordinate(self):
        """Compute the point coordinates needed to plot the Slot.

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object

        Returns
        -------
        point_dict: dict
            A dict of the slot coordinates
        """

        Rbo = self.get_Rbo()

        # comp point coordinate (in complex)

        Z1 = (Rbo - self.H0) + 1j * self.W0 / 2
        Z2 = Z1 + self.H1

        Zc61 = -1j * self.W3 / 2 * np.exp(1j * np.pi / self.Zh)
        Zc62 = (1 - 1j * self.W3 / 2) * np.exp(1j * np.pi / self.Zh)

        Zc63 = Z1 + 1j
        Z6 = inter_line_line(Z1, Zc63, Zc61, Zc62)
        Z6 = Z6[0]

        Zc31 = -1j * (self.W3 / 2 + self.H1) * np.exp(1j * np.pi / self.Zh)
        Zc32 = (1 - 1j * (self.W3 / 2 + self.H1)) * np.exp(1j * np.pi / self.Zh)

        Zc33 = Z2 + 1j
        Z3 = inter_line_line(Z2, Zc33, Zc31, Zc32)
        Z3 = Z3[0]

        # radius Rbo - H2
        Zint5 = inter_line_circle(Z6, Zc61, Rbo - self.H2)
        # Select the point with Re(Z) > 0 and Im(z) >0
        if Zint5[0].real > 0 and Zint5[0].imag > 0:
            Z5 = Zint5[0]
        else:
            Z5 = Zint5[1]

        # radius Rbo - H2
        Zint4 = inter_line_circle(Z3, Zc31, Rbo - self.H2)
        # Select the point with Re(Z) > 0 and Im(z) >0
        if Zint4[0].real > 0 and Zint4[0].imag > 0:
            Z4 = Zint4[0]
        else:
            Z4 = Zint4[1]

        # add possibility to create hole without magnet
        if self.W1 != None and self.W2 != None:
            # draw magnet
            Zm1 = Z1
            Zm2 = Z2
            Zm3 = Z2 + 1j * self.W1
            Zm4 = Z1 + 1j * self.W1

            Zcm1 = ((Z3 + Z4) / 2) * np.exp(-1j * np.pi / self.Zh)
            Zcm2 = Zcm1 + 1j * self.H1

            Zm5 = (Zcm1 - self.W2 / 2) * np.exp(1j * np.pi / self.Zh)
            Zm6 = (Zcm1 + self.W2 / 2) * np.exp(1j * np.pi / self.Zh)
            Zm7 = (Zcm2 + self.W2 / 2) * np.exp(1j * np.pi / self.Zh)
            Zm8 = (Zcm2 - self.W2 / 2) * np.exp(1j * np.pi / self.Zh)

        point_dict = {}
        point_dict["Z1"] = Z1
        point_dict["Z2"] = Z2
        point_dict["Z3"] = Z3
        point_dict["Z4"] = Z4
        point_dict["Z5"] = Z5
        point_dict["Z6"] = Z6

        # add possibility to create hole without magnet
        if self.W1 != None and self.W2 != None:
            point_dict["ZM1"] = Zm1
            point_dict["ZM2"] = Zm2
            point_dict["ZM3"] = Zm3
            point_dict["ZM4"] = Zm4
            point_dict["ZM5"] = Zm5
            point_dict["ZM6"] = Zm6
            point_dict["ZM7"] = Zm7
            point_dict["ZM8"] = Zm8

        # Draw the right hole by symmetry
        point_dict["Z7"] = Z1.conjugate()
        point_dict["Z8"] = Z2.conjugate()
        point_dict["Z9"] = Z3.conjugate()
        point_dict["Z10"] = Z4.conjugate()
        point_dict["Z11"] = Z5.conjugate()
        point_dict["Z12"] = Z6.conjugate()

        # add possibility to create hole without magnet
        if self.W1 != None and self.W2 != None:
            point_dict["ZM9"] = Zm1.conjugate()
            point_dict["ZM10"] = Zm2.conjugate()
            point_dict["ZM11"] = Zm3.conjugate()
            point_dict["ZM12"] = Zm4.conjugate()
            point_dict["ZM13"] = Zm5.conjugate()
            point_dict["ZM14"] = Zm6.conjugate()
            point_dict["ZM15"] = Zm7.conjugate()
            point_dict["ZM16"] = Zm8.conjugate()

        return point_dict

    # Inlined from Methods.Slot.HoleM61.build_geometry
    def build_geometry(self, alpha=0, delta=0, is_simplified=False):
        """Compute the curve (Segment) needed to plot the Slot.
        The ending point of a curve is the starting point of the next curve in
        the list

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object
        alpha : float
            Angle to rotate the slot (Default value = 0) [rad]
        delta : complex
            Complex to translate the slot (Default value = 0)
        is_simplified : bool
            True to avoid line superposition

        Returns
        -------
        surf_list: list
            List of SurfLine needed to draw the HoleM58

        """
        Rbo = self.get_Rbo()

        # Get correct label for surfaces
        lam_label = self.parent.get_label()
        R_id, surf_type = self.get_R_id()
        vent_label = lam_label + "_" + surf_type + "_R" + str(R_id) + "-"
        mag_label = lam_label + "_" + HOLEM_LAB + "_R" + str(R_id) + "-"

        # Get all the points
        point_dict = self._comp_point_coordinate()
        Z1 = point_dict["Z1"]
        Z2 = point_dict["Z2"]
        Z3 = point_dict["Z3"]
        Z4 = point_dict["Z4"]
        Z5 = point_dict["Z5"]
        Z6 = point_dict["Z6"]

        Z7 = point_dict["Z7"]
        Z8 = point_dict["Z8"]
        Z9 = point_dict["Z9"]
        Z10 = point_dict["Z10"]
        Z11 = point_dict["Z11"]
        Z12 = point_dict["Z12"]

        # add possibility to create hole without magnet
        if self.W1 != None and self.W2 != None:
            ZM1 = point_dict["ZM1"]
            ZM2 = point_dict["ZM2"]
            ZM3 = point_dict["ZM3"]
            ZM4 = point_dict["ZM4"]
            ZM5 = point_dict["ZM5"]
            ZM6 = point_dict["ZM6"]
            ZM7 = point_dict["ZM7"]
            ZM8 = point_dict["ZM8"]
            ZM9 = point_dict["ZM9"]
            ZM10 = point_dict["ZM10"]
            ZM11 = point_dict["ZM11"]
            ZM12 = point_dict["ZM12"]
            ZM13 = point_dict["ZM13"]
            ZM14 = point_dict["ZM14"]
            ZM15 = point_dict["ZM15"]
            ZM16 = point_dict["ZM16"]

        surf_list = []
        # Create all the surfaces for all the cases

        # surface Hole without magnet
        curve_list = []
        curve_list.append(Segment(Z1, Z2))
        curve_list.append(Segment(Z2, Z3))
        curve_list.append(Segment(Z3, Z4))
        curve_list.append(
            Arc1(
                begin=Z4,
                end=Z5,
                radius=Rbo - self.H2,
                is_trigo_direction=True,
            )
        )
        curve_list.append(Segment(Z5, Z6))
        curve_list.append(Segment(Z6, Z1))
        point_ref = (Z3 + Z6) / 2
        S2 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # surface Hole without magnet
        curve_list = []
        curve_list.append(Segment(Z7, Z8))
        curve_list.append(Segment(Z8, Z9))
        curve_list.append(Segment(Z9, Z10))
        curve_list.append(
            Arc1(
                begin=Z10,
                end=Z11,
                radius=Rbo - self.H2,
                is_trigo_direction=True,
            )
        )
        curve_list.append(Segment(Z11, Z12))
        curve_list.append(Segment(Z12, Z7))

        point_ref = (Z9 + Z12) / 2
        S1 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # add possibility to create hole without magnet
        if self.W1 != None and self.W2 != None:
            # Magnet_2 surface
            curve_list = []
            curve_list.append(Segment(ZM1, ZM2))
            curve_list.append(Segment(ZM2, ZM3))
            curve_list.append(Segment(ZM3, ZM4))
            curve_list.append(Segment(ZM4, ZM1))
            point_ref = (ZM1 + ZM3) / 2
            SM2 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_2 and magnet_3
            curve_list = []
            curve_list.append(Segment(ZM4, ZM3))
            curve_list.append(Segment(ZM3, Z3))
            curve_list.append(Segment(Z3, ZM5))
            curve_list.append(Segment(ZM5, ZM8))
            curve_list.append(Segment(ZM8, Z6))
            curve_list.append(Segment(Z6, ZM4))
            point_ref = (Z3 + ZM4) / 2
            S23 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Surface for magnet_3
            curve_list = []
            curve_list.append(Segment(ZM5, ZM6))
            curve_list.append(Segment(ZM6, ZM7))
            curve_list.append(Segment(ZM7, ZM8))
            curve_list.append(Segment(ZM8, ZM5))

            point_ref = (ZM5 + ZM7) / 2
            SM3 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_3 and top of slot
            curve_list = []
            curve_list.append(Segment(ZM6, Z4))
            curve_list.append(
                Arc1(begin=Z4, end=Z5, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z5, ZM7))
            curve_list.append(Segment(ZM7, ZM6))

            point_ref = (Z5 + ZM6) / 2
            S3T = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_2 but with magnet_3
            curve_list = []
            curve_list.append(Segment(Z1, Z2))
            curve_list.append(Segment(Z2, Z3))
            curve_list.append(Segment(Z3, ZM5))
            curve_list.append(Segment(ZM5, ZM8))
            curve_list.append(Segment(ZM8, Z6))
            curve_list.append(Segment(Z6, Z1))
            point_ref = (Z1 + Z3) / 2
            SW02 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_3 but with magnet_2
            curve_list = []
            curve_list.append(Segment(ZM3, Z3))
            curve_list.append(Segment(Z3, Z4))
            curve_list.append(
                Arc1(begin=Z4, end=Z5, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z5, Z6))
            curve_list.append(Segment(Z6, ZM4))
            curve_list.append(Segment(ZM4, ZM3))

            point_ref = (Z5 + Z3) / 2
            SW03 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Magnet_1 surface
            curve_list = []
            curve_list.append(Segment(ZM9, ZM10))
            curve_list.append(Segment(ZM10, ZM11))
            curve_list.append(Segment(ZM11, ZM12))
            curve_list.append(Segment(ZM12, ZM9))
            point_ref = (ZM10 + ZM12) / 2
            SM1 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_1 and magnet_0
            curve_list = []
            curve_list.append(Segment(ZM11, ZM12))
            curve_list.append(Segment(ZM12, Z12))
            curve_list.append(Segment(Z12, ZM16))
            curve_list.append(Segment(ZM16, ZM13))
            curve_list.append(Segment(ZM13, Z9))
            curve_list.append(Segment(Z9, ZM11))
            point_ref = (Z9 + ZM12) / 2
            S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Surface for magnet_0
            curve_list = []
            curve_list.append(Segment(ZM13, ZM14))
            curve_list.append(Segment(ZM14, ZM15))
            curve_list.append(Segment(ZM15, ZM16))
            curve_list.append(Segment(ZM16, ZM13))

            point_ref = (ZM13 + ZM15) / 2
            SM0 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_0 and top of slot
            curve_list = []
            curve_list.append(Segment(ZM15, Z11))
            curve_list.append(
                Arc1(begin=Z11, end=Z10, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z10, ZM14))
            curve_list.append(Segment(ZM14, ZM15))

            point_ref = (Z10 + ZM15) / 2
            S0T = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_1 but with magnet_0
            curve_list = []
            curve_list.append(Segment(Z7, Z8))
            curve_list.append(Segment(Z8, Z9))
            curve_list.append(Segment(Z9, ZM13))
            curve_list.append(Segment(ZM13, ZM16))
            curve_list.append(Segment(ZM16, Z12))
            curve_list.append(Segment(Z12, Z7))
            point_ref = (Z12 + Z8) / 2
            SW01 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_0 but with magnet_1
            curve_list = []
            curve_list.append(Segment(ZM11, Z9))
            curve_list.append(Segment(Z9, Z10))
            curve_list.append(
                Arc1(begin=Z10, end=Z11, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z11, Z12))
            curve_list.append(Segment(Z12, ZM12))
            curve_list.append(Segment(ZM12, ZM11))

            point_ref = (Z10 + Z12) / 2
            SW00 = SurfLine(line_list=curve_list, point_ref=point_ref)

        # Create the surface list by selecting the correct ones

        # add possibility to create hole without magnet
        surf_list = []
        if self.W1 != None and self.W2 != None:
            if self.magnet_0:
                SM0.label = mag_label + "T0-S0"
                S0T.label = vent_label + "T0-S0"
                surf_list += [SM0, S0T]
                if self.magnet_1:
                    SM1.label = mag_label + "T1-S0"
                    S10.label = vent_label + "T1-S0"
                    surf_list += [
                        S10,
                        SM1,
                    ]
                    if self.magnet_2:
                        SM2.label = mag_label + "T2-S0"
                        surf_list += [SM2]
                        if self.magnet_3:
                            SM3.label = mag_label + "T3-S0"
                            S23.label = vent_label + "T2-S0"
                            S3T.label = vent_label + "T3-S0"
                            surf_list += [S23, SM3, S3T]
                        else:
                            SW03.label = vent_label + "T2-S0"
                            surf_list += [SW03]
                    else:
                        if self.magnet_3:
                            SW02.label = vent_label + "T2-S0"
                            SM3.label = mag_label + "T2-S0"
                            S3T.label = vent_label + "T3-S0"
                            surf_list += [SW02, SM3, S3T]
                        else:
                            S2.label = vent_label + "T2-S0"
                            surf_list += [S2]

                else:
                    SW01.label = vent_label + "T1-S0"
                    surf_list += [SW01]
                    if self.magnet_2:
                        SM2.label = mag_label + "T1-S0"
                        surf_list += [SM2]
                        if self.magnet_3:
                            SM3.label = mag_label + "T2-S0"
                            S23.label = vent_label + "T1-S0"
                            S3T.label = vent_label + "T3-S0"
                            surf_list += [S23, SM3, S3T]
                        else:
                            SW03.label = vent_label + "T2-S0"
                            surf_list += [SW03]
                    else:
                        if self.magnet_3:
                            SW02.label = vent_label + "T2-S0"
                            SM3.label = mag_label + "T1-S0"
                            S3T.label = vent_label + "T3-S0"
                            surf_list += [SW02, SM3, S3T]
                        else:
                            S2.label = vent_label + "T1-S0"
                            surf_list += [S2]
            else:
                if self.magnet_1:
                    SW00.label = vent_label + "T0-S0"
                    SM1.label = mag_label + "T0-S0"
                    surf_list += [SW00, SM1]
                    if self.magnet_2:
                        SM2.label = mag_label + "T1-S0"
                        surf_list += [SM2]
                        if self.magnet_3:
                            SM3.label = mag_label + "T2-S0"
                            S23.label = vent_label + "T1-S0"
                            S3T.label = vent_label + "T2-S0"
                            surf_list += [S23, SM3, S3T]
                        else:
                            SW03.label = vent_label + "T1-S0"
                            surf_list += [SW03]
                    else:
                        if self.magnet_3:
                            SW02.label = vent_label + "T1-S0"
                            SM3.label = mag_label + "T1-S0"
                            S3T.label = vent_label + "T2-S0"
                            surf_list += [SW02, SM3, S3T]
                        else:
                            S2.label = vent_label + "T1-S0"
                            surf_list += [S2]
                else:
                    S1.label = vent_label + "T0-S0"
                    surf_list += [S1]
                    if self.magnet_2:
                        SM2.label = mag_label + "T0-S0"
                        surf_list += [SM2]
                        if self.magnet_3:
                            SM3.label = mag_label + "T1-S0"
                            S23.label = vent_label + "T1-S0"
                            S3T.label = vent_label + "T2-S0"
                            surf_list += [S23, SM3, S3T]
                        else:
                            SW03.label = vent_label + "T1-S0"
                            surf_list += [SW03]
                    else:
                        if self.magnet_3:
                            SW02.label = vent_label + "T1-S0"
                            SM3.label = mag_label + "T1-S0"
                            S3T.label = vent_label + "T2-S0"
                            surf_list += [SW02, SM3, S3T]
                        else:
                            S2.label = vent_label + "T1-S0"
                            surf_list += [S2]

        else:
            S1.label = vent_label + "T0-S0"
            surf_list += [S1]
            S2.label = vent_label + "T1-S0"
            surf_list += [S2]

        # Apply the transformations
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Slot.HoleM61.check
    def check(self):
        """Check that the HoleM61 object is correct

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object

        Returns
        -------
        None

        Raises
        _______
        S61_WCheckError
            You must have H1 < H0
            You must have H2 < H0
        """
        # Check that everything is set
        if self.W0 is None:
            raise S61_NoneError("You must set W0 !")

        # add possibility to create hole without magnet
        # elif self.W1 is None:
        #    raise S61_NoneError("You must set W1 !")
        # elif self.W2 is None:
        #    raise S61_NoneError("You must set W2 !")
        elif self.W3 is None:
            raise S61_NoneError("You must set W3 !")
        elif self.H0 is None:
            raise S61_NoneError("You must set H0 !")
        elif self.H1 is None:
            raise S61_NoneError("You must set H1 !")
        elif self.H2 is None:
            raise S61_NoneError("You must set H2 !")

        if self.H1 > self.H0:
            raise S61_WCheckError("You must have H1 < H0")

        if self.H2 > self.H0:
            raise S61_WCheckError("You must have H2 < H0")

    # Inlined from Methods.Slot.HoleM61.comp_magnetization_dict
    def comp_magnetization_dict(self, is_north=True):
        """Compute the dictionary of the magnetization direction of the magnets (key=magnet_X, value=angle[rad])
        Mangetization angle with Hole centered on Ox axis

        Parameters
        ----------
        self : HoleM61
            a HoleM61 object
        is_north: True
            True: comp north magnetization, else add pi [rad]

        Returns
        -------
        mag_dict: dict
            magnetization dictionary (key=magnet_X, value=angle[rad])
        """

        # Comp magnet
        point_dict = self._comp_point_coordinate()

        mag_dict = {}
        S0 = Segment(point_dict["ZM7"], point_dict["ZM8"])
        mag_dict["magnet_0"] = S0.comp_normal()
        S1 = Segment(point_dict["ZM4"], point_dict["ZM1"])
        mag_dict["magnet_1"] = S1.comp_normal()
        S2 = Segment(point_dict["ZM9"], point_dict["ZM12"])
        mag_dict["magnet_2"] = S2.comp_normal()
        S3 = Segment(point_dict["ZM16"], point_dict["ZM15"])
        mag_dict["magnet_3"] = S3.comp_normal()

        if not is_north:
            mag_dict["magnet_0"] += np.pi
            mag_dict["magnet_1"] += np.pi
            mag_dict["magnet_2"] += np.pi
            mag_dict["magnet_3"] += np.pi

        if self.magnetization_dict_offset is not None:
            for key, value in self.magnetization_dict_offset:
                mag_dict[key] += value

        return mag_dict

    # Inlined from Methods.Slot.HoleM61.comp_radius
    def comp_radius(self):
        """Compute the radius of the min and max circle that contains the slot

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object

        Returns
        -------
        (Rmin,Rmax): tuple
            Radius of the circle that contains the slot [m]
        """

        Rbo = self.get_Rbo()

        Rmax = Rbo - self.H2
        Rmin = np.abs((Rbo - self.H0) + 1j * self.W0 / 2)

        return (Rmin, Rmax)

    # Inlined from Methods.Slot.HoleM61.comp_surface_magnet_id
    def comp_surface_magnet_id(self, index):
        """Compute the surface of the hole magnet of the corresponding index

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object
        index : int
            Index of the magnet to compute the surface

        Returns
        -------
        Smag: float
            Surface of the Magnet [m**2]
        """
        # define sum all surface
        label = "magnet_" + str(index)

        if index in [1, 2] and getattr(self, label) is not None:
            return self.W1 * self.H1
        if index in [0, 3] and getattr(self, label) is not None:
            return self.W2 * self.H1
        if index not in [0, 1, 2, 3]:
            raise Exception("Error index isn't equal at 0, 1, 2 or 3")
        return 0

    # Inlined from Methods.Slot.HoleM61.has_magnet
    def has_magnet(self):
        """Return if the Hole has magnets

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object

        Returns
        -------
        has_magnet : bool
            True if the magnets are not None
        """

        return (
            self.magnet_0 is not None
            or self.magnet_1 is not None
            or self.magnet_2 is not None
            or self.magnet_3 is not None
        )

    # Inlined from Methods.Slot.HoleM61.plot_schematics
    def plot_schematics(
        self,
        is_return_default=False,
        is_default=False,
        is_add_point_label=False,
        is_add_schematics=True,
        is_add_main_line=True,
        type_add_active=True,
        save_path=None,
        is_show_fig=True,
        fig=None,
        ax=None,
    ):
        """Plot the schematics of the slot

        Parameters
        ----------
        self : HoleM61
            A HoleM61 object
        is_default : bool
            True: plot default schematics, else use current slot values
        is_return_default : bool
            True: return the default lamination used for the schematics (skip plot)
        is_add_point_label : bool
            True to display the name of the points (Z1, Z2....)
        is_add_schematics : bool
            True to display the schematics information (W0, H0...)
        is_add_main_line : bool
            True to display "main lines" (slot opening and 0x axis)
        type_add_active : int
            0: No active surface, 1: active surface as winding, 2: active surface as magnet
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_show_fig : bool
            To call show at the end of the method
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the schematics
        ax : Matplotlib.axes.Axes object
            Axis containing the schematics
        -------
        lam : LamHole / LamSlot
            Default lamination used for the schematics
        """

        # Use some default parameter
        if is_default:
            hole = type(self)(
                Zh=4,
                W0=2e-2,
                W1=2e-2,
                W2=20e-3,
                W3=12e-3,
                H0=61e-3,
                H1=10e-3,
                H2=10e-3,
            )
            lam = LamHole(
                Rint=0.03, Rext=0.12, is_internal=True, is_stator=False, hole=[hole]
            )
            if is_return_default:
                return lam
            else:
                return hole.plot_schematics(
                    is_default=False,
                    is_return_default=False,
                    is_add_point_label=is_add_point_label,
                    is_add_schematics=is_add_schematics,
                    is_add_main_line=is_add_main_line,
                    type_add_active=type_add_active,
                    save_path=save_path,
                    is_show_fig=is_show_fig,
                    fig=fig,
                    ax=ax,
                )
        # Getting the main plot
        if self.parent is None:
            raise ParentMissingError("Error: The hole is not inside a Lamination")
        lam = self.parent

        # Remove the magnets
        if type_add_active == 0:
            lam.hole[0].remove_magnet()

        alpha = np.pi / 2  # To rotate the schematics
        fig, ax = lam.plot(
            alpha=np.pi / self.Zh + alpha,
            is_show_fig=False,
            is_lam_only=type_add_active == 0,
            fig=fig,
            ax=ax,
        )  # center hole on Ox axis
        sp = 2 * np.pi / self.Zh
        Rbo = self.get_Rbo()
        point_dict = self._comp_point_coordinate()

        # Adding point label
        if is_add_point_label:
            for name, Z in point_dict.items():
                Z = Z * np.exp(1j * alpha)
                ax.text(
                    Z.real,
                    Z.imag,
                    name,
                    fontsize=P_FONT_SIZE,
                    bbox=TEXT_BOX,
                )

        # Adding schematics
        if is_add_schematics:
            Zint = inter_line_circle(
                (point_dict["Z5"] + point_dict["Z4"]) / 2,
                (point_dict["ZM7"] + point_dict["ZM6"]) / 2,
                Rbo,
            )
            # Select the point with Re(Z) > 0 and Im(z) >0
            if Zint[0].real > 0 and Zint[0].imag > 0:
                Zc = Zint[0]
            else:
                Zc = Zint[1]

            # H2
            line = Segment(
                (point_dict["Z5"] + point_dict["Z4"]) / 2 * np.exp(1j * alpha),
                Zc * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H2",
                offset_label=1j * self.H2 * 0.6 - self.H2 * 0.3,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )

            Zint = inter_line_circle(
                (point_dict["Z10"] + point_dict["Z11"]) / 2,
                (point_dict["ZM14"] + point_dict["ZM15"]) / 2,
                Rbo,
            )
            # Select the point with Re(Z) > 0 and Im(z) >0
            if Zint[0].real > 0 and Zint[0].imag > 0:
                Zc = Zint[0]
            else:
                Zc = Zint[1]

            # H2
            line = Segment(
                (point_dict["Z10"] + point_dict["Z11"]) / 2 * np.exp(1j * alpha),
                Zc * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H2",
                offset_label=1j * self.H2 * 0.6 - self.H2 * 0.3,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # W3
            line = Segment(
                (point_dict["Z5"] + point_dict["Z6"]) / 2 * np.exp(1j * alpha),
                (point_dict["Z12"] + point_dict["Z11"])
                / 2
                * np.exp(1j * sp)
                * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W3",
                offset_label=-self.H1 * 0.75 + 1j * self.H1 * 0.3,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            line = Segment(
                (point_dict["Z12"] + point_dict["Z11"]) / 2 * np.exp(1j * alpha),
                (point_dict["Z5"] + point_dict["Z6"])
                / 2
                * np.exp(-1j * sp)
                * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W3",
                offset_label=1j * self.H1 * 0.3 + self.H1 * 0.15,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )

            # magnet width only if magnet is visible
            if type_add_active == 2:
                # Add magnet Id on the corresponding surfaces
                for surf in self.build_geometry():
                    label = surf.label
                    label_dict = decode_label(label)
                    point_ref = surf.point_ref

                    if HOLEM_LAB in label_dict["surf_type"]:  # LamHole
                        T_id = label_dict["T_id"]
                        point_ref = point_ref * np.exp(1j * alpha)
                        ax.text(
                            point_ref.real,
                            point_ref.imag,
                            T_id,
                        )

                # W2
                line = Segment(
                    point_dict["ZM6"] * np.exp(1j * alpha),
                    point_dict["ZM5"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=1j * self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                line = Segment(
                    point_dict["ZM13"] * np.exp(1j * alpha),
                    point_dict["ZM14"] * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=ARROW_COLOR,
                    linewidth=ARROW_WIDTH,
                    label="W2",
                    offset_label=1j * self.H1 * 0.6 - self.H1 * 0.5,
                    is_arrow=True,
                    fontsize=SC_FONT_SIZE,
                )

                # W1
                Zlim1 = point_dict["ZM1"] - self.H1
                Zlim2 = point_dict["ZM4"] - self.H1
                plot_quote(
                    point_dict["ZM1"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["ZM4"] * np.exp(1j * alpha),
                    offset_label=-1j * self.H1 * 0.6 - 0.2 * self.W2,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )

                Zlim1 = point_dict["ZM9"] - self.H1
                Zlim2 = point_dict["ZM12"] - self.H1
                plot_quote(
                    point_dict["ZM9"] * np.exp(1j * alpha),
                    Zlim1 * np.exp(1j * alpha),
                    Zlim2 * np.exp(1j * alpha),
                    point_dict["ZM12"] * np.exp(1j * alpha),
                    offset_label=-1j * self.H1 * 0.6 - 0.2 * self.W2,
                    fig=fig,
                    ax=ax,
                    label="W1",
                )

            # W0
            line = Segment(
                (point_dict["Z1"] + point_dict["Z2"]) * np.exp(1j * alpha) / 2,
                (point_dict["Z8"] + point_dict["Z7"]) * np.exp(1j * alpha) / 2,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="W0",
                offset_label=1j * self.H1 * 0.5 + self.W0 * 0.1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H0
            line = Segment(
                Rbo * np.exp(1j * alpha),
                (point_dict["Z1"] + point_dict["Z7"]) * np.exp(1j * alpha) / 2,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H0",
                offset_label=self.W0 * 0.1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )
            # H1
            line = Segment(
                (point_dict["Z3"] + point_dict["Z2"]) * np.exp(1j * alpha) / 2,
                (point_dict["Z3"] + point_dict["Z2"]) * np.exp(1j * alpha) / 2
                - 1j * self.H1,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H1",
                offset_label=self.H1 * 0.3 - 0.012 - 0.1j * self.H1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )

            line = Segment(
                (point_dict["Z8"] + point_dict["Z9"]) * np.exp(1j * alpha) / 2,
                (point_dict["Z8"] + point_dict["Z9"]) * np.exp(1j * alpha) / 2
                - 1j * self.H1,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=ARROW_COLOR,
                linewidth=ARROW_WIDTH,
                label="H1",
                offset_label=self.H1 * 0.3 - 0.1j * self.H1,
                is_arrow=True,
                fontsize=SC_FONT_SIZE,
            )

        if is_add_main_line:
            # Ox axis
            line = Segment(0, lam.Rext * 1.5 * np.exp(1j * alpha))
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            # Tooth axis
            line = Segment(0, lam.Rext * 1.5 * np.exp(1j * sp / 2) * np.exp(1j * alpha))
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            line = Segment(
                0, lam.Rext * 1.5 * np.exp(-1j * sp / 2) * np.exp(1j * alpha)
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

            # H2
            line = Arc1(
                begin=point_dict["Z11"] * np.exp(1j * alpha * 0.8),
                end=point_dict["Z5"] * np.exp(1.2 * 1j * alpha),
                radius=Rbo - self.H2,
                is_trigo_direction=True,
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

            # H0 lines
            line = Segment(
                point_dict["Z2"] * np.exp(1j * alpha),
                point_dict["Z8"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

            line = Segment(
                point_dict["Z1"] * np.exp(1j * alpha),
                point_dict["Z7"] * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )

            if type_add_active == 2:
                # W2 lines
                line = Segment(
                    (point_dict["ZM6"] + point_dict["ZM5"]) * np.exp(1j * alpha) / 2,
                    (point_dict["ZM7"] + point_dict["ZM8"]) * np.exp(1j * alpha) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    (point_dict["ZM13"] + point_dict["ZM14"]) * np.exp(1j * alpha) / 2,
                    (point_dict["ZM15"] + point_dict["ZM16"]) * np.exp(1j * alpha) / 2,
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            # W3 parralel
            line = Segment(
                point_dict["Z6"] * np.exp(1j * alpha),
                point_dict["Z12"] * np.exp(1j * sp) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            if type_add_active == 2:
                line = Segment(
                    point_dict["ZM8"] * np.exp(1j * alpha),
                    point_dict["ZM16"] * np.exp(1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["ZM7"] * np.exp(1j * alpha),
                    point_dict["ZM15"] * np.exp(1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

            line = Segment(
                point_dict["Z12"] * np.exp(1j * alpha),
                point_dict["Z6"] * np.exp(-1j * sp) * np.exp(1j * alpha),
            )
            line.plot(
                fig=fig,
                ax=ax,
                color=MAIN_LINE_COLOR,
                linestyle=MAIN_LINE_STYLE,
                linewidth=MAIN_LINE_WIDTH,
            )
            if type_add_active == 2:
                line = Segment(
                    point_dict["ZM16"] * np.exp(1j * alpha),
                    point_dict["ZM8"] * np.exp(-1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )
                line = Segment(
                    point_dict["ZM15"] * np.exp(1j * alpha),
                    point_dict["ZM7"] * np.exp(-1j * sp) * np.exp(1j * alpha),
                )
                line.plot(
                    fig=fig,
                    ax=ax,
                    color=MAIN_LINE_COLOR,
                    linestyle=MAIN_LINE_STYLE,
                    linewidth=MAIN_LINE_WIDTH,
                )

        # Zooming and cleaning
        W = (point_dict["Z1"] * np.exp(1j * sp)).imag
        Rint = self.parent.Rint
        Rext = self.parent.Rext

        ax.axis("equal")
        ax.set_ylim(Rint, Rext)
        ax.set_xlim(-W, W)
        manager = plt.get_current_fig_manager()
        if manager is not None:
            manager.set_window_title(type(self).__name__ + " Schematics")
        ax.set_title("")
        ax.get_legend().remove()
        ax.set_axis_off()
        fig.tight_layout()

        # Save / Show
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)

        if is_show_fig:
            fig.show()
        return fig, ax

    # Inlined from Methods.Slot.HoleM61.remove_magnet
    def remove_magnet(self):
        """Remove the magnet (set to None) of the Hole

        Parameters
        ----------
        self : HoleM61
            a HoleM61 object
        """

        self.magnet_0 = None
        self.magnet_1 = None
        self.magnet_2 = None
        self.magnet_3 = None

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """

    class S61_WCheckError(SlotCheckError):
        """ """

    class S61_NoneError(SlotCheckError):
        """Raised when a propery of HoleM58 is None"""


MachineCheckError = HoleM61.MachineCheckError
LaminationCheckError = HoleM61.LaminationCheckError
SlotCheckError = HoleM61.SlotCheckError
S61_WCheckError = HoleM61.S61_WCheckError
S61_NoneError = HoleM61.S61_NoneError
