# Experimental dataclass generated from Generator/ClassesRef/Geometry/Segment.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from ..Functions.Geometry.inter_line_circle import inter_line_circle
from ..Functions.Geometry.inter_line_line import inter_line_line
from ..Functions.init_fig import init_fig
from ..Functions.Plot import TEXT_BOX
from .line import Line
from .machine import LINE_NPOINT_D


@dataclass(eq=False)
class Segment(Line):
    """A segment between two points

    Attributes
    ----------
    begin : complex
        begin point of the line
        Default: 0
    end : complex
        end point of the line
        Default: 0
    """

    begin: complex = 0
    """begin point of the line"""
    end: complex = 0
    """end point of the line"""

    # Inlined from Methods.Geometry.Segment.check
    def check(self):
        """assert that the line is correct (begin != end)

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        None

        Raises
        ------
        PointSegmentError
            The beginning point and the ending point of an Segment
            can't be the same

        """
        if self.begin == self.end or (abs(self.begin) == 0 and abs(self.end) == 0):
            raise PointSegmentError(
                "The beginning point and the ending point of "
                "a Segment can't be the same"
            )

    # Inlined from Methods.Geometry.Segment.comp_distance
    def comp_distance(self, Z):
        """Compute the distance of a point to the Segment

        Parameters
        ----------
        self : Segment
            A Segment object
        Z : complex
            Complex coordinate of the point

        Returns
        -------
        D : float
            distance of a point to the Segment
        """

        Z1 = np.array([self.begin.real, self.begin.imag, 0])
        Z2 = np.array([self.end.real, self.end.imag, 0])
        Z3 = np.array([Z.real, Z.imag, 0])
        return self.distance_numpy(Z1, Z2, Z3)

    @staticmethod
    def distance_numpy(A, B, P):
        # from: https://gist.github.com/nim65s/5e9902cd67f094ce65b0
        """segment line AB, point P, where each one is an array([x, y])"""
        if all(A == P) or all(B == P):
            return 0
        if (
            np.arccos(
                np.dot((P - A) / np.linalg.norm(P - A), (B - A) / np.linalg.norm(B - A))
            )
            > np.pi / 2
        ):
            return np.linalg.norm(P - A)
        if (
            np.arccos(
                np.dot((P - B) / np.linalg.norm(P - B), (A - B) / np.linalg.norm(A - B))
            )
            > np.pi / 2
        ):
            return np.linalg.norm(P - B)
        return np.linalg.norm(np.cross(A - B, A - P)) / np.linalg.norm(B - A)

    # Inlined from Methods.Geometry.Segment.comp_length
    def comp_length(self):
        """Compute the length of the line

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        length: float
            lenght of the line [m]

        Raises
        ------
        PointSegmentError
            Call Segment.check()

        """

        self.check()

        z1 = self.begin
        z2 = self.end

        return float(abs(z2 - z1))

    # Inlined from Methods.Geometry.Segment.discretize
    def discretize(self, nb_point=LINE_NPOINT_D):
        """Return the discretize version of the Segment.
        Begin and end are always returned

        Parameters
        ----------
        self : Segment
            A Segment object
        nb_point : int
            Number of points to add to discretize the line (Default value = LINE_NPOINT_D)

        Returns
        -------
        list_point: list
            List of complex coordinate of the points

        Raises
        ------
        NbPointSegmentDError
            nb_point must be an integer >=
        """

        self.check()
        if not isinstance(nb_point, int):
            raise NbPointSegmentDError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointSegmentDError("nb_point must be >=0")

        # t start by 0 (begin) and end by 1 (end)
        # len(t) = nb_point +2 : begin + end + nb_point between
        t = np.linspace(0, 1, nb_point + 2)

        # We use the complex representation of the point
        z1 = self.begin
        z2 = self.end

        # Generate the points with the parametric representation of the line
        return z1 - (z1 - z2) * t

    # Inlined from Methods.Geometry.Segment.draw_FEMM
    def draw_FEMM(
        self,
        femm,
        nodeprop=None,
        propname=None,
        element_size=None,
        automesh=None,
        hide=False,
        group=None,
        is_draw=True,
    ):
        """<   Draw the segment in FEMM and assign the property

        Parameters
        ----------
        femm : FEMMHandler
            client to send command to a FEMM instance
        nodeprop :
            Nodal property
            (Default value = None)
        propname :
            Boundary property ’propname’
            (Default value = None)
        element_size :
            Local element size along segment no greater than element_size
            (Default value = None)
        automesh :
            0 = mesher defers to the element constraint defined by
            element_size, 1 = mesher automatically chooses mesh size along
            the selected segments
            (Default value = None)
        hide :
            0 = not hidden in post-processor, 1 == hidden in post processorc
            (Default value = False)
        group :
            group the segment belongs
            (Default value = None)
        is_draw : bool
            1 to draw the list of surfaces given

        Returns
        -------
        None
        """

        # Determine locations of the nodes
        X1, Y1 = self.begin.real, self.begin.imag
        X2, Y2 = self.end.real, self.end.imag

        if is_draw:
            # Adding nodes
            femm.mi_addnode(X1, Y1)
            femm.mi_addnode(X2, Y2)

        # Adding property on the node
        femm.mi_selectnode(X1, Y1)
        femm.mi_setnodeprop(nodeprop, group)
        femm.mi_clearselected()
        femm.mi_selectnode(X2, Y2)
        femm.mi_setnodeprop(nodeprop, group)
        femm.mi_clearselected()

        if is_draw:
            # Adding the segment
            femm.mi_addsegment(X1, Y1, X2, Y2)

        # Set property of the segment
        femm.mi_selectsegment((X1 + X2) / 2, (Y1 + Y2) / 2)
        femm.mi_setsegmentprop(propname, element_size, automesh, hide, group)
        femm.mi_clearselected()

    # Inlined from Methods.Geometry.Segment.get_begin
    def get_begin(self):
        """Return the begin point of the segment

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        begin: complex
            Begin point of the Segment
        """

        return self.begin

    # Inlined from Methods.Geometry.Segment.get_end
    def get_end(self):
        """Return the end point of the segment

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        end: complex
            End point of the Segment
        """

        return self.end

    # Inlined from Methods.Geometry.Segment.get_middle
    def get_middle(self):
        """Return the point at the middle of the Segment

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Segment
        """

        Z1 = self.begin
        Z2 = self.end

        Zmid = (Z1 + Z2) / 2.0
        # Return (0,0) if the point is too close from 0
        if abs(Zmid) < 1e-6:
            Zmid = 0
        return Zmid

    # Inlined from Methods.Geometry.Segment.intersect_line
    def intersect_line(self, Z1, Z2):
        """Return a list (0, 1 or 2 complex) of coordinates of the
        intersection of the segment with a line defined by two complex

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        Z_list: list
            Complex coordinates of the intersection (if any,
            return [begin, end] if the segment is part of the line)
        """

        Z3 = self.begin
        Z4 = self.end

        Z_list = inter_line_line(Z1, Z2, Z3, Z4)
        if len(Z_list) == 0:
            # No intersection
            return []
        elif len(Z_list) == 1:
            # One intersect. Is it between begin and end or not ?
            Z_int = Z_list[0]
            Seg_len = self.comp_length()
            if np.abs(Z_int - Z3) <= Seg_len and np.abs(Z_int - Z4) <= Seg_len:
                return [Z_int]
            elif np.abs(Z_int - Z3) <= 1e-6 or np.abs(Z_int - Z4) <= 1e-6:
                # Zint is begin or end
                return [Z_int]
            else:
                return []
        elif len(Z_list) == 2:
            # The segment is on the line
            return [Z3, Z4]

    # Inlined from Methods.Geometry.Segment.intersect_obj
    def intersect_obj(self, other, is_on_line=True):
        """Find the intersection points between this line
        and another line object

        Parameters
        ----------
        self : Segment
            A Segment object
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
            inter_list = inter_line_circle(
                Z1=self.begin,
                Z2=self.end,
                R=abs(other.comp_radius()),
                Zc=other.get_center(),
            )
        else:
            inter_list = self.intersect_line(Z1=other.get_begin(), Z2=other.get_end())

        if not is_on_line:
            return inter_list

        # Keep only points on both lines
        Z_list = []
        for Z in inter_list:
            if self.is_on_line(Z) and other.is_on_line(Z):
                Z_list.append(Z)

        return Z_list

    # Inlined from Methods.Geometry.Segment.is_arc
    def is_arc(self):
        """Check if the line is an Arc

        Parameters
        ----------
        self : Segment
            A Segment object

        Returns
        -------
        is_arc : bool
            False for Segment
        """

        return False

    # Inlined from Methods.Geometry.Segment.is_on_line
    def is_on_line(self, Z):
        """Check is a point defined by its complex coordinate is on the segment

        Parameters
        ----------
        self : Segment
            A Segment object
        Z : complex
            Complex coordinate of the point

        Returns
        -------
        is_on_line : bool
            True if the point is on the segment
        """

        Z1 = self.begin
        Z2 = self.end
        Z3 = Z
        # Check if the points are aligned
        Z12 = Z1 - Z2
        Z13 = Z1 - Z3
        if abs(Z12.real * Z13.imag - Z12.imag * Z13.real) < 1e-10:
            K13 = Z12.real * Z13.real + Z12.imag * Z13.imag
            K12 = Z12.real * Z12.real + Z12.imag * Z12.imag
            if K13 >= 0 and K13 <= K12:
                return True
        return False

    # Inlined from Methods.Geometry.Segment.plot
    def plot(
        self,
        fig=None,
        ax=None,
        is_arrow=False,
        linestyle="solid",
        linewidth=1,
        color="black",
        label=None,
        offset_label=0,
        fontsize=12,
    ):
        """Plot the segment

        Parameters
        ----------
        self : Segment
            A Segment object
        fig : Matplotlib.figure.Figure
            existing figure to use if None create a new one
        ax : Matplotlib.axes.Axes object
            Axis on which to plot the data
        is_arrow : bool
            True to draw a double headed arrow instead of a line
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
        begin = self.get_begin()
        end = self.get_end()

        # Init fig
        (fig, ax, patch_leg, label_leg) = init_fig(fig=fig, ax=ax, shape="rectangle")

        if is_arrow:  # Plot as double headed arrow
            ax.annotate(
                text="",
                xy=(end.real, end.imag),
                xytext=(begin.real, begin.imag),
                arrowprops=dict(arrowstyle="<->", linewidth=linewidth, color=color),
            )
        else:  # Plot as a line
            points = np.array([begin, end])
            ax.plot(
                points.real,
                points.imag,
                linestyle=linestyle,
                linewidth=linewidth,
                color=color,
            )

        # Add the Label
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

    # Inlined from Methods.Geometry.Segment.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Segment
            An Segment object

        Returns
        -------
        """

        end = self.end
        self.end = self.begin
        self.begin = end

    # Inlined from Methods.Geometry.Segment.rotate
    def rotate(self, angle):
        """Rotation of the Segment of angle

        Parameters
        ----------
        self : Segment
            An Segment Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None

        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationSegmentError("The angle must be a float or int ")

        # check if Segment is correct"
        self.check()

        # Modification from the rotation of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.end = self.end * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Segment.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Segment
            A Segment Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.end = self.end * scale_factor

    # Inlined from Methods.Geometry.Segment.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object)

        Parameters
        ----------
        self : Segment
            An Segment object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        if is_begin:
            self.end = self.get_middle()
        else:
            self.begin = self.get_middle()

    # Inlined from Methods.Geometry.Segment.split_line
    def split_line(self, Z1, Z2, is_join=False, prop_dict_join=None, *, DELTA=1e-09):
        """Cut the Segment according to a line defined by two complex
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
        top_split_list, bot_split_list : ([Segment], [Segment])
            Both part of the Segment (1 or 2 segment depending on cutting point)
        """

        Z_int = self.intersect_line(Z1, Z2)
        # Begin and end point in the line coordonate system
        Zb = (self.begin - Z1) * np.exp(-1j * np.angle(Z2 - Z1))
        Ze = (self.end - Z1) * np.exp(-1j * np.angle(Z2 - Z1))

        if len(Z_int) == 0:
            # No intersection copy the line
            if Zb.imag >= 0 and Ze.imag >= 0:
                # Begin and end on top
                return [self.copy()], []
            elif Zb.imag <= 0 and Ze.imag <= 0:
                # Begin and end on bot
                return [], [self.copy()]
            else:
                raise Exception("Split Segment error (case 0 int)")
            # return [self.copy()], []
        elif len(Z_int) == 1:
            # One intersection => Three possible lines
            # Begin => Intersection
            line1 = self.copy()
            line1.end = Z_int[0]
            # Intersection => End
            line2 = self.copy()
            line2.begin = Z_int[0]
            # begin or end on cutting line
            line3 = self.copy()

            # Return the correct line according to the points position
            if Zb.imag > DELTA and abs(Ze.imag) > DELTA:  # begin on top, end != Int
                return [line1], [line2]
            elif Zb.imag > DELTA:
                return [line3], []
            elif Zb.imag < -DELTA and abs(Ze.imag) > DELTA:  # begin on bot, end != Int
                return [line2], [line1]
            elif Zb.imag < -DELTA:
                return [], [line3]
            # Zb.imag == 0 => begin on cutting line
            elif Ze.imag > DELTA:  # End on top
                return [line3], []
            elif Ze.imag < -DELTA:  # End on bot
                return [], [line3]
            else:
                raise Exception("Split Segment error (case 1 int)")
        elif len(Z_int) == 2:
            # The segment is on the line => Copy the line twice
            return [self.copy()], [self.copy()]

    # Inlined from Methods.Geometry.Segment.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Segment according to a point on the segment

        Parameters
        ----------
        self : Segment
            An Segment object
        Z1 : complex
            Cutting point on the line
        is_begin : bool
            True to keep the part begin=>Z1, False for the part Z1=>end

        Returns
        -------
        """

        if not self.is_on_line(Z1):
            raise Exception("Point is not on the line")

        if is_begin:
            self.end = Z1
        else:
            self.begin = Z1

    # Inlined from Methods.Geometry.Segment.translate
    def translate(self, Zt):
        """Translate the Segment object

        Parameters
        ----------
        self : Segment
            An Segment object

        Zt : complex
            Complex value for translation

        Returns
        -------
        None
        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise PointTranslateSegmentError(
                "The point must be a complex number or int or float"
            )

        # check if the Segment is correct
        self.check()

        # Modification from the translation of Segment
        self.begin = self.begin + Zt
        self.end = self.end + Zt

    class PointSegmentError(Exception):
        """ """

    class NbPointSegmentDError(Exception):
        """ """

    class AngleRotationSegmentError(Exception):
        """ """

    class PointTranslateSegmentError(Exception):
        """ """


PointSegmentError = Segment.PointSegmentError
NbPointSegmentDError = Segment.NbPointSegmentDError
AngleRotationSegmentError = Segment.AngleRotationSegmentError
PointTranslateSegmentError = Segment.PointTranslateSegmentError
