# -*- coding: utf-8 -*-
# File generated according to Generator/ClassesRef/Geometry/Arc.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Geometry/Arc
"""

# Inline fallback report:
# These methods remain imported because their source or imports cannot be safely moved into this class.
# - comp_maxseg: import name 'sqrt' refers to different sources (numpy.sqrt and ..Methods.Geometry.Arc.comp_maxseg.sqrt)
# - split_line: import name 'angle' refers to different sources (numpy.angle and ..Methods.Geometry.Arc.split_line.angle)

from os import linesep
from sys import getsizeof
from logging import getLogger
from ._check import check_var, raise_
from ..Functions.get_logger import get_logger
from ..Functions.save import save
from ..Functions.load import load_init_dict
from ..Functions.Load.import_class import import_class
from copy import deepcopy
from .Line import Line

# Import all class method
# Try/catch to remove unnecessary dependencies in unused method
from ..Methods.Geometry.Arc.comp_maxseg import comp_maxseg
from ..Methods.Geometry.Arc.split_line import split_line
from numpy import sqrt, angle, exp, sign, abs, pi, abs as np_abs
from ..Functions.Geometry.inter_line_circle import inter_line_circle
from ..Functions.Geometry.inter_circle_circle import inter_circle_circle
from ..Functions.init_fig import init_fig
from ..Functions.Plot import TEXT_BOX

from numpy import isnan
from ._check import InitUnKnowClassError


class Arc(Line):
    """Abstract class for arc"""

    VERSION = 1

    # cf Methods.Geometry.Arc.comp_distance
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
        A2 = angle(Z2 * exp(-1j * angle(self.get_begin() - Zc)))

        if sign(A1) == sign(A2) and abs(A2) < abs(A1):
            # The point is on the correct side of the arc
            D1 = abs(sqrt(Z2.real**2 + Z2.imag**2) - self.comp_radius())
            return D1
        else:
            D2 = abs(Z - self.get_begin())
            D3 = abs(Z - self.get_end())
            D4 = abs(Z - self.get_middle())
            return min([D2, D3, D4])

    # cf Methods.Geometry.Arc.comp_maxseg
    comp_maxseg = comp_maxseg

    # cf Methods.Geometry.Arc.draw_FEMM
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

        if abs(angle) > 180:
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
            mid1 = cent + (mid - cent) * exp(1j * angle / 4)
            mid2 = cent + (mid - cent) * exp(-1j * angle / 4)
            femm.mi_selectarcsegment(mid1.real, mid1.imag)
            femm.mi_selectarcsegment(mid2.real, mid1.imag)
        else:
            femm.mi_selectarcsegment(X2, Y2)

        maxseg = self.comp_maxseg(element_size, maxseg)
        femm.mi_setarcsegmentprop(maxseg, propname, hide, group)
        femm.mi_clearselected()

    # cf Methods.Geometry.Arc.intersect_line
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
            if np_abs(Zlist[0] - begin) < 1e-6:
                # First point is begin
                return Zlist
            if np_abs(Zlist[1] - begin) < 1e-6:
                # Second point is begin
                return Zlist[::-1]

            # Go to the coordinate system Zc as center, begin on X > 0 axis
            Z1 = (Zlist[0] - Zc) * exp(-1j * angle(begin - Zc))
            Z2 = (Zlist[1] - Zc) * exp(-1j * angle(begin - Zc))

            alpha = self.get_angle()
            A1 = angle(Z1) % (2 * pi)
            A2 = angle(Z2) % (2 * pi)
            # Check if Zlist needs to be reversed
            if alpha > 0 and A1 > A2:
                return Zlist[::-1]
            if alpha < 0 and A2 > A1:
                return Zlist[::-1]
        return Zlist

    # cf Methods.Geometry.Arc.intersect_obj
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
        Z_list = list()
        for Z in inter_list:
            if self.is_on_line(Z) and other.is_on_line(Z):
                Z_list.append(Z)

        return Z_list

    # cf Methods.Geometry.Arc.is_arc
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

    # cf Methods.Geometry.Arc.is_on_line
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
        if abs(np_abs(Z - Zc) - R) > 1e-6:
            return False

        # Check if point is begin or end
        begin = self.get_begin()
        end = self.get_end()
        if np_abs(Z - begin) < 1e-6:
            return True
        if np_abs(Z - end) < 1e-6:
            return True

        # Go to the coordinate system Zc as center, begin on X > 0 axis
        Ze = (end - Zc) * exp(-1j * angle(begin - Zc))
        Z = (Z - Zc) * exp(-1j * angle(begin - Zc))

        alpha = self.get_angle()
        Ae = angle(Ze) % (2 * pi)
        Az = angle(Z) % (2 * pi)
        if alpha > 0:  # Trigo direction
            if Ae > Az:
                return True
            return False
        # Clockwise direction
        if Az > Ae:
            return True
        return False

    # cf Methods.Geometry.Arc.plot
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

    # cf Methods.Geometry.Arc.split_line
    split_line = split_line
    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(self, prop_dict=None, init_dict=None, init_str=None):
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
            if "prop_dict" in list(init_dict.keys()):
                prop_dict = init_dict["prop_dict"]
        # Set the properties (value check and convertion are done in setter)
        # Call Line init
        super(Arc, self).__init__(prop_dict=prop_dict)
        # The class is frozen (in Line init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        Arc_str = ""
        # Get the properties inherited from Line
        Arc_str += super(Arc, self).__str__()
        return Arc_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from Line
        if not super(Arc, self).__eq__(other):
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
            super(Arc, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from Line
        S += super(Arc, self).__sizeof__()
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
        Arc_dict = super(Arc, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        Arc_dict["__class__"] = "Arc"
        return Arc_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        if self.prop_dict is None:
            prop_dict_val = None
        else:
            prop_dict_val = self.prop_dict.copy()
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(prop_dict=prop_dict_val)
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        # Set to None the properties inherited from Line
        super(Arc, self)._set_None()
