# Experimental dataclass generated from Generator/ClassesRef/Machine/Lamination.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from math import gcd

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

from . import NotImplementedYetError
from ..definitions import config_dict
from ..Functions.Geometry.merge_notch_list import merge_notch_list
from ..Functions.Geometry.transform_hole_surf import transform_hole_surf
from ..Functions.init_fig import init_fig
from ..Functions.labels import (
    BORE_LAB,
    BOUNDARY_PROP_LAB,
    LAM_LAB,
    NOTCH_LAB,
    RADIUS_PROP_LAB,
    ROTOR_LAB,
    STATOR_LAB,
    YOKE_LAB,
    YS_LAB,
    YSL_LAB,
    YSNL_LAB,
    YSNR_LAB,
    YSR_LAB,
)
from ..Functions.Load.import_class import import_class
from ..Functions.Plot.get_color_legend_from_surface import get_color_legend_from_surface
from ..Functions.Winding.gen_phase_list import gen_name
from ._pyleecan_class import PyleecanClass
from .arc_1 import Arc1
from .arc_3 import Arc3
from .bore import Bore
from .hole import Hole
from .machine import Machine
from .material import Material
from .notch import Notch
from .notch_even_dist import NotchEvenDist
from .out_geo_lam import OutGeoLam
from .segment import Segment
from .skew import Skew
from .surf_line import SurfLine
from .surf_ring import SurfRing


@dataclass(eq=False)
class Lamination(PyleecanClass):
    """abstract class for lamination

    Attributes
    ----------
    L1 : float
        Lamination stack active length without radial ventilation airducts but including insulation layers between lamination sheets
        Unit: m; Default: 0.35; Minimum: 0
    mat_type : Material or None
        Lamination's material
        Default: None
    Nrvd : int
        number of radial air ventilation ducts in lamination
        Default: 0; Minimum: 0
    Wrvd : float
        axial width of ventilation ducts in lamination
        Unit: m; Default: 0; Minimum: 0
    Kf1 : float
        lamination stacking / packing factor
        Default: 0.95; Minimum: 0; Maximum: 1
    is_internal : bool
        True for internal lamination topology, False for external lamination
        Default: True
    Rint : float
        To fill
        Unit: m; Default: 0; Minimum: 0
    Rext : float
        To fill
        Unit: m; Default: 1; Minimum: 0
    is_stator : bool
        To fill
        Default: True
    axial_vent : [Hole] or None
        Axial ventilation ducts
        Default: None
    notch : [Notch] or None
        Lamination bore notches
        Default: None
    skew : Skew or None
        Skew object
        Default: None
    bore : Bore or None
        Bore Shape
        Default: None
    yoke : Bore or None
        Yoke Shape
        Default: None
    """

    PATCH_COLOR_ALPHA = config_dict["PLOT"]["COLOR_DICT"]["PATCH_COLOR_ALPHA"]
    ROTOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["ROTOR_COLOR"]
    STATOR_COLOR = config_dict["PLOT"]["COLOR_DICT"]["STATOR_COLOR"]
    L1: float = 0.35
    """Lamination stack active length without radial ventilation airducts but including insulation layers between lamination sheets"""
    mat_type: Material | None = None
    """Lamination's material"""
    Nrvd: int = 0
    """number of radial air ventilation ducts in lamination"""
    Wrvd: float = 0
    """axial width of ventilation ducts in lamination"""
    Kf1: float = 0.95
    """lamination stacking / packing factor"""
    is_internal: bool = True
    """True for internal lamination topology, False for external lamination"""
    Rint: float = 0
    """To fill"""
    Rext: float = 1
    """To fill"""
    is_stator: bool = True
    """To fill"""
    axial_vent: list[Hole] | None = None
    """Axial ventilation ducts"""
    notch: list[Notch] | None = None
    """Lamination bore notches"""
    skew: Skew | None = None
    """Skew object"""
    bore: Bore | None = None
    """Bore Shape"""
    yoke: Bore | None = None
    """Yoke Shape"""

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(parent, (Machine,)):
            raise TypeError(
                "Lamination parent must be an instance of Machine, or None; "
                + f"got {type(parent).__name__}"
            )

    # Inlined from Methods.Machine.Lamination.build_geometry
    def build_geometry(self, sym=1, alpha=0, delta=0, is_circular_radius=False):
        """Build the geometry of the Lamination

        Parameters
        ----------
        self : Lamination
            Lamination Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_circular_radius : bool
            True to add surfaces to "close" the Lamination radii

        Returns
        surf_list : list
            list of surfaces needed to draw the lamination

        """
        # Label setup
        label = self.get_label()
        label_lam = label + "_" + LAM_LAB
        label_bore = label + "_" + LAM_LAB + BORE_LAB
        label_yoke = label + "_" + LAM_LAB + YOKE_LAB
        if self.is_internal:
            label_ext = label_bore
            label_int = label_yoke
        else:
            label_ext = label_yoke
            label_int = label_bore

        # Get Radius lines
        yoke_prop = {RADIUS_PROP_LAB: YOKE_LAB, BOUNDARY_PROP_LAB: label_yoke}
        if self.is_internal:
            if self.Rint > 0:
                int_line = self.build_radius_lines(
                    is_bore=False, sym=sym, is_reversed=True, prop_dict=yoke_prop
                )
            else:
                int_line = []
            ext_line = self.build_radius_lines(
                is_bore=True, sym=sym, prop_dict={RADIUS_PROP_LAB: BORE_LAB}
            )
        else:
            ext_line = self.build_radius_lines(
                is_bore=False, sym=sym, is_reversed=True, prop_dict=yoke_prop
            )
            int_line = self.build_radius_lines(
                is_bore=True, sym=sym, prop_dict={RADIUS_PROP_LAB: BORE_LAB}
            )

        # Add the ventilation ducts if there is any
        surf_list = []
        vent_surf_list = []
        if self.axial_vent not in [None, []]:
            for vent in self.axial_vent:
                kwargs = dict(alpha=0, delta=0)
                vent_list = vent.build_geometry(**kwargs)
                surf = transform_hole_surf(
                    hole_surf_list=vent_list,
                    Zh=vent.Zh,
                    sym=sym,
                    is_split=True,
                    **kwargs,
                )
                vent_surf_list.extend(surf)
        surf_list.extend(vent_surf_list)

        # Add keys if any
        if self.notch is not None:
            for ii, notch in enumerate(self.notch):
                if notch.has_key():
                    surf_list.extend(notch.build_geometry_key(index=ii, sym=sym))

        # Add the closing surfaces if requested
        if is_circular_radius:
            surf_list.extend(self.get_surfaces_closing(sym=sym))

        # Create the Lamination surfaces
        point_ref = self.comp_point_ref(sym=sym)
        if sym == 1:  # Complete lamination
            ext_surf = SurfLine(
                label=label_ext, line_list=ext_line, point_ref=point_ref
            )
            int_surf = SurfLine(label=label_int, line_list=int_line, point_ref=0)
            if self.Rint > 0 and len(ext_line) > 0:
                surf_list.insert(
                    0,
                    SurfRing(
                        out_surf=ext_surf,
                        in_surf=int_surf,
                        label=label_lam,
                        point_ref=point_ref,
                    ),  # First in list for plot
                )
            elif self.Rint == 0 and len(ext_line) > 0:
                surf_list.insert(0, ext_surf)  # First in list for plot
            elif self.Rint == self.Rext:  # No lamination
                pass  # No surface to draw
            elif len(ext_line) == 0:  # (SlotM17)
                pass  # No surface to draw / No lamination
        # Part of the lamination by symmetry
        elif sym != 1 and len(ext_line) > 0 and self.Rint != self.Rext:
            # Get limit point of the yoke side
            if self.is_internal:
                ZTR = ext_line[0].get_begin()  # Top Right
                ZTL = ext_line[-1].get_end()  # Top Left
                if len(int_line) > 0:
                    ZBR = int_line[-1].get_end()  # Bot Right
                    ZBL = int_line[0].get_begin()  # Bot Left
                else:  # Machine without shaft for instance
                    ZBR = None
                    ZBL = None
            else:
                ZTR = ext_line[-1].get_end()  # Top Right
                ZTL = ext_line[0].get_begin()  # Top Left
                if len(int_line) > 0:
                    ZBL = int_line[-1].get_end()  # Bot Left
                    ZBR = int_line[0].get_begin()  # Bot Right
                else:  # Machine without shaft for instance
                    ZBR = None
                    ZBL = None
            right_list, left_list = self.build_yoke_side_line(
                sym=sym,
                vent_surf_list=vent_surf_list,
                ZBR=ZBR,
                ZTR=ZTR,
                ZBL=ZBL,
                ZTL=ZTL,
            )
            # Create lines
            curve_list = []
            if self.is_internal:
                curve_list.extend(right_list)
            else:
                curve_list.extend(left_list)
            curve_list.extend(ext_line)
            if self.is_internal:
                curve_list.extend(left_list)
            else:
                curve_list.extend(right_list)
            if self.Rint > 0:
                curve_list.extend(int_line)

            surf_yoke = SurfLine(
                line_list=curve_list, label=label_lam, point_ref=point_ref
            )
            surf_list.insert(0, surf_yoke)  # First in list for plot

        # apply the transformation
        for surf in surf_list:
            surf.rotate(alpha)
            surf.translate(delta)

        return surf_list

    # Inlined from Methods.Machine.Lamination.build_radius_desc
    def build_radius_desc(self, is_bore, sym=1):
        """This method returns an ordered description of the slot/notch
        that defines the bore/yoke radius of the lamination
        (Bore/Yoke shape not taken into account by this method, cf build_radius_lines)

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True generate description of bore, else yoke
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        radius_desc : list
            trigo ordered list of dictionary with key:
                "begin_angle" : float [rad]
                "end_angle" : float [rad]
                "obj" : Slot or None
                "lines : lines corresponding to the radius part
                "label" : Radius/Notch/Slot
        """

        # For readibility
        is_notch = self.has_notch(is_bore=is_bore)
        is_slot = self.has_slot(is_bore=is_bore)
        if is_bore:
            R = self.get_Rbo()
        else:
            R = self.get_Ryoke()

        radius_desc = []
        if not is_notch and not is_slot:
            radius_lines = []
            if sym == 1:  # Two arcs to avoid angle > 180 deg
                arc1 = Arc3(begin=R, end=-R, is_trigo_direction=True)
                arc2 = Arc3(begin=-R, end=R, is_trigo_direction=True)
                end_angle = 0
                radius_lines.append(arc1)
                radius_lines.append(arc2)
            else:
                end_angle = 2 * np.pi / sym
                rot = np.exp(1j * end_angle)
                arc = Arc1(begin=R, end=R * rot, radius=R, is_trigo_direction=True)
                radius_lines.append(arc)
            radius_desc.append(
                {
                    "begin_angle": 0,
                    "end_angle": end_angle,
                    "obj": None,
                    "lines": radius_lines,
                    "label": "Radius",
                }
            )
            return radius_desc

        # Notch/Slot case
        if is_notch:
            # Get all the notch on the selected radius
            notch_list = [
                notch for notch in self.notch if notch.notch_shape.is_bore == is_bore
            ]
            # Get description of first notch
            notch_desc_list = notch_list[0].get_notch_desc_list(sym=sym)
            # If more than one notch, we need to merge and order the description
            for ii in range(len(notch_list) - 1):
                notch_desc_list = merge_notch_list(
                    notch_desc_list, notch_list[ii + 1].get_notch_desc_list(sym=sym)
                )
        else:
            notch_desc_list = []
        # Get slot description
        if is_slot:
            slot_desc_list = self.get_slot_desc_list(sym=sym, is_bore=is_bore)
        else:
            slot_desc_list = []
        all_desc_list = merge_notch_list(notch_desc_list, slot_desc_list)

        # Add the radius between each notch/slot
        for ii in range(len(all_desc_list) - 1):
            radius_desc.append(all_desc_list[ii])
            begin = all_desc_list[ii]["end_angle"]
            end = all_desc_list[ii + 1]["begin_angle"]
            if begin != end:  # begin = end for "full slot / no tooth"
                radius_desc.append(
                    {
                        "begin_angle": begin,
                        "end_angle": end,
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * begin),
                                end=R * np.exp(1j * end),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
        # Add last notch/slot
        radius_desc.append(all_desc_list[-1])
        # Add first and last radius line if required
        if all_desc_list[0]["begin_angle"] > 0:
            if sym == 1 and all_desc_list[-1]["end_angle"] > 2 * np.pi:
                # Alpha >0, last notch cross Ox
                begin = all_desc_list[-1]["end_angle"] - 2 * np.pi
                radius_desc.insert(
                    0,
                    {
                        "begin_angle": begin,
                        "end_angle": all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * begin),
                                end=R * np.exp(1j * all_desc_list[0]["begin_angle"]),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    },
                )
            else:  # Add radius from Ox to first notch
                radius_desc.insert(
                    0,
                    {
                        "begin_angle": 0,
                        "end_angle": all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * 0),
                                end=R * np.exp(1j * all_desc_list[0]["begin_angle"]),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    },
                )
        if all_desc_list[-1]["end_angle"] < 2 * np.pi / sym:
            if all_desc_list[0]["begin_angle"] < 0 and sym == 1:
                # Full lamination with slot/notch on Ox
                radius_desc.append(
                    {
                        "begin_angle": all_desc_list[-1]["end_angle"],
                        "end_angle": 2 * np.pi + all_desc_list[0]["begin_angle"],
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * all_desc_list[-1]["end_angle"]),
                                end=R
                                * np.exp(
                                    1j * (2 * np.pi + all_desc_list[0]["begin_angle"])
                                ),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
            else:
                radius_desc.append(
                    {
                        "begin_angle": all_desc_list[-1]["end_angle"],
                        "end_angle": 2 * np.pi / sym,
                        "obj": None,
                        "lines": [
                            Arc1(
                                begin=R * np.exp(1j * all_desc_list[-1]["end_angle"]),
                                end=R * np.exp(1j * 2 * np.pi / sym),
                                radius=R,
                                is_trigo_direction=True,
                            )
                        ],
                        "label": "Radius",
                    }
                )
        return radius_desc

    # Inlined from Methods.Machine.Lamination.build_radius_lines
    def build_radius_lines(self, is_bore, sym=1, is_reversed=False, prop_dict=None):
        """Create the lines need to draw the selected radius of the Lamination

        Parameters
        ----------
        self : Lamination
            a Lamination object
        is_bore : bool
            True generate lines of bore, else yoke
        is_reversed : bool
            True to return the lines in clockwise oder (reverse begin and end), False trigo
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        prop_dict : dict
            Property dictionary to apply on the radius lines (not on slot/notch)

        Returns
        -------
        radius_lines : list
            list of bore/yoke lines
        """
        # For readibitlity
        is_notch = self.has_notch(is_bore=is_bore)
        is_slot = self.has_slot(is_bore=is_bore)
        if is_bore:
            R = self.get_Rbo()
            is_shape = self.bore is not None
            shape_obj = self.bore
        else:
            R = self.get_Ryoke()
            is_shape = self.yoke is not None
            shape_obj = self.yoke

        if not is_shape:  # Arc or Slot/Notch only
            radius_desc_list = self.build_radius_desc(is_bore=is_bore, sym=sym)
            # Cut lines for sym
            if sym != 1:
                # Cut first desc (if needed)
                if radius_desc_list[0]["begin_angle"] < 0:
                    lines = []
                    for line in radius_desc_list[0]["lines"]:
                        top_split_list, _ = line.split_line(0, 1)
                        lines.extend(top_split_list)
                    radius_desc_list[0]["begin_angle"] = 0
                    radius_desc_list[0]["lines"] = lines
                # Cut last desc (if needed)
                if radius_desc_list[-1]["end_angle"] > 2 * np.pi / sym:
                    lines = []
                    for line in radius_desc_list[-1]["lines"]:
                        _, bot_split_list = line.split_line(
                            0, np.exp(1j * 2 * np.pi / sym)
                        )
                        lines.extend(bot_split_list)
                    radius_desc_list[-1]["end_angle"] = 2 * np.pi / sym
                    radius_desc_list[-1]["lines"] = lines
            # Extract the line list
            radius_lines = []
            for desc_dict in radius_desc_list:
                # Apply prop_dict on Radius only
                if prop_dict is not None and desc_dict["label"] == "Radius":
                    for line in desc_dict["lines"]:
                        if line.prop_dict is None:
                            line.prop_dict = {}
                        line.prop_dict.update(prop_dict)
                radius_lines.extend(desc_dict["lines"])

        elif is_shape and not is_notch and not is_slot:
            # Bore/Yoke shape only
            radius_lines = shape_obj.get_bore_line()
            if sym > 1:  # Ox cut
                lines = []
                for line in radius_lines:
                    top_split_list, _ = line.split_line(0, 1)
                    lines.extend(top_split_list)
                radius_lines = lines
            if sym > 2:
                lines = []
                for line in radius_lines:
                    _, bot_split_list = line.split_line(0, np.exp(1j * 2 * np.pi / sym))
                    lines.extend(bot_split_list)
                radius_lines = lines
            # Only radius lines => prop_dict on all lines
            if prop_dict is not None:
                for line in radius_lines:
                    if line.prop_dict is None:
                        line.prop_dict = {}
                    line.prop_dict.update(prop_dict)
        else:  # Bore/Yoke shape to merge with slot/notch
            radius_desc_list = self.build_radius_desc(is_bore=is_bore, sym=sym)
            radius_lines = shape_obj.merge_slot(
                radius_desc_list, prop_dict=prop_dict, sym=sym
            )

        # Reverse the lines
        if is_reversed:
            radius_lines = radius_lines[::-1]
            for line in radius_lines:
                line.reverse()

        return radius_lines

    # Inlined from Methods.Machine.Lamination.build_yoke_side_line
    def build_yoke_side_line(
        self,
        sym,
        vent_surf_list,
        ZBR=None,
        ZTR=None,
        ZBL=None,
        ZTL=None,
        *,
        DELTA=1e-06,
    ):
        """Define the Yoke Side lines of a Lamination by taking into account sym and vent

        Parameters
        ----------
        self: Lamination
            a Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        vent_surf_list :
            List of the ventilation surfaces
        ZBR : Complex
            Yoke Side Limit point Bottom Right
        ZTR : Complex
            Yoke Side Limit point Top Right
        ZBL : Complex
            Yoke Side Limit point Bottom Left
        ZTL : Complex
            Yoke Side Limit point Top Left

        Returns
        -------
        right_list, left_list: ([Line], [Line])
            List of the lines to draw the left and right side of the yoke
        """

        # Find the ventilation lines that collide with the Yoke Side
        inter_line_list_R, inter_line_list_L = [], []
        for surf in vent_surf_list:
            for line in surf.get_lines():
                if (
                    line.prop_dict is not None
                    and BOUNDARY_PROP_LAB in line.prop_dict
                    and YS_LAB in line.prop_dict[BOUNDARY_PROP_LAB]
                ):
                    # Find if the line collide on right or left
                    if abs(np.angle(line.get_middle())) < DELTA:
                        inter_line_list_R.append(line)
                    else:
                        inter_line_list_L.append(line)

        # Yoke Limit point
        if ZBR is None:
            alpha = 2 * np.pi / sym
            ZBR = self.Rint
            ZTR = self.Rext
            ZBL = ZBR * np.exp(1j * alpha)
            ZTL = ZTR * np.exp(1j * alpha)

        lam_lab = self.get_label()
        if self.is_internal:
            right_list = self.merge_line_list(
                ZBR, ZTR, lam_lab + "_" + YSR_LAB, inter_line_list_R
            )
            left_list = self.merge_line_list(
                ZTL, ZBL, lam_lab + "_" + YSL_LAB, inter_line_list_L
            )
        else:
            left_list = self.merge_line_list(
                ZBL, ZTL, lam_lab + "_" + YSL_LAB, inter_line_list_L
            )
            right_list = self.merge_line_list(
                ZTR, ZBR, lam_lab + "_" + YSR_LAB, inter_line_list_R
            )

        return right_list, left_list

    @staticmethod
    def merge_line_list(Z1, Z2, label, inter_list):
        """Merge the ventilation lines and the yoke side line"""
        is_int_to_ext = abs(Z1) < abs(Z2)
        #  Always number the lines from int to out (to match both sides)
        if not is_int_to_ext:
            Z1, Z2 = Z2, Z1
        # Sort the inter_list by begin (assume that the vents doesn't collide)
        inter_list.sort(key=lambda x: abs(x.get_begin()), reverse=False)
        # Make sure that all the lines are int to ext
        for line in inter_list:
            if abs(line.get_end()) < abs(line.get_begin()):
                line.reverse()

        line_list = []
        Zb = Z1  # Current Begin
        ii = 0  # Line index
        for line in inter_list:
            line_list.append(
                Segment(
                    Zb,
                    line.get_begin(),
                    prop_dict={BOUNDARY_PROP_LAB: label + "-" + str(ii)},
                )
            )
            ii += 1
            line.prop_dict[BOUNDARY_PROP_LAB] = label + "-" + str(ii)
            ii += 1
            Zb = line.get_end()
        # Add last line (or Z1 to Z2 if no intersection)
        line_list.append(
            Segment(Zb, Z2, prop_dict={BOUNDARY_PROP_LAB: label + "-" + str(ii)})
        )
        # reverse the lines if needed
        if not is_int_to_ext:
            line_list = line_list[::-1]
            for line in line_list:
                line.reverse()

        return line_list

    # Inlined from Methods.Machine.Lamination.check
    def check(self):
        """Check that the Lamination object is correct

        Parameters
        ----------
        self :
            A Lamination object

        Returns
        -------
        None

        Raises
        _______
        LC_VentYokeIn
            The ventilation ducts cross the yoke internal radius
        LC_VentYokeOut
            The ventilation ducts cross the yoke external radius
        LC_RadiusError
            The internal radius is greater than the external one


        """

        if self.Rint > self.Rext:
            raise LC_RadiusError("The internal radius is greater than the external one")

        for vent in self.axial_vent:
            vent.check()

            # The ventilation duct must be on the yoke
            if vent.Zh > 0:
                if self.is_internal:
                    Rin = self.Rint
                    Rout = self.Rint + self.comp_height_yoke()
                else:
                    Rin = self.Rint + self.comp_height_yoke()
                    Rout = self.Rext

                (Rmin, Rmax) = vent.comp_radius()

                if Rmin < Rin:
                    raise LC_VentYokeIn(
                        "The ventilation ducts cross the yoke internal radius"
                    )
                if Rmax > Rout:
                    raise LC_VentYokeOut(
                        "The ventilation ducts cross the yoke external radius"
                    )

    # Inlined from Methods.Machine.Lamination.comp_angle_q_axis
    def comp_angle_q_axis(self):
        """Compute the angle between the X axis and the first q+ axis
        By convention a "Tooth" is centered on the X axis
        By convention the first magnet is +

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        d_angle : float
            angle between the X axis and the first d+ axis
        """

        q_angle = self.comp_angle_d_axis()
        p = self.get_pole_pair_number()
        return q_angle + np.pi / p / 2

    # Inlined from Methods.Machine.Lamination.comp_height_yoke
    def comp_height_yoke(self):
        """Compute the yoke height

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Hy: float
            yoke height [m]

        """
        return self.Rext - self.Rint

    # Inlined from Methods.Machine.Lamination.comp_length
    def comp_length(self):
        """Compute the total length of the Lamination (including radial
        ventilations duct)

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Lt: float
            Total Lenght of the Lamination [m]

        """
        if self.Nrvd is None or self.Wrvd is None:
            return self.L1
        else:
            return self.L1 + self.Nrvd * self.Wrvd

    # Inlined from Methods.Machine.Lamination.comp_masses
    def comp_masses(self):
        """Compute the masses of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        M_dict: dict
            Lamination mass dictionary (Mtot, Mlam, Mteeth, Myoke) [kg]

        """
        rho = self.mat_type.struct.rho
        V_dict = self.comp_volumes()

        M_dict = {}
        M_dict["Myoke"] = V_dict["Vyoke"] * self.Kf1 * rho
        M_dict["Mteeth"] = V_dict["Vteeth"] * self.Kf1 * rho
        M_dict["Mlam"] = V_dict["Vlam"] * self.Kf1 * rho
        M_dict["Mtot"] = M_dict["Mlam"]

        return M_dict

    # Inlined from Methods.Machine.Lamination.comp_output_geo
    def comp_output_geo(self):
        """Compute the main geometry output

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        output: OutGeoLam
            Main geometry output of the lamintion

        """

        output = OutGeoLam()
        output.name_phase = self.get_name_phase()
        output.BH_curve = self.mat_type.mag.get_BH()

        return output

    # Inlined from Methods.Machine.Lamination.comp_periodicity_duct_spatial
    def comp_periodicity_duct_spatial(self, per_a, is_antiper_a):
        """Compute the periodity of the axial cooling ducts

        Parameters
        ----------
        self : Lamination
            A Lamination object
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities

        Returns
        -------
        per_a : int
            Spatial periodicity of the lamination including ducts
        is_antiper_a : bool
            Spatial antiperidicity of the lamination including ducts
        """

        # No duct => no impact on sym
        if self.axial_vent in [None, []]:
            self.axial_vent = []
            return per_a, is_antiper_a

        # Compute duct periodicity
        per_d = self.axial_vent[0].Zh
        for duct in self.axial_vent[1:]:
            per_d = int(gcd(per_d, duct.Zh))

        # "Merge" lamination and duct periodicity
        if is_antiper_a:
            per = int(gcd(per_d, per_a * 2))
            if per == per_a * 2:  # No impact of vent
                pass
            elif per == per_a:  # Anti per removed
                is_antiper_a = False
            elif per_a % per == 0:
                per_a = per
                is_antiper_a = False
            elif per % 2 == 0:
                per_a = int(per / 2)
                is_antiper_a = True
            else:
                per_a = per
                is_antiper_a = False
        else:
            per_a = int(gcd(per_d, per_a))

        # if hasattr(self, "get_Zs") and hasattr(self, "get_pole_pair_number"):
        #     Zs = self.get_Zs()
        #     p = self.get_pole_pair_number()
        #     if per_a == 1:
        #         is_antiper_a = bool(Zs % 2 == 0)
        #     else:
        #         is_antiper_a = bool(Zs / p % 2 == 0)

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.Lamination.comp_periodicity_geo
    def comp_periodicity_geo(self):
        """Compute the geometric periodicity factor of the lamination

        Parameters
        ----------
        self : lamination
            A lamination object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if hasattr(self, "get_Zs"):
            Zs = self.get_Zs()

            nb_list = [Zs]
            # account for notches and bore
            if self.notch is not None:
                for notch in self.notch:
                    nb_list.append(notch.comp_periodicity_spatial()[0])

            if self.bore:
                nb_list.append(self.bore.comp_periodicity_spatial()[0])
            if self.yoke:
                nb_list.append(self.yoke.comp_periodicity_spatial()[0])

            # compute the gcd of the list
            if len(nb_list) == 1:
                per_a = nb_list[0]
            else:
                per_a = np.gcd(nb_list[0], nb_list[1])
                for ii in range(2, len(nb_list)):
                    per_a = np.gcd(per_a, nb_list[ii])

            nb_list.pop(0)
            is_antiper_a = False

            # Account for duct periodicity
            per_a, is_antiper_a = self.comp_periodicity_duct_spatial(
                per_a, is_antiper_a
            )
            per_a = int(per_a)

        else:
            per_a = None
            is_antiper_a = False

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.Lamination.comp_periodicity_spatial
    def comp_periodicity_spatial(self):
        """Compute the periodicity factor of the lamination

        Parameters
        ----------
        self : lamination
            A lamination object

        Returns
        -------
        per_a : int
            Number of spatial periodicities of the lamination
        is_antiper_a : bool
            True if an spatial anti-periodicity is possible after the periodicities
        """

        if hasattr(self, "get_Zs") and hasattr(self, "get_pole_pair_number"):
            Zs = self.get_Zs()
            p = self.get_pole_pair_number()

            nb_list = [p, Zs]
            # account for notches and bore
            if self.notch is not None:
                for notch in self.notch:
                    nb_list.append(notch.comp_periodicity_spatial()[0])

            if self.bore:
                nb_list.append(self.bore.comp_periodicity_spatial()[0])
            if self.yoke:
                nb_list.append(self.yoke.comp_periodicity_spatial()[0])

            # compute the gcd of the list
            per_a = np.gcd(nb_list[0], nb_list[1])
            for ii in range(2, len(nb_list)):
                per_a = np.gcd(per_a, nb_list[ii])

            nb_list.pop(0)
            is_antiper_a = all([nb / per_a % 2 == 0 for nb in nb_list])

            # Account for duct periodicity
            per_a, is_antiper_a = self.comp_periodicity_duct_spatial(
                per_a, is_antiper_a
            )
            per_a = int(per_a)

        else:
            per_a = None
            is_antiper_a = False

        return per_a, is_antiper_a

    # Inlined from Methods.Machine.Lamination.comp_point_ref
    def comp_point_ref(self, sym=1):
        """Compute coordinates of a point in the lamination
        to assign property in FEA software
        Account for slot, notches and ventilations (TODO)

        Parameters
        ----------
        self : Lamination
            Lamination Object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        point_ref : complex
            Reference point of the lamination

        """

        Rref = self.comp_radius_mid_yoke()

        # Find a radius that doesn't match any ventilation
        if self.axial_vent not in [None, []]:
            R1, R2 = Rref, Rref
            for vent in self.axial_vent:
                (Rmin, Rmax) = vent.comp_radius()
                R1 = min(R1, Rmin)
                R2 = max(R2, Rmax)
            if self.is_internal:
                Rref = (self.Rint + R1) / 2
            else:
                Rref = (self.Rext + R2) / 2

        # Find an angle without notches on the yoke
        if not self.has_notch(is_bore=False):
            angle = np.pi / sym
        else:
            yoke_desc_list = self.build_radius_desc(sym=sym, is_bore=False)
            ii = 0
            while (
                ii < len(yoke_desc_list)
                and yoke_desc_list[ii]["label"] != "Radius"
                and (
                    yoke_desc_list[ii]["begin_angle"] < yoke_desc_list[ii]["end_angle"]
                )
            ):
                ii += 1
            angle = (
                yoke_desc_list[ii]["begin_angle"] + yoke_desc_list[ii]["end_angle"]
            ) / 2

        return Rref * np.exp(1j * angle)

    # Inlined from Methods.Machine.Lamination.comp_radius_mec
    def comp_radius_mec(self):
        """Compute the mechanical radius of the Lamination [m]

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Rmec: float
            Mechanical radius [m]

        """

        if self.is_internal:
            return self.Rext
        else:
            return self.Rint

    # Inlined from Methods.Machine.Lamination.comp_radius_mid_yoke
    def comp_radius_mid_yoke(self):
        """Compute the Lamination middle of the yoke radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Ry: float
            middle of the yoke radius [m]

        """

        Hyoke = self.comp_height_yoke()
        if self.is_internal:
            return self.Rint + Hyoke / 2
        else:
            return self.Rext - Hyoke / 2

    # Inlined from Methods.Machine.Lamination.comp_surface_axial_vent
    def comp_surface_axial_vent(self):
        """Compute the Lamination axial vent

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Svent: float
            Surface of the Lamination's axial ventilation [m**2]

        """

        if len(self.axial_vent) > 0:
            return sum([vent.comp_surface() * vent.Zh for vent in self.axial_vent])
        else:
            return 0

    # Inlined from Methods.Machine.Lamination.comp_surfaces
    def comp_surfaces(self):
        """Compute the Lamination surface (Total, Vent).

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        S_dict: dict
            Lamination surface dictionary (Slam, Svent, Syoke, Steeth, Sslot) [m**2]

        """
        if self.is_internal:
            ext_shape = self.bore
            int_shape = self.yoke
        else:
            ext_shape = self.yoke
            int_shape = self.bore

        # Surface of the external disk
        if ext_shape is not None:
            S_ext = ext_shape.comp_surface()
        else:
            S_ext = (self.Rext**2) * np.pi
        # Surface of the internal disk
        if int_shape is not None:
            S_int = int_shape.comp_surface()
        else:
            S_int = (self.Rint**2) * np.pi

        # Surface of lamination without hole
        Slam = S_ext - S_int

        # Surface of the ventilation ducts on the yoke
        Svent = self.comp_surface_axial_vent()

        # Compute notches surfaces
        Snotch = 0
        if self.notch is not None and len(self.notch) > 0:
            for notch in self.notch:
                Snotch += notch.comp_surface()

        return {
            "Slam": Slam - Svent - Snotch,
            "Svent": Svent,
            "Syoke": Slam,
            "Steeth": 0,
            "Sslot": 0,
            "Snotch": Snotch,
        }

    # Inlined from Methods.Machine.Lamination.comp_volumes
    def comp_volumes(self):
        """Compute the volumes of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        V_dict: dict
            Volume of the Lamination (Vlam, Vvent, Vyoke, Vteeth) [m**3]

        """

        Lf = self.comp_length()  # Include radial ventilation ducts

        S_dict = self.comp_surfaces()
        Vvent = Lf * S_dict["Svent"]
        # L1 is without ventilation ducts (volume to compute masses)
        Vlam = self.L1 * S_dict["Slam"]
        Vyoke = self.L1 * S_dict["Syoke"]
        Vteeth = self.L1 * S_dict["Steeth"]
        return {"Vlam": Vlam, "Vvent": Vvent, "Vyoke": Vyoke, "Vteeth": Vteeth}

    # Inlined from Methods.Machine.Lamination.get_label
    def get_label(self, is_add_id=True):
        """Return the label of the lamination (Stator-0 for instance)

        Parameters
        ----------
        self : Lamination
            a Lamination object
        is_add_id : bool
            True to add the "-X" part

        Returns
        -------
        label : str
            Label of the lamination

        """

        if self.is_stator:
            label = STATOR_LAB
        else:
            label = ROTOR_LAB

        if is_add_id:
            if self.parent is not None:
                try:
                    lam_list = self.parent.get_lam_list(is_int_to_ext=True, key=label)
                    label += "-" + str(lam_list.index(self))
                except:
                    pass
            # else:
            #     raise ParentMissingError("Error: The slot is not inside a Lamination")

        return label

    # Inlined from Methods.Machine.Lamination.get_name_phase
    def get_name_phase(self):
        """Return the name of the winding phases

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        name_phase: list
            Empty list

        """
        if (
            not hasattr(self, "winding") or self.winding is None
            # or self.winding.conductor is None
        ):
            return []
        return gen_name(self.winding.qs)

    # Inlined from Methods.Machine.Lamination.get_notches_surf
    def get_notches_surf(self, sym):
        """Return the list of surfaces for notches

        Parameters
        ----------
        self : Lamination
            A Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Return
        ------
        surf_list : list
            list of surfaces needed for the notches
        """

        if self.notch is None:
            self.notch = []

        # Get all the notch on the bore radius
        notch_list = [notch for notch in self.notch if notch.notch_shape.is_bore]
        if len(notch_list) == 0:
            return []

        surf_list = []
        for ii, notch in enumerate(notch_list):
            # Method used for symetry (for now) so only NotchEvenDist
            assert isinstance(notch, NotchEvenDist)
            if notch.has_key():
                continue  # Key surface overlap closing surface
            # Get the original surface
            Nsurf = notch.notch_shape.get_surface()
            Nsurf.label = self.get_label() + "_" + NOTCH_LAB + "_R" + str(ii) + "-T0-S0"
            Nsurf.rotate(angle=notch.alpha)
            # Label definition
            BC_prop_right = self.get_label() + "_" + YSNR_LAB
            BC_prop_left = self.get_label() + "_" + YSNL_LAB
            # Generate all the surfaces (handle cut on sym axis)
            surf_list.extend(
                transform_hole_surf(
                    hole_surf_list=[Nsurf],
                    Zh=notch.notch_shape.Zs,
                    sym=sym,
                    alpha=0,
                    delta=0,
                    is_split=True,
                    BC_prop_right=BC_prop_right,
                    BC_prop_left=BC_prop_left,
                )
            )

        return surf_list

    # Inlined from Methods.Machine.Lamination.get_polar_eq
    def get_polar_eq(self):
        """Returns a polar equivalent of the lamination

        Parameters
        ----------
        self : Lamination
            Lamination object

        Returns
        -------
        polar_eq: Lamination
            The polar equivalent of the lamination
        """

        raise NotImplementedYetError(
            "get_polar_eq available only for LamSlotWind for now"
        )

    # Inlined from Methods.Machine.Lamination.get_Rbo
    def get_Rbo(self):
        """Return the bore lamination radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Rbo: float
            The lamination bore radius [m]

        """

        if self.is_internal:
            return self.Rext
        else:
            return self.Rint

    # Inlined from Methods.Machine.Lamination.get_Ryoke
    def get_Ryoke(self):
        """Return the yoke lamination radius

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        Ryoke: float
            The lamination yoke radius [m]

        """

        if self.is_internal:
            return self.Rint
        else:
            return self.Rext

    # Inlined from Methods.Machine.Lamination.get_surfaces_closing
    def get_surfaces_closing(self, sym=1):
        """Return the surfaces needed to close the radii of the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)

        Returns
        -------
        surf_list : list
            List of the closing surfaces
        """

        # No notch when bore shape
        if self.bore is None:
            return self.get_notches_surf(sym=sym)
        else:
            return []

    # Inlined from Methods.Machine.Lamination.has_key
    def has_key(self):
        """Check if a there is key in the Lamination

        Parameters
        ----------
        self : Lamination
            A Lamination object

        Returns
        -------
        has_key : bool
            True if the Lamination has at least one key
        """

        if self.notch is None:
            return False
        return any([notch.has_key() for notch in self.notch])

    # Inlined from Methods.Machine.Lamination.has_notch
    def has_notch(self, is_bore):
        """Check if notches are set on the requested radius

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True check notch on bore radius, else on yoke

        Returns
        -------
        has_notch : bool
            True if notches are set on the requested radius
        """

        if self.notch is None or len(self.notch) == 0:
            return False

        # notch_shape.is_bore = None => Default is True
        if is_bore:
            return any(
                [notch.notch_shape.is_bore in [True, None] for notch in self.notch]
            )
        else:
            return any([notch.notch_shape.is_bore == False for notch in self.notch])

    # Inlined from Methods.Machine.Lamination.has_slot
    def has_slot(self, is_bore=True):
        """Return if the lamination has slot on the requested radius
        (notches not taken into account, cf has_notch)

        Parameters
        ----------
        self : Lamination
            A Lamination object
        is_bore : bool
            True check if there are slots on the bore, else yoke

        Returns
        -------
        has_slot : bool
            True if the lamination has slot on the requested radius
        """

        return False

    # Inlined from Methods.Machine.Lamination.is_outwards
    def is_outwards(self):
        """Return if the slot is outwards (on an external lamination) or inwards
        (on an internal lamination)

        Parameters
        ----------
        self : Slot
            A Slot object

        Returns
        -------
        is_outwards: bool
            True if the Lamination is not internal and false if not
        """
        return not self.is_internal

    # Inlined from Methods.Machine.Lamination.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_lam_only=False,
        sym=1,
        alpha=0,
        delta=0,
        is_edge_only=False,
        edgecolor=None,
        is_add_arrow=False,
        is_show_fig=True,
        save_path=None,
        is_winding_connection=False,
    ):
        """Plot the Lamination in a matplotlib fig

        Parameters
        ----------
        self : Lamination
            A Lamination object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_lam_only: bool
            True to plot only the lamination (no effect for Lamination object)
        sym : int
            Symmetry factor (1= full machine, 2= half of the machine...)
        alpha : float
            Angle for rotation [rad]
        delta : complex
            Complex value for translation
        is_edge_only: bool
            To plot transparent Patches
        edgecolor:
            Color of the edges if is_edge_only=True
        is_show_fig : bool
            To call show at the end of the method
        save_path : str
            full path including folder, name and extension of the file to save if save_path is not None
        is_winding_connection : bool
            True to display winding connections (not used)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        surf_list = self.build_geometry(sym=sym, alpha=alpha, delta=delta)
        patches = []

        # Color Selection for Surfaces
        for surf in surf_list:
            color, legend = get_color_legend_from_surface(surf, is_lam_only)

            if color is not None:
                patches.extend(
                    surf.get_patches(
                        color=color,
                        is_edge_only=is_edge_only,
                        edgecolor=edgecolor,
                    )
                )
            if not is_edge_only and legend is not None and legend not in label_leg:
                label_leg.append(legend)
                patch_leg.append(Patch(color=color))

        # Display the result
        ax.set_xlabel("(m)")
        ax.set_ylabel("(m)")
        for patch in patches:
            ax.add_patch(patch)

        # Axis Setup
        ax.axis("equal")

        # The Lamination is centered in the figure
        Lim = self.Rext * 1.5
        ax.set_xlim(-Lim, Lim)
        ax.set_ylim(-Lim, Lim)

        title = None

        # Adding legend
        if not is_edge_only:
            if self.is_stator:
                title = "Stator without slot"
            else:
                title = "Rotor without slot"
            ax.set_title(title)
            ax.legend(patch_leg, label_leg)
        if is_show_fig:
            fig.show()
        if save_path is not None:
            fig.savefig(save_path)
            plt.close(fig=fig)
        return fig, ax

    # Inlined from Methods.Machine.Lamination.plot_preview_notch
    def plot_preview_notch(self, index, fig=None, ax=None):
        """Preview the position/shape of a notch on the lamination

        Parameters
        ----------
        self : Lamination
            Lamination object
        index : int
            Index of the notch to preview
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        if self.notch is None:
            raise Exception("No notch set")
        if index > len(self.notch) - 1:
            raise Exception(
                "Requested notch index "
                + str(index)
                + ", "
                + str(len(self.notch))
                + " notches were set"
            )
        # Plot the original lamination without notches
        lam = self.copy()
        lam.notch = []

        fig, ax = lam.plot(
            fig=fig,
            ax=ax,
            is_lam_only=True,
        )

        # Create equivalent LamSlot with notch as slot
        LamSlot = import_class("pyleecan.Classes", "LamSlot")
        lam_notch = LamSlot(
            is_stator=lam.is_stator,
            is_internal=lam.is_internal,
            Rint=lam.Rint,
            Rext=lam.Rext,
            slot=self.notch[index].notch_shape,
        )
        fig, ax = lam_notch.plot(
            fig=fig,
            ax=ax,
            is_edge_only=True,
            edgecolor="r--",
            alpha=-np.pi / self.notch[index].notch_shape.Zs + self.notch[index].alpha,
        )
        # Setup legend
        if self.is_stator:
            name = "Stator"
            color = self.STATOR_COLOR
        else:
            name = "Rotor"
            color = self.ROTOR_COLOR
        patch_leg = [
            Patch(facecolor=color, edgecolor="k"),
            Patch(facecolor=self.PATCH_COLOR_ALPHA, edgecolor="r", linestyle="--"),
        ]
        label_leg = ["Current " + name, "Notches"]
        ax.set_axis_off()
        ax.legend(patch_leg, label_leg)

        return fig, ax

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class LC_VentYokeOut(LaminationCheckError):
        """ """

    class LC_VentYokeIn(LaminationCheckError):
        """ """

    class LC_RadiusError(LaminationCheckError):
        """ """


MachineCheckError = Lamination.MachineCheckError
LaminationCheckError = Lamination.LaminationCheckError
LC_VentYokeOut = Lamination.LC_VentYokeOut
LC_VentYokeIn = Lamination.LC_VentYokeIn
LC_RadiusError = Lamination.LC_RadiusError
