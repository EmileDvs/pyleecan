# Experimental dataclass generated from Generator/ClassesRef/Slot/SlotUD.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ..Functions.labels import SOP_LAB, WIND_LAB
from .arc_1 import Arc1
from .line import Line
from .segment import Segment
from .slot import Slot
from .surf_line import SurfLine


@dataclass(eq=False)
class SlotUD(Slot):
    """ "User defined" Slot from a line list.

    Attributes
    ----------
    line_list : [Line] or None
        list of line to draw the edges of the slot
        Default: None
    wind_begin_index : int or None
        Index of the first line to include in the winding
        Default: None
    wind_end_index : int or None
        Index of the last line to include in the winding
        Default: None
    type_line_wind : int
        0 to close winding with Segment, 1 for Arc1
        Default: 0; Minimum: 0; Maximum: 1
    name : str or None
        Name of the slot (for save)
        Default: None
    """

    line_list: list[Line] | None = None
    """list of line to draw the edges of the slot"""
    wind_begin_index: int | None = None
    """Index of the first line to include in the winding"""
    wind_end_index: int | None = None
    """Index of the last line to include in the winding"""
    type_line_wind: int = 0
    """0 to close winding with Segment, 1 for Arc1"""
    name: str | None = None
    """Name of the slot (for save)"""

    # Inlined from Methods.Slot.SlotUD.build_geometry
    def build_geometry(self):
        """Compute the curve (Line) needed to plot the object.
        The ending point of a curve is the starting point of the next curve
        in the list

        Parameters
        ----------
        self : SlotUD
            A SlotUD object

        Returns
        -------
        curve_list: list
            A list of Segments

        """

        return [line.copy() for line in self.line_list]

    # Inlined from Methods.Slot.SlotUD.check
    def check(self):
        """Check that the SlotUD is correctly defined"""

        if self.line_list is None:
            self.line_list = []

        if len(self.line_list) == 0:
            raise SlotCheckError("SlotUD must have at least one line")

        for ii in range(len(self.line_list) - 1):
            if (
                abs(self.line_list[ii].get_end() - self.line_list[ii + 1].get_begin())
                > 1e-6
            ):
                raise SlotCheckError(
                    "SlotUD line "
                    + str(ii)
                    + " and line "
                    + str(ii + 1)
                    + " doesn't match"
                )

        begin_id = self.wind_begin_index
        end_id = self.wind_end_index
        if begin_id is not None and end_id is not None:
            if begin_id > len(self.line_list):
                raise SlotCheckError(
                    "SlotUD wind_begin_index is greater than line_list length"
                )
            if end_id > len(self.line_list):
                raise SlotCheckError(
                    "SlotUD wind_end_index is greater than line_list length"
                )
            if begin_id > end_id:
                raise SlotCheckError(
                    "SlotUD wind_begin_index is greater than wind_end_index"
                )

    # Inlined from Methods.Slot.SlotUD.get_surface_active
    def get_surface_active(self, alpha=0, delta=0):
        """Return the full winding surface

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_wind: Surface
            Surface corresponding to the Winding Area
        """
        # get curve_list
        type_line_wind = self.type_line_wind
        if self.wind_begin_index is None and self.wind_end_index is None:
            # Winding not define, use complete surface
            line_list = self.build_geometry()
            type_line_wind = 1  # Enforce Arc1
        else:
            line_list = self.build_geometry()[
                self.wind_begin_index : self.wind_end_index
            ]

        # Add closing line
        if type_line_wind == 0:
            line_list.append(
                Segment(begin=line_list[-1].get_end(), end=line_list[0].get_begin())
            )
        else:
            line_list.append(
                Arc1(
                    begin=line_list[-1].get_end(),
                    end=line_list[0].get_begin(),
                    radius=-abs(line_list[-1].get_end()),
                    is_trigo_direction=False,
                )
            )

        label = self.parent.get_label() + "_" + WIND_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=line_list, label=label)
        surface.comp_point_ref(is_set=True)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return surface

    # Inlined from Methods.Slot.SlotUD.get_surface_opening
    def get_surface_opening(self, alpha=0, delta=0):
        """Return the list of surfaces defining the opening area of the Slot

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        alpha : float
            float number for rotation (Default value = 0) [rad]
        delta : complex
            complex number for translation (Default value = 0)

        Returns
        -------
        surf_list : list
            list of surfaces objects
        """

        # get curve_list
        line_list = self.build_geometry()
        curve_list_start = line_list[: self.wind_begin_index]
        curve_list_end = line_list[self.wind_end_index :]
        # Active Line
        Zb = curve_list_start[-1].get_end()
        Ze = curve_list_end[0].get_begin()
        if self.type_line_wind == 0:
            act_line = Segment(begin=Zb, end=Ze)
        else:
            act_line = Arc1(
                begin=Zb,
                end=Ze,
                radius=abs(Zb),
                is_trigo_direction=True,
            )
        bot_line = Arc1(
            curve_list_end[-1].get_end(),
            curve_list_start[0].get_begin(),
            -self.get_Rbo(),
            is_trigo_direction=False,
        )

        curve_list = curve_list_start + [act_line] + curve_list_end + [bot_line]
        label = self.parent.get_label() + "_" + SOP_LAB + "_R0-T0-S0"
        surface = SurfLine(line_list=curve_list, label=label)
        surface.comp_point_ref(is_set=True)

        # Apply transformation
        surface.rotate(alpha)
        surface.translate(delta)

        return [surface]

    # Inlined from Methods.Slot.SlotUD.set_from_point_list
    def set_from_point_list(self, point_list, is_sym=False):
        """Set the line_list from a point list (connected by Segments)

        Parameters
        ----------
        self : SlotUD
            A SlotUD object
        point_list : [complex]
            List of complex coordinates
        is_sym : bool
            True to duplicate the point by symmetries
        """

        # Apply symmetry if needed
        Z_list = point_list.copy()
        if is_sym:
            for point in point_list[::-1]:
                Z_list.append(point.conjugate())

        # Creation of curve
        line_list = []
        for ii in range(len(Z_list) - 1):
            line_list.append(Segment(Z_list[ii], Z_list[ii + 1]))

        self.line_list = line_list

    class MachineCheckError(Exception):
        """ """

    class LaminationCheckError(MachineCheckError):
        """ """

    class SlotCheckError(LaminationCheckError):
        """ """


MachineCheckError = SlotUD.MachineCheckError
LaminationCheckError = SlotUD.LaminationCheckError
SlotCheckError = SlotUD.SlotCheckError
