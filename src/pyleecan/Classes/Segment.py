# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Segment.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Segment
"""

from os import linesep
from sys import getsizeof
from logging import getLogger
from pyleecan.Classes._check import check_var, raise_
from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.save import save
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.Load.import_class import import_class
from copy import deepcopy
from pyleecan.Classes.Line import Line

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
import numpy as np
from pyleecan.Classes.Machine import LINE_NPOINT_D
from pyleecan.Functions.Geometry.inter_line_line import inter_line_line
from pyleecan.Functions.Geometry.inter_line_circle import inter_line_circle
from pyleecan.Functions.init_fig import init_fig
from pyleecan.Functions.Plot import TEXT_BOX


from pyleecan.Classes._check import InitUnKnowClassError


class Segment(Line):
    """A segment between two points"""

    VERSION = 1

    # cf Methods.Geometry.Segment.check
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

    # cf Methods.Geometry.Segment.comp_distance
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

    # cf Methods.Geometry.Segment.comp_length
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

    # cf Methods.Geometry.Segment.discretize
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

    # cf Methods.Geometry.Segment.draw_FEMM
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

    # cf Methods.Geometry.Segment.get_begin
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

    # cf Methods.Geometry.Segment.get_end
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

    # cf Methods.Geometry.Segment.get_middle
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

    # cf Methods.Geometry.Segment.intersect_line
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

    # cf Methods.Geometry.Segment.intersect_obj
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
        Z_list = list()
        for Z in inter_list:
            if self.is_on_line(Z) and other.is_on_line(Z):
                Z_list.append(Z)

        return Z_list

    # cf Methods.Geometry.Segment.is_arc
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

    # cf Methods.Geometry.Segment.is_on_line
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

    # cf Methods.Geometry.Segment.plot
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

    # cf Methods.Geometry.Segment.reverse
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

    # cf Methods.Geometry.Segment.rotate
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

    # cf Methods.Geometry.Segment.scale
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

    # cf Methods.Geometry.Segment.split_half
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

    # cf Methods.Geometry.Segment.split_line
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

    # cf Methods.Geometry.Segment.split_point
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

    # cf Methods.Geometry.Segment.translate
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, begin=0, end=0, prop_dict=None, init_dict=None, init_str=None):
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
            if "begin" in list(init_dict.keys()):
                begin = init_dict["begin"]
            if "end" in list(init_dict.keys()):
                end = init_dict["end"]
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
        # Set the properties (value check and convertion are done in setter)
        self.begin = begin
        self.end = end
        # Call Line init
        super(Segment, self).__init__(prop_dict=prop_dict)
        # The class is frozen (in Line init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Segment_str = ""
        # Get the properties inherited from Line
        Segment_str += super(Segment, self).__str__()
        Segment_str += "begin = " + str(self.begin) + linesep
        Segment_str += "end = " + str(self.end) + linesep
        return Segment_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Line
        if not super(Segment, self).__eq__(other):
            return False
        if other.begin != self.begin:
            return False
        if other.end != self.end:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from Line
        diff_list.extend(
            super(Segment, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if other._begin != self._begin:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._begin) + ", other=" + str(other._begin) + ")"
                )
                diff_list.append(name + ".begin" + val_str)
            else:
                diff_list.append(name + ".begin")
        if other._end != self._end:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._end) + ", other=" + str(other._end) + ")"
                )
                diff_list.append(name + ".end" + val_str)
            else:
                diff_list.append(name + ".end")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Line
        S += super(Segment, self).__sizeof__()
        S += getsizeof(self.begin)
        S += getsizeof(self.end)
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

        # Get the properties inherited from Line
        Segment_dict = super(Segment, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        if self.begin is None:
            Segment_dict["begin"] = None
        elif isinstance(self.begin, float):
            Segment_dict["begin"] = self.begin
        else:
            Segment_dict["begin"] = str(self.begin)
        if self.end is None:
            Segment_dict["end"] = None
        elif isinstance(self.end, float):
            Segment_dict["end"] = self.end
        else:
            Segment_dict["end"] = str(self.end)
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Segment_dict["__class__"] = "Segment"
        return Segment_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        begin_val = self.begin
        end_val = self.end
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(begin=begin_val, end=end_val, prop_dict=prop_dict_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.begin = None
        self.end = None
        # Set to None the properties inherited from Line
        super(Segment, self)._set_None()

    def _get_begin(self):
        """getter of begin"""
        return self._begin

    def _set_begin(self, value):
        """setter of begin"""
        if isinstance(value, str):
            value = complex(value)
        check_var("begin", value, "complex")
        self._begin = value

    begin = property(
        fget=_get_begin,
        fset=_set_begin,
        doc="""begin point of the line

        :Type: complex
        """,
    )

    def _get_end(self):
        """getter of end"""
        return self._end

    def _set_end(self, value):
        """setter of end"""
        if isinstance(value, str):
            value = complex(value)
        check_var("end", value, "complex")
        self._end = value

    end = property(
        fget=_get_end,
        fset=_set_end,
        doc="""end point of the line

        :Type: complex
        """,
    )

    class PointSegmentError(Exception):
        """ """

        pass

    class NbPointSegmentDError(Exception):
        """ """

        pass

    class AngleRotationSegmentError(Exception):
        """ """

        pass

    class PointTranslateSegmentError(Exception):
        """ """

        pass


PointSegmentError = Segment.PointSegmentError

NbPointSegmentDError = Segment.NbPointSegmentDError

AngleRotationSegmentError = Segment.AngleRotationSegmentError

PointTranslateSegmentError = Segment.PointTranslateSegmentError
