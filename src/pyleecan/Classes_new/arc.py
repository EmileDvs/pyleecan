# Experimental dataclass generated from Generator/ClassesRef/Geometry/Arc.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import ClassVar

import numpy as np

from ..Functions_new.Geometry.inter_circle_circle import inter_circle_circle
from ..Functions_new.Geometry.inter_line_circle import inter_line_circle
from ..Functions_new.init_fig import init_fig
from ..Functions_new.Plot import TEXT_BOX
from ._import import import_class
from .line import Line
from .segment import Segment


@dataclass(eq=False)
class Arc(Line):
    """Abstract class for arc

    Attributes
    ----------
    """

    ARC_NPOINT_D: ClassVar = 99

    # Inlined from Methods.Geometry.Arc.comp_distance
    def comp_distance(self, Z):
        """Compute the distance of a point to the Arc

        Parameters
        ----------
        self : Arc
            An Arc object
        Z : complex
            Complex coordinate of the point

        Returns
        -------
        D : float
            distance of a point to the Segment
        """

        Zc = self.get_center()
        Z2 = Z - Zc

        A1 = self.get_angle()
        A2 = np.angle(Z2 * np.exp(-1j * np.angle(self.get_begin() - Zc)))

        if np.sign(A1) == np.sign(A2) and abs(A2) < abs(A1):
            # The point is on the correct side of the arc
            D1 = abs(np.sqrt(Z2.real**2 + Z2.imag**2) - self.comp_radius())
            return D1
        else:
            D2 = abs(Z - self.get_begin())
            D3 = abs(Z - self.get_end())
            D4 = abs(Z - self.get_middle())
            return min([D2, D3, D4])

    # Inlined from Methods.Geometry.Arc.comp_maxseg
    def comp_maxseg(self, elementsize, maxseg_amp, *, MAXSEG_default=5):
        """
        Computes the number of segments per arc degrees in
        function of the elementsize of the region

        Parameters
        ----------
        self : Arc
            An Arc object
        elementsize : float
            max element size parameter
        maxseg_amp : float
            amplifying factor

        Returns
        -------
        maxseg : float
            number of segments per arc degrees
        """

        if elementsize == 0:
            # taking default maximum segment value
            maxseg = MAXSEG_default

        else:
            angle = self.get_angle(is_deg=True)
            begin = self.get_begin()
            end = self.get_end()

            if np.abs(angle) == 180:
                l_arc = np.pi * np.abs(begin - end) / 2
            elif np.abs(angle) == 90:
                l_arc = np.pi / 2 * np.abs(begin - end) / np.sqrt(2)
            else:
                l_arc = np.abs(
                    (begin - end) / (2 * np.sin(angle / 2 * np.pi / 180))
                ) * np.abs(angle * np.pi / 180)

            n_seg = l_arc / elementsize

            maxseg = np.abs(min(MAXSEG_default, np.abs(angle / n_seg * maxseg_amp)))

        return maxseg

    # Inlined from Methods.Geometry.Arc.draw_FEMM
    def draw_FEMM(
        self,
        femm,
        nodeprop=None,
        maxseg=None,
        element_size=None,
        propname=None,
        hide=False,
        group=None,
        is_draw=True,
    ):
        """Draw the Arc object in FEMM and assign the property

        Parameters
        ----------
        femm : FEMMHandler
            client to send command to a FEMM instance
        nodeprop :
            Nodal property
             (Default value = None)
        maxseg :
            Meshed with elements that span at most maxsegdeg degrees per element
             (Default value = None)
        propname :
            Boundary property ’propname’
             (Default value = None)
        hide :
            0 = not hidden in post-processor, 1 == hidden in post processor
             (Default value = False)
        group :
            the group the Arc1 object belongs
             (Default value = None)
        is_draw : bool
            1 to draw the list of surfaces given

        Returns
        -------
        None
        """

        # split if arc angle > 180
        angle = self.get_angle(is_deg=True)

        # Compute the coordinate of the nodes
        begin = self.get_begin()
        mid = self.get_middle()
        end = self.get_end()
        X1, Y1 = begin.real, begin.imag
        X2, Y2 = mid.real, mid.imag
        X3, Y3 = end.real, end.imag

        if is_draw:
            # Adding nodes
            femm.mi_addnode(X1, Y1)
            femm.mi_addnode(X3, Y3)

        femm.mi_selectnode(X1, Y1)
        femm.mi_setnodeprop(nodeprop, group)
        femm.mi_clearselected()

        femm.mi_selectnode(X3, Y3)
        femm.mi_setnodeprop(nodeprop, group)
        femm.mi_clearselected()

        if np.abs(angle) > 180:
            if is_draw:
                femm.mi_addnode(X2, Y2)

            femm.mi_selectnode(X2, Y2)
            femm.mi_setnodeprop(nodeprop, group)
            femm.mi_clearselected()

        # invert the nodes
        if angle < 0:
            angle = -angle
            X1, Y1, X3, Y3 = X3, Y3, X1, Y1

        if is_draw:
            if angle > 180:
                femm.mi_addarc(X1, Y1, X2, Y2, angle / 2, 2)
                femm.mi_addarc(X2, Y2, X3, Y3, angle / 2, 2)
            else:
                femm.mi_addarc(X1, Y1, X3, Y3, angle, 2)

        # Set Arc properties
        if angle > 180:
            cent = self.get_center()
            mid1 = cent + (mid - cent) * np.exp(1j * angle / 4)
            mid2 = cent + (mid - cent) * np.exp(-1j * angle / 4)
            femm.mi_selectarcsegment(mid1.real, mid1.imag)
            femm.mi_selectarcsegment(mid2.real, mid1.imag)
        else:
            femm.mi_selectarcsegment(X2, Y2)

        maxseg = self.comp_maxseg(element_size, maxseg)
        femm.mi_setarcsegmentprop(maxseg, propname, hide, group)
        femm.mi_clearselected()

    # Inlined from Methods.Geometry.Arc.intersect_line
    def intersect_line(self, Z1, Z2):
        """Return a list (0, 1 or 2 complex) of coordinates of the
        intersection of the arc with a line defined by two complex

        Parameters
        ----------
        self : Arc
            An Arc object

        Returns
        -------
        Z_list: list
            Complex coordinates of the intersection (if any)
        """

        Zc = self.get_center()
        R = self.comp_radius()

        # Get intersetion between line and the full circle
        Zlist = inter_line_circle(Z1=Z1, Z2=Z2, R=R, Zc=Zc)

        # Keep only the points actually on the arc
        Zlist = [Z for Z in Zlist if self.is_on_line(Z)]

        # Order the intersection points (begin=>intersect1=>intersection2=>end)
        if len(Zlist) == 2:
            begin = self.get_begin()
            if np.abs(Zlist[0] - begin) < 1e-6:
                # First point is begin
                return Zlist
            if np.abs(Zlist[1] - begin) < 1e-6:
                # Second point is begin
                return Zlist[::-1]

            # Go to the coordinate system Zc as center, begin on X > 0 axis
            Z1 = (Zlist[0] - Zc) * np.exp(-1j * np.angle(begin - Zc))
            Z2 = (Zlist[1] - Zc) * np.exp(-1j * np.angle(begin - Zc))

            alpha = self.get_angle()
            A1 = np.angle(Z1) % (2 * np.pi)
            A2 = np.angle(Z2) % (2 * np.pi)
            # Check if Zlist needs to be reversed
            if alpha > 0 and A1 > A2:
                return Zlist[::-1]
            if alpha < 0 and A2 > A1:
                return Zlist[::-1]
        return Zlist

    # Inlined from Methods.Geometry.Arc.intersect_obj
    def intersect_obj(self, other, is_on_line=True):
        """Find the intersection points between this line
        and another line object

        Parameters
        ----------
        self : Arc
            An Arc object
        other : Line
            The other line object to intersect
        is_on_line : bool
            True to return only points that are on both Line objects

        Returns
        -------
        Z_list: list
            Complex coordinates of the intersection (if any)
        """

        if other.is_arc():
            inter_list = inter_circle_circle(
                Zc1=self.get_center(),
                Zc2=other.get_center(),
                R1=abs(self.comp_radius()),
                R2=abs(other.comp_radius()),
            )
        else:
            inter_list = self.intersect_line(Z1=other.get_begin(), Z2=other.get_end())

        if not is_on_line:
            return inter_list

        # Plot for debug
        # fig, ax = self.plot(color="r")
        # other.plot(fig=fig, ax=ax, color="b")
        # for ii, Z in enumerate(inter_list):
        #     ax.plot(Z.real, Z.imag, "rx", zorder=0)
        #     ax.text(Z.real, Z.imag, str(ii))
        # ax.plot(0, 0, "kx", zorder=0)
        # ax.text(0, 0, "O")
        # plt.show()

        # Keep only points on both lines
        Z_list = []
        for Z in inter_list:
            if self.is_on_line(Z) and other.is_on_line(Z):
                Z_list.append(Z)

        return Z_list

    # Inlined from Methods.Geometry.Arc.is_arc
    def is_arc(self):
        """Check if the line is an Arc

        Parameters
        ----------
        self : Arc
            An Arc object

        Returns
        -------
        is_arc : bool
            True for Arc
        """

        return True

    # Inlined from Methods.Geometry.Arc.is_on_line
    def is_on_line(self, Z):
        """Check is a point defined by its complex coordinate is on the arc

        Parameters
        ----------
        self : Arc
            An Arc object
        Z : complex
            Complex coordinate of the point

        Returns
        -------
        is_on_line : bool
            True if the point is on the arc
        """

        Zc = self.get_center()
        R = self.comp_radius()

        # Check if on the circle
        if abs(np.abs(Z - Zc) - R) > 1e-6:
            return False

        # Check if point is begin or end
        begin = self.get_begin()
        end = self.get_end()
        if np.abs(Z - begin) < 1e-6:
            return True
        if np.abs(Z - end) < 1e-6:
            return True

        # Go to the coordinate system Zc as center, begin on X > 0 axis
        Ze = (end - Zc) * np.exp(-1j * np.angle(begin - Zc))
        Z = (Z - Zc) * np.exp(-1j * np.angle(begin - Zc))

        alpha = self.get_angle()
        Ae = np.angle(Ze) % (2 * np.pi)
        Az = np.angle(Z) % (2 * np.pi)
        if alpha > 0:  # Trigo direction
            if Ae > Az:
                return True
            return False
        # Clockwise direction
        if Az > Ae:
            return True
        return False

    # Inlined from Methods.Geometry.Arc.plot
    def plot(
        self,
        fig=None,
        ax=None,
        linestyle="solid",
        linewidth=1,
        color="black",
        label=None,
        offset_label=0,
        fontsize=12,
    ):
        """Plot the Arc

        Parameters
        ----------
        self : Arc
            An Arc object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        linestyle : str
            Line of the line (solid, dotted...)
        linewidth : int
            Line Width
        color : str
            Color of the line
        label : str
            To add a label at the middle of the line
        offset_label : complex
            Complex value to shift the label from the middle
        fontsize : int
            Size of the font for the label (if any)

        Returns
        -------
        fig : Matplotlib.figure.Figure
            Figure containing the plot
        ax : Matplotlib.axes.Axes object
            Axis containing the plot
        """

        # Init fig
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        # Plot the line
        points = self.discretize(nb_point=10000)
        ax.plot(
            points.real,
            points.imag,
            linestyle=linestyle,
            linewidth=linewidth,
            color=color,
        )

        # Add the label (if needed)
        if label is not None:
            Zmid = self.get_middle()
            ax.text(
                Zmid.real + offset_label.real,
                Zmid.imag + offset_label.imag,
                label,
                fontsize=fontsize,
                bbox=TEXT_BOX,
            )

        return fig, ax

    # Inlined from Methods.Geometry.Arc.split_line
    def split_line(self, Z1, Z2, is_join=False, prop_dict_join=None, *, DELTA=1e-07):
        """Cut the Arc according to a line defined by two complex
        "Above" is in the coordinate system with Z1 in 0 and Z2 on the X>0 axis

        Parameters
        ----------
        self : Segment
            An Segment object
        Z1 : complex
            First point of the cutting Line
        Z2 : complex
            Second point of the cutting Line
        is_join : bool
            True to join the split_list with Segment if there is more that one remaining parts
        prop_dict_join : dict
            Property dict to set on the join line

        Returns
        -------
        top_split_list, bot_split_list : ([Line], [Line])
            Both part of the arc
        """

        # Dynamic import of Arc1 to prevent import loop from code generator
        Arc1 = import_class("Arc1")

        # Get the intersection point
        Z_int = self.intersect_line(Z1, Z2)
        # Begin and end point in the line coordonate system
        Zb = (self.get_begin() - Z1) * np.exp(-1j * np.angle(Z2 - Z1))
        Ze = (self.get_end() - Z1) * np.exp(-1j * np.angle(Z2 - Z1))
        # Center of the arc (for later check)
        Zc = self.get_center()

        if len(Z_int) == 0:
            # No intersection copy the line
            line = self.copy()
            # Begin and end on top
            if Zb.imag >= 0 and Ze.imag >= 0:
                return [line], []
            # Begin and end on bot
            elif Zb.imag <= 0 and Ze.imag <= 0:
                return [], [line]
            else:
                raise Exception("Split Arc error (case 0 int)")
        if len(Z_int) == 1:
            # One intersection => Three possible lines
            # Begin => Intersection
            line1 = Arc1(
                begin=self.get_begin(),
                end=Z_int[0],
                radius=self.comp_radius(),
                is_trigo_direction=bool(self.get_angle() > 0),
            )
            # Fix radius if needed
            if (
                np.abs(line1.begin - line1.end) > 1e-6  # Avoid error for center
                and np.abs(line1.get_center() - Zc) > 1e-6
            ):
                line1.radius = -1 * line1.radius
            # Intersection => End
            line2 = Arc1(
                begin=Z_int[0],
                end=self.get_end(),
                radius=self.comp_radius(),
                is_trigo_direction=bool(self.get_angle() > 0),
            )
            # Fix radius if needed
            if (
                np.abs(line2.begin - line2.end) > 1e-6
                and np.abs(line2.get_center() - Zc) > 1e-6  # Avoid error for center
            ):
                line2.radius = -1 * line2.radius

            # Copy of the complete line (begin or end on cutting line, or cutting line is tangent)
            line3 = self.copy()

            # If the line is tangent, begin and end are on the same side of the line
            if (Zb.imag > DELTA and Ze.imag > DELTA) or (
                Zb.imag < -DELTA and Ze.imag < -DELTA
            ):
                # Begin (and end) on top
                if Zb.imag > DELTA:
                    return [line3], []
                # Begin (and end) on bot
                elif Zb.imag < -DELTA:
                    return [], [line3]
                else:
                    raise Exception("Split Arc error (case 1 int-Tangent)")
            # Return the correct line according to the points position
            elif Zb.imag > DELTA and abs(Ze.imag) > DELTA:  # Begin on top; End!=Int
                return [line1], [line2]
            elif Zb.imag > DELTA:  # Begin on top; End==Int
                return [line3], []
            elif Zb.imag < -DELTA and abs(Ze.imag) > DELTA:  # Begin on bot; End!=Int
                return [line2], [line1]
            elif Zb.imag < -DELTA:  # Begin on bot; End==Int
                return [], [line3]
            # Zb.imag == 0 => begin on cutting line
            elif Ze.imag > DELTA:  # Begin==Int, End on Top
                return [line3], []
            elif Ze.imag < -DELTA:  # Begin==Int, End on Bot
                return [], [line3]
            else:
                raise Exception("Split Arc error (case 1 int-Non Tangent)")
        elif len(Z_int) == 2:
            # Two intersection => Three possible lines
            # Begin => Intersection1 (intersection are ordered along the arc)
            line1 = Arc1(
                begin=self.get_begin(),
                end=Z_int[0],
                radius=self.comp_radius(),
                is_trigo_direction=bool(self.get_angle() > 0),
            )
            # Fix radius if needed
            if (
                np.abs(line1.begin - line1.end) > 1e-6  # Avoid error for center
                and np.abs(line1.get_center() - Zc) > 1e-6
            ):
                line1.radius = -1 * line1.radius
            # Intersection 1 => Intersection 2
            line2 = Arc1(
                begin=Z_int[0],
                end=Z_int[1],
                radius=self.comp_radius(),
                is_trigo_direction=bool(self.get_angle() > 0),
            )
            # Fix radius if needed
            if (
                np.abs(line2.begin - line2.end) > 1e-6  # Avoid error for center
                and np.abs(line2.get_center() - Zc) > 1e-6
            ):
                line2.radius = -1 * line2.radius
            # Intersection 2 => End
            line3 = Arc1(
                begin=Z_int[1],
                end=self.get_end(),
                radius=self.comp_radius(),
                is_trigo_direction=bool(self.get_angle() > 0),
            )
            # Fix radius if needed
            if (
                np.abs(line3.begin - line3.end) > 1e-6  # Avoid error for center
                and np.abs(line3.get_center() - Zc) > 1e-6
            ):
                line3.radius = -1 * line3.radius
            # Line Intersection 1 => Intersection 2 for join
            seg_join = Segment(begin=Z_int[0], end=Z_int[1], prop_dict=prop_dict_join)
            # If both intersection are Begin and end
            line4 = self.copy()
            if is_join:
                line_list = [line1, seg_join, line3]
            else:
                line_list = [line1, line3]
            if np.abs(Z_int[0] - self.get_begin()) < DELTA:  # Begin==Int1
                line_list.pop(0)
            if np.abs(Z_int[1] - self.get_end()) < DELTA:
                line_list.pop(-1)

            # If the intersetion points are begin and end
            if (
                np.abs(Z_int[0] - self.get_begin()) < DELTA
                and np.abs(Z_int[1] - self.get_end()) < DELTA
            ):
                Zm = (self.get_middle() - Z1) * np.exp(-1j * np.angle(Z2 - Z1))
                # begin and end are on the line => Zm.imag != 0
                if Zm.imag > 0:
                    return [line4], []
                elif Zm.imag < 0:
                    return [], [line4]
                else:
                    raise Exception("Split Arc error (case 2 int-Both)")
            elif Zb.imag > DELTA:  # Begin on top
                return line_list, [line2]
            elif Zb.imag < -DELTA:  # Begin on bot
                return [line2], line_list
            elif Ze.imag > DELTA:  # Begin== Int1, End on Top
                return line_list, [line2]
            elif Ze.imag < -DELTA:  # Begin== Int1, End on Bot
                return [line2], line_list
            else:
                Exception("Split Arc error (case 2 int)")
