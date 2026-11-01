# File generated according to Generator/ClassesRef/Slot/HoleM61.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Slot/HoleM61"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes import ParentMissingError
from pyleecan.Classes.Arc1 import Arc1
from pyleecan.Classes.HoleMag import HoleMag
from pyleecan.Classes.LamHole import LamHole
from pyleecan.Classes.Segment import Segment
from pyleecan.Classes.SurfLine import SurfLine
from pyleecan.Classes._check import check_var

from pyleecan.definitions import config_dict

from pyleecan.Functions.Geometry.inter_line_circle import inter_line_circle
from pyleecan.Functions.Geometry.inter_line_line import inter_line_line
from pyleecan.Functions.Load.import_class import import_class
from pyleecan.Functions.Plot import (
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
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.labels import HOLEM_LAB, decode_label
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save


class HoleM61(HoleMag):
    """Hole M61"""

    VERSION = 1
    IS_SYMMETRICAL = 1
    MAGNET_COLOR = config_dict["PLOT"]["COLOR_DICT"]["MAGNET_COLOR"]

    # cf Methods.Slot.HoleM61._comp_point_coordinate
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

        point_dict = dict()
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

    # cf Methods.Slot.HoleM61.build_geometry
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

        surf_list = list()
        # Create all the surfaces for all the cases

        # surface Hole without magnet
        curve_list = list()
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
        curve_list = list()
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
            curve_list = list()
            curve_list.append(Segment(ZM1, ZM2))
            curve_list.append(Segment(ZM2, ZM3))
            curve_list.append(Segment(ZM3, ZM4))
            curve_list.append(Segment(ZM4, ZM1))
            point_ref = (ZM1 + ZM3) / 2
            SM2 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_2 and magnet_3
            curve_list = list()
            curve_list.append(Segment(ZM4, ZM3))
            curve_list.append(Segment(ZM3, Z3))
            curve_list.append(Segment(Z3, ZM5))
            curve_list.append(Segment(ZM5, ZM8))
            curve_list.append(Segment(ZM8, Z6))
            curve_list.append(Segment(Z6, ZM4))
            point_ref = (Z3 + ZM4) / 2
            S23 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Surface for magnet_3
            curve_list = list()
            curve_list.append(Segment(ZM5, ZM6))
            curve_list.append(Segment(ZM6, ZM7))
            curve_list.append(Segment(ZM7, ZM8))
            curve_list.append(Segment(ZM8, ZM5))

            point_ref = (ZM5 + ZM7) / 2
            SM3 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_3 and top of slot
            curve_list = list()
            curve_list.append(Segment(ZM6, Z4))
            curve_list.append(
                Arc1(begin=Z4, end=Z5, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z5, ZM7))
            curve_list.append(Segment(ZM7, ZM6))

            point_ref = (Z5 + ZM6) / 2
            S3T = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_2 but with magnet_3
            curve_list = list()
            curve_list.append(Segment(Z1, Z2))
            curve_list.append(Segment(Z2, Z3))
            curve_list.append(Segment(Z3, ZM5))
            curve_list.append(Segment(ZM5, ZM8))
            curve_list.append(Segment(ZM8, Z6))
            curve_list.append(Segment(Z6, Z1))
            point_ref = (Z1 + Z3) / 2
            SW02 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_3 but with magnet_2
            curve_list = list()
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
            curve_list = list()
            curve_list.append(Segment(ZM9, ZM10))
            curve_list.append(Segment(ZM10, ZM11))
            curve_list.append(Segment(ZM11, ZM12))
            curve_list.append(Segment(ZM12, ZM9))
            point_ref = (ZM10 + ZM12) / 2
            SM1 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_1 and magnet_0
            curve_list = list()
            curve_list.append(Segment(ZM11, ZM12))
            curve_list.append(Segment(ZM12, Z12))
            curve_list.append(Segment(Z12, ZM16))
            curve_list.append(Segment(ZM16, ZM13))
            curve_list.append(Segment(ZM13, Z9))
            curve_list.append(Segment(Z9, ZM11))
            point_ref = (Z9 + ZM12) / 2
            S10 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Surface for magnet_0
            curve_list = list()
            curve_list.append(Segment(ZM13, ZM14))
            curve_list.append(Segment(ZM14, ZM15))
            curve_list.append(Segment(ZM15, ZM16))
            curve_list.append(Segment(ZM16, ZM13))

            point_ref = (ZM13 + ZM15) / 2
            SM0 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface between magnet_0 and top of slot
            curve_list = list()
            curve_list.append(Segment(ZM15, Z11))
            curve_list.append(
                Arc1(begin=Z11, end=Z10, radius=Rbo - self.H2, is_trigo_direction=True)
            )
            curve_list.append(Segment(Z10, ZM14))
            curve_list.append(Segment(ZM14, ZM15))

            point_ref = (Z10 + ZM15) / 2
            S0T = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_1 but with magnet_0
            curve_list = list()
            curve_list.append(Segment(Z7, Z8))
            curve_list.append(Segment(Z8, Z9))
            curve_list.append(Segment(Z9, ZM13))
            curve_list.append(Segment(ZM13, ZM16))
            curve_list.append(Segment(ZM16, Z12))
            curve_list.append(Segment(Z12, Z7))
            point_ref = (Z12 + Z8) / 2
            SW01 = SurfLine(line_list=curve_list, point_ref=point_ref)

            # Air surface without magnet_0 but with magnet_1
            curve_list = list()
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
        surf_list = list()
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

    # cf Methods.Slot.HoleM61.check
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

    # cf Methods.Slot.HoleM61.comp_magnetization_dict
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

        mag_dict = dict()
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

    # cf Methods.Slot.HoleM61.comp_radius
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

    # cf Methods.Slot.HoleM61.comp_surface_magnet_id
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

    # cf Methods.Slot.HoleM61.has_magnet
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

    # cf Methods.Slot.HoleM61.plot_schematics
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

    # cf Methods.Slot.HoleM61.remove_magnet
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        W0=None,
        W1=None,
        W2=None,
        W3=None,
        H0=None,
        H1=None,
        H2=None,
        magnet_0=-1,
        magnet_1=-1,
        magnet_2=-1,
        magnet_3=-1,
        Zh=36,
        mat_void=-1,
        magnetization_dict_offset=None,
        Alpha0=0,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "W0" in list(init_dict.keys()):
                W0 = init_dict["W0"]
            if "W1" in list(init_dict.keys()):
                W1 = init_dict["W1"]
            if "W2" in list(init_dict.keys()):
                W2 = init_dict["W2"]
            if "W3" in list(init_dict.keys()):
                W3 = init_dict["W3"]
            if "H0" in list(init_dict.keys()):
                H0 = init_dict["H0"]
            if "H1" in list(init_dict.keys()):
                H1 = init_dict["H1"]
            if "H2" in list(init_dict.keys()):
                H2 = init_dict["H2"]
            if "magnet_0" in list(init_dict.keys()):
                magnet_0 = init_dict["magnet_0"]
            if "magnet_1" in list(init_dict.keys()):
                magnet_1 = init_dict["magnet_1"]
            if "magnet_2" in list(init_dict.keys()):
                magnet_2 = init_dict["magnet_2"]
            if "magnet_3" in list(init_dict.keys()):
                magnet_3 = init_dict["magnet_3"]
            if "Zh" in list(init_dict.keys()):
                Zh = init_dict["Zh"]
            if "mat_void" in list(init_dict.keys()):
                mat_void = init_dict["mat_void"]
            if "magnetization_dict_offset" in list(init_dict.keys()):
                magnetization_dict_offset = init_dict["magnetization_dict_offset"]
            if "Alpha0" in list(init_dict.keys()):
                Alpha0 = init_dict["Alpha0"]
        # Set the properties (value check and convertion are done in setter)
        self.W0 = W0
        self.W1 = W1
        self.W2 = W2
        self.W3 = W3
        self.H0 = H0
        self.H1 = H1
        self.H2 = H2
        self.magnet_0 = magnet_0
        self.magnet_1 = magnet_1
        self.magnet_2 = magnet_2
        self.magnet_3 = magnet_3
        # Call HoleMag init
        super(HoleM61, self).__init__(
            Zh=Zh,
            mat_void=mat_void,
            magnetization_dict_offset=magnetization_dict_offset,
            Alpha0=Alpha0,
        )
        # The class is frozen (in HoleMag init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        HoleM61_str = ""
        # Get the properties inherited from HoleMag
        HoleM61_str += super(HoleM61, self).__str__()
        HoleM61_str += "W0 = " + str(self.W0) + linesep
        HoleM61_str += "W1 = " + str(self.W1) + linesep
        HoleM61_str += "W2 = " + str(self.W2) + linesep
        HoleM61_str += "W3 = " + str(self.W3) + linesep
        HoleM61_str += "H0 = " + str(self.H0) + linesep
        HoleM61_str += "H1 = " + str(self.H1) + linesep
        HoleM61_str += "H2 = " + str(self.H2) + linesep
        if self.magnet_0 is not None:
            tmp = self.magnet_0.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM61_str += "magnet_0 = " + tmp
        else:
            HoleM61_str += "magnet_0 = None" + linesep + linesep
        if self.magnet_1 is not None:
            tmp = self.magnet_1.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM61_str += "magnet_1 = " + tmp
        else:
            HoleM61_str += "magnet_1 = None" + linesep + linesep
        if self.magnet_2 is not None:
            tmp = self.magnet_2.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM61_str += "magnet_2 = " + tmp
        else:
            HoleM61_str += "magnet_2 = None" + linesep + linesep
        if self.magnet_3 is not None:
            tmp = self.magnet_3.__str__().replace(linesep, linesep + "\t").rstrip("\t")
            HoleM61_str += "magnet_3 = " + tmp
        else:
            HoleM61_str += "magnet_3 = None" + linesep + linesep
        return HoleM61_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from HoleMag
        if not super(HoleM61, self).__eq__(other):
            return False
        if other.W0 != self.W0:
            return False
        if other.W1 != self.W1:
            return False
        if other.W2 != self.W2:
            return False
        if other.W3 != self.W3:
            return False
        if other.H0 != self.H0:
            return False
        if other.H1 != self.H1:
            return False
        if other.H2 != self.H2:
            return False
        if other.magnet_0 != self.magnet_0:
            return False
        if other.magnet_1 != self.magnet_1:
            return False
        if other.magnet_2 != self.magnet_2:
            return False
        if other.magnet_3 != self.magnet_3:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from HoleMag
        diff_list.extend(
            super(HoleM61, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._W0 is not None
            and self._W0 is not None
            and np.isnan(other._W0)
            and np.isnan(self._W0)
        ):
            pass
        elif other._W0 != self._W0:
            if is_add_value:
                val_str = " (self=" + str(self._W0) + ", other=" + str(other._W0) + ")"
                diff_list.append(name + ".W0" + val_str)
            else:
                diff_list.append(name + ".W0")
        if (
            other._W1 is not None
            and self._W1 is not None
            and np.isnan(other._W1)
            and np.isnan(self._W1)
        ):
            pass
        elif other._W1 != self._W1:
            if is_add_value:
                val_str = " (self=" + str(self._W1) + ", other=" + str(other._W1) + ")"
                diff_list.append(name + ".W1" + val_str)
            else:
                diff_list.append(name + ".W1")
        if (
            other._W2 is not None
            and self._W2 is not None
            and np.isnan(other._W2)
            and np.isnan(self._W2)
        ):
            pass
        elif other._W2 != self._W2:
            if is_add_value:
                val_str = " (self=" + str(self._W2) + ", other=" + str(other._W2) + ")"
                diff_list.append(name + ".W2" + val_str)
            else:
                diff_list.append(name + ".W2")
        if (
            other._W3 is not None
            and self._W3 is not None
            and np.isnan(other._W3)
            and np.isnan(self._W3)
        ):
            pass
        elif other._W3 != self._W3:
            if is_add_value:
                val_str = " (self=" + str(self._W3) + ", other=" + str(other._W3) + ")"
                diff_list.append(name + ".W3" + val_str)
            else:
                diff_list.append(name + ".W3")
        if (
            other._H0 is not None
            and self._H0 is not None
            and np.isnan(other._H0)
            and np.isnan(self._H0)
        ):
            pass
        elif other._H0 != self._H0:
            if is_add_value:
                val_str = " (self=" + str(self._H0) + ", other=" + str(other._H0) + ")"
                diff_list.append(name + ".H0" + val_str)
            else:
                diff_list.append(name + ".H0")
        if (
            other._H1 is not None
            and self._H1 is not None
            and np.isnan(other._H1)
            and np.isnan(self._H1)
        ):
            pass
        elif other._H1 != self._H1:
            if is_add_value:
                val_str = " (self=" + str(self._H1) + ", other=" + str(other._H1) + ")"
                diff_list.append(name + ".H1" + val_str)
            else:
                diff_list.append(name + ".H1")
        if (
            other._H2 is not None
            and self._H2 is not None
            and np.isnan(other._H2)
            and np.isnan(self._H2)
        ):
            pass
        elif other._H2 != self._H2:
            if is_add_value:
                val_str = " (self=" + str(self._H2) + ", other=" + str(other._H2) + ")"
                diff_list.append(name + ".H2" + val_str)
            else:
                diff_list.append(name + ".H2")
        if (other.magnet_0 is None and self.magnet_0 is not None) or (
            other.magnet_0 is not None and self.magnet_0 is None
        ):
            diff_list.append(name + ".magnet_0 None mismatch")
        elif self.magnet_0 is not None:
            diff_list.extend(
                self.magnet_0.compare(
                    other.magnet_0,
                    name=name + ".magnet_0",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_1 is None and self.magnet_1 is not None) or (
            other.magnet_1 is not None and self.magnet_1 is None
        ):
            diff_list.append(name + ".magnet_1 None mismatch")
        elif self.magnet_1 is not None:
            diff_list.extend(
                self.magnet_1.compare(
                    other.magnet_1,
                    name=name + ".magnet_1",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_2 is None and self.magnet_2 is not None) or (
            other.magnet_2 is not None and self.magnet_2 is None
        ):
            diff_list.append(name + ".magnet_2 None mismatch")
        elif self.magnet_2 is not None:
            diff_list.extend(
                self.magnet_2.compare(
                    other.magnet_2,
                    name=name + ".magnet_2",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        if (other.magnet_3 is None and self.magnet_3 is not None) or (
            other.magnet_3 is not None and self.magnet_3 is None
        ):
            diff_list.append(name + ".magnet_3 None mismatch")
        elif self.magnet_3 is not None:
            diff_list.extend(
                self.magnet_3.compare(
                    other.magnet_3,
                    name=name + ".magnet_3",
                    ignore_list=ignore_list,
                    is_add_value=is_add_value,
                )
            )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from HoleMag
        S += super(HoleM61, self).__sizeof__()
        S += getsizeof(self.W0)
        S += getsizeof(self.W1)
        S += getsizeof(self.W2)
        S += getsizeof(self.W3)
        S += getsizeof(self.H0)
        S += getsizeof(self.H1)
        S += getsizeof(self.H2)
        S += getsizeof(self.magnet_0)
        S += getsizeof(self.magnet_1)
        S += getsizeof(self.magnet_2)
        S += getsizeof(self.magnet_3)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from HoleMag
        HoleM61_dict = super(HoleM61, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        HoleM61_dict["W0"] = self.W0
        HoleM61_dict["W1"] = self.W1
        HoleM61_dict["W2"] = self.W2
        HoleM61_dict["W3"] = self.W3
        HoleM61_dict["H0"] = self.H0
        HoleM61_dict["H1"] = self.H1
        HoleM61_dict["H2"] = self.H2
        if self.magnet_0 is None:
            HoleM61_dict["magnet_0"] = None
        else:
            HoleM61_dict["magnet_0"] = self.magnet_0.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_1 is None:
            HoleM61_dict["magnet_1"] = None
        else:
            HoleM61_dict["magnet_1"] = self.magnet_1.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_2 is None:
            HoleM61_dict["magnet_2"] = None
        else:
            HoleM61_dict["magnet_2"] = self.magnet_2.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        if self.magnet_3 is None:
            HoleM61_dict["magnet_3"] = None
        else:
            HoleM61_dict["magnet_3"] = self.magnet_3.as_dict(
                type_handle_ndarray=type_handle_ndarray,
                keep_function=keep_function,
                **kwargs
            )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        HoleM61_dict["__class__"] = "HoleM61"
        return HoleM61_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        W0_val = self.W0
        W1_val = self.W1
        W2_val = self.W2
        W3_val = self.W3
        H0_val = self.H0
        H1_val = self.H1
        H2_val = self.H2
        if self.magnet_0 is None:
            magnet_0_val = None
        else:
            magnet_0_val = self.magnet_0.copy()
        if self.magnet_1 is None:
            magnet_1_val = None
        else:
            magnet_1_val = self.magnet_1.copy()
        if self.magnet_2 is None:
            magnet_2_val = None
        else:
            magnet_2_val = self.magnet_2.copy()
        if self.magnet_3 is None:
            magnet_3_val = None
        else:
            magnet_3_val = self.magnet_3.copy()
        Zh_val = self.Zh
        if self.mat_void is None:
            mat_void_val = None
        else:
            mat_void_val = self.mat_void.copy()
        if self.magnetization_dict_offset is None:
            magnetization_dict_offset_val = None
        else:
            magnetization_dict_offset_val = self.magnetization_dict_offset.copy()
        Alpha0_val = self.Alpha0
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            W0=W0_val,
            W1=W1_val,
            W2=W2_val,
            W3=W3_val,
            H0=H0_val,
            H1=H1_val,
            H2=H2_val,
            magnet_0=magnet_0_val,
            magnet_1=magnet_1_val,
            magnet_2=magnet_2_val,
            magnet_3=magnet_3_val,
            Zh=Zh_val,
            mat_void=mat_void_val,
            magnetization_dict_offset=magnetization_dict_offset_val,
            Alpha0=Alpha0_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.W0 = None
        self.W1 = None
        self.W2 = None
        self.W3 = None
        self.H0 = None
        self.H1 = None
        self.H2 = None
        if self.magnet_0 is not None:
            self.magnet_0._set_None()
        if self.magnet_1 is not None:
            self.magnet_1._set_None()
        if self.magnet_2 is not None:
            self.magnet_2._set_None()
        if self.magnet_3 is not None:
            self.magnet_3._set_None()
        # Set to None the properties inherited from HoleMag
        super(HoleM61, self)._set_None()

    def _get_W0(self):
        """getter of W0"""
        return self._W0

    def _set_W0(self, value):
        """setter of W0"""
        check_var("W0", value, "float", Vmin=0)
        self._W0 = value

    W0 = property(
        fget=_get_W0,
        fset=_set_W0,
        doc="""Distance beetween two Hole

        :Type: float
        :min: 0
        """,
    )

    def _get_W1(self):
        """getter of W1"""
        return self._W1

    def _set_W1(self, value):
        """setter of W1"""
        check_var("W1", value, "float", Vmin=0)
        self._W1 = value

    W1 = property(
        fget=_get_W1,
        fset=_set_W1,
        doc="""Magnet width

        :Type: float
        :min: 0
        """,
    )

    def _get_W2(self):
        """getter of W2"""
        return self._W2

    def _set_W2(self, value):
        """setter of W2"""
        check_var("W2", value, "float", Vmin=0)
        self._W2 = value

    W2 = property(
        fget=_get_W2,
        fset=_set_W2,
        doc="""Magnet width

        :Type: float
        :min: 0
        """,
    )

    def _get_W3(self):
        """getter of W3"""
        return self._W3

    def _set_W3(self, value):
        """setter of W3"""
        check_var("W3", value, "float", Vmin=0)
        self._W3 = value

    W3 = property(
        fget=_get_W3,
        fset=_set_W3,
        doc="""Tooth width

        :Type: float
        :min: 0
        """,
    )

    def _get_H0(self):
        """getter of H0"""
        return self._H0

    def _set_H0(self, value):
        """setter of H0"""
        check_var("H0", value, "float", Vmin=0)
        self._H0 = value

    H0 = property(
        fget=_get_H0,
        fset=_set_H0,
        doc="""Distance from the lamination bore

        :Type: float
        :min: 0
        """,
    )

    def _get_H1(self):
        """getter of H1"""
        return self._H1

    def _set_H1(self, value):
        """setter of H1"""
        check_var("H1", value, "float", Vmin=0)
        self._H1 = value

    H1 = property(
        fget=_get_H1,
        fset=_set_H1,
        doc="""Magnet height

        :Type: float
        :min: 0
        """,
    )

    def _get_H2(self):
        """getter of H2"""
        return self._H2

    def _set_H2(self, value):
        """setter of H2"""
        check_var("H2", value, "float", Vmin=0)
        self._H2 = value

    H2 = property(
        fget=_get_H2,
        fset=_set_H2,
        doc="""Distance beetween the lamination bore and top of the slot

        :Type: float
        :min: 0
        """,
    )

    def _get_magnet_0(self):
        """getter of magnet_0"""
        return self._magnet_0

    def _set_magnet_0(self, value):
        """setter of magnet_0"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_0"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_0")
            value = Magnet()
        check_var("magnet_0", value, "Magnet")
        self._magnet_0 = value

        if self._magnet_0 is not None:
            self._magnet_0.parent = self

    magnet_0 = property(
        fget=_get_magnet_0,
        fset=_set_magnet_0,
        doc="""First Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_1(self):
        """getter of magnet_1"""
        return self._magnet_1

    def _set_magnet_1(self, value):
        """setter of magnet_1"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_1"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_1")
            value = Magnet()
        check_var("magnet_1", value, "Magnet")
        self._magnet_1 = value

        if self._magnet_1 is not None:
            self._magnet_1.parent = self

    magnet_1 = property(
        fget=_get_magnet_1,
        fset=_set_magnet_1,
        doc="""Second Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_2(self):
        """getter of magnet_2"""
        return self._magnet_2

    def _set_magnet_2(self, value):
        """setter of magnet_2"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_2"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_2")
            value = Magnet()
        check_var("magnet_2", value, "Magnet")
        self._magnet_2 = value

        if self._magnet_2 is not None:
            self._magnet_2.parent = self

    magnet_2 = property(
        fget=_get_magnet_2,
        fset=_set_magnet_2,
        doc="""Third Magnet

        :Type: Magnet
        """,
    )

    def _get_magnet_3(self):
        """getter of magnet_3"""
        return self._magnet_3

    def _set_magnet_3(self, value):
        """setter of magnet_3"""
        if isinstance(value, str):  # Load from file
            try:
                value = load_init_dict(value)[1]
            except Exception as e:
                self.get_logger().error(
                    "Error while loading " + value + ", setting None instead"
                )
                value = None
        if isinstance(value, dict) and "__class__" in value:
            class_obj = import_class(
                "pyleecan.Classes", value.get("__class__"), "magnet_3"
            )
            value = class_obj(init_dict=value)
        elif type(value) is int and value == -1:  # Default constructor
            Magnet = import_class("pyleecan.Classes", "Magnet", "magnet_3")
            value = Magnet()
        check_var("magnet_3", value, "Magnet")
        self._magnet_3 = value

        if self._magnet_3 is not None:
            self._magnet_3.parent = self

    magnet_3 = property(
        fget=_get_magnet_3,
        fset=_set_magnet_3,
        doc="""Fourth Magnet

        :Type: Magnet
        """,
    )

    class MachineCheckError(Exception):
        """ """

        pass

    class LaminationCheckError(MachineCheckError):
        """ """

        pass

    class SlotCheckError(LaminationCheckError):
        """ """

        pass

    class S61_WCheckError(SlotCheckError):
        """ """

        pass

    class S61_NoneError(SlotCheckError):
        """Raised when a propery of HoleM58 is None"""

        pass


MachineCheckError = HoleM61.MachineCheckError

LaminationCheckError = HoleM61.LaminationCheckError

SlotCheckError = HoleM61.SlotCheckError

S61_WCheckError = HoleM61.S61_WCheckError

S61_NoneError = HoleM61.S61_NoneError
