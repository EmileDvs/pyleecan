# Experimental dataclass generated from Generator/ClassesRef/Geometry/Arc1.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .arc import Arc
from .machine import ARC_NPOINT_D


@dataclass(eq=False)
class Arc1(Arc):
    """An arc between two points (defined by a radius)

    Attributes
    ----------
    begin : complex
        begin point of the arc
        Default: 0
    end : complex
        end point of the arc
        Default: 0
    radius : float
        Radius of the arc (can be + or -)
        Default: 0
    is_trigo_direction : bool
        Rotation direction of the arc
        Default: True
    """

    begin: complex = 0
    """begin point of the arc"""
    end: complex = 0
    """end point of the arc"""
    radius: float = 0
    """Radius of the arc (can be + or -)"""
    is_trigo_direction: bool = True
    """Rotation direction of the arc"""

    # Inlined from Methods.Geometry.Arc1.check
    def check(self):
        """assert that the arc is correct (begin != end; radius !=0)

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        None

        Raises
        ------
        PointArc1Error
            The beginning point and the ending point of an Arc1
            can't be the same
        RadiusArc1Error
            An Arc1 can't have a null radius

        """

        if self.begin == self.end or (abs(self.begin) == 0 and abs(self.end) == 0):
            raise PointArc1Error(
                "The beginning point and the ending "
                + "point of an Arc1 can't be "
                + "the same"
            )
        if self.radius == 0:
            raise RadiusArc1Error("An Arc1 can't have a null radius")

    # Inlined from Methods.Geometry.Arc1.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        length: float
            length of the arc
        """

        self.check()

        R = abs(self.radius)

        # alpha is the opening angle
        alpha = abs(self.get_angle())

        # 2*pi*R is the length of the total circle
        # The arc is an alpha / 2pi portion of the cercle
        return float(2 * np.pi * R * (alpha / (2 * np.pi)))

    # Inlined from Methods.Geometry.Arc1.comp_radius
    def comp_radius(self):
        """Compute the Radius of the Arc1 (for unification with other arc objects)

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        radius: float
            radius of the arc
        """

        self.check()

        return abs(self.radius)  # Radius of the arc

    # Inlined from Methods.Geometry.Arc1.discretize
    def discretize(self, nb_point=ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always returned

        Parameters
        ----------
        self : Arc1
            The Arc1 object to discretize
        nb_point :
            Number of points to add to discretize the arc (Default value = ARC_NPOINT_D)

        Returns
        -------
        list_point: list
            list of complex coordinate of the points

        Raises
        ------
        NbPointArc1DError
            nb_point must be an integer >=0
        """

        # Check that the Arc is correct
        self.check()
        if not isinstance(nb_point, int):
            raise NbPointArc1DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise NbPointArc1DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        z2 = self.end
        zc = self.get_center()

        # Geometric transformation : center is the origin, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))
        Zend = (z2 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        if self.is_trigo_direction:
            sign = 1
        else:
            sign = -1
        t = np.linspace(0, self.get_angle(), nb_point + 2)
        list_point = Zstart * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # Inlined from Methods.Geometry.Arc1.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """
        # Go to center ref with begin on the X > 0 axis
        Zc = self.get_center()
        Z2 = (self.end - Zc) * np.exp(-1j * np.angle(self.begin - Zc))

        if Z2.imag > 0 and self.is_trigo_direction:
            alpha = np.angle(Z2)
        elif Z2.imag > 0 and not self.is_trigo_direction:
            alpha = -(2 * np.pi - np.angle(Z2))
        elif Z2.imag < 0 and self.is_trigo_direction:
            alpha = 2 * np.pi - abs(np.angle(Z2))
        elif Z2.imag < 0 and not self.is_trigo_direction:
            alpha = np.angle(Z2)
        elif Z2.imag == 0 and self.is_trigo_direction:
            alpha = abs(np.angle(Z2))
        elif Z2.imag == 0 and not self.is_trigo_direction:
            alpha = -abs(np.angle(Z2))
        else:
            alpha = 0

        if is_deg:
            return alpha * 180 / np.pi
        else:
            return alpha

    # Inlined from Methods.Geometry.Arc1.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        begin: complex
            Complex coordinates of the begin point of the Arc1
        """

        return self.begin

    # Inlined from Methods.Geometry.Arc1.get_center
    def get_center(self):
        """Return the center of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        Zc: complex
            Complex coordinates of the center of the Arc1
        """

        self.check()

        # The center is on the bisection of [begin, end]
        z1 = self.begin
        z2 = self.end
        R = self.radius
        D12 = np.abs(z2 - z1)  # length of segment [begin,end]

        # Centre at the middle of begin and end (distance(Z1, Z2) = diameter )
        if np.abs(D12 - np.abs(2 * R)) < 1e-6:
            Zc = (z2 + z1) / 2.0
        else:
            # In the coordinate system begin on center and end on X > 0 axis
            if R > 0:  # Center is above the segment
                Zc = D12 / 2 + 1j * np.sqrt(R**2 - (D12 / 2) ** 2)
            else:
                Zc = D12 / 2 - 1j * np.sqrt(R**2 - (D12 / 2) ** 2)
            # Go back to the original coordinate system
            Zc = Zc * np.exp(1j * np.angle(z2 - z1)) + z1

        # Return (0,0) if the point is too close from 0
        if np.abs(Zc) < 1e-6:
            Zc = 0

        return Zc

    # Inlined from Methods.Geometry.Arc1.get_end
    def get_end(self):
        """Return the end point of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        end: complex
            Complex coordinates of the end point of the Arc1
        """

        return self.end

    # Inlined from Methods.Geometry.Arc1.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc1
        """

        # We use the complex representation of the point
        z1 = self.begin
        z2 = self.end
        zc = self.get_center()

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        alpha = self.get_angle()
        Zmid = Zstart * np.exp(1j * alpha / 2)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # Inlined from Methods.Geometry.Arc1.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc1
            An Arc1 object

        Returns
        -------
        """

        end = self.end
        self.end = self.begin
        self.begin = end
        self.radius = -self.radius
        self.is_trigo_direction = not self.is_trigo_direction

    # Inlined from Methods.Geometry.Arc1.rotate
    def rotate(self, angle):
        """Rotation of the Arc1 of <angle> rad with 0 as the center

        Parameters
        ----------
        self : Arc1
            An Arc1 Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise AngleRotationArc1Error("The angle must be a float or int ")

        # check if Arc1 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.end = self.end * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Arc1.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc1
            An Arc1 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.end = self.end * scale_factor
        self.radius = self.radius * scale_factor

    # Inlined from Methods.Geometry.Arc1.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object)

        Parameters
        ----------
        self : Arc1
            An Arc1 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        # Check that the center is the same
        Zc = self.get_center()

        if is_begin:
            self.end = self.get_middle()
        else:
            self.begin = self.get_middle()

        # Correct center if needed
        if abs(Zc - self.get_center()) > 1e-6:
            self.radius = -1 * self.radius

    # Inlined from Methods.Geometry.Arc1.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc1
            An Arc1 object
        Z1 : complex
            Cutting point on the line
        is_begin : bool
            True to keep the part begin=>Z1, False for the part Z1=>end

        Returns
        -------
        """

        # Check if the point is on the circle
        Zc = self.get_center()
        R = self.comp_radius()
        if abs(np.abs(Z1 - Zc) - R) > 1e-6:
            raise Exception("Point is not on the line")

        # Check that the center is the same
        if is_begin:
            self.end = Z1
        else:
            self.begin = Z1

        # Correct center if needed
        if abs(Zc - self.get_center()) > 1e-6:
            self.radius = -1 * self.radius

    # Inlined from Methods.Geometry.Arc1.translate
    def translate(self, Zt):
        """Translate the Arc1 object

        Parameters
        ----------
        self : Arc1
            An Arc1 object

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
            raise PointTranslateArc1Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc1 is correct
        self.check()

        # Modification from the translation of Arc1
        self.begin = self.begin + Zt
        self.end = self.end + Zt

    class PointArc1Error(Exception):
        """ """

    class RadiusArc1Error(Exception):
        """ """

    class NbPointArc1DError(Exception):
        """ """

    class AngleRotationArc1Error(Exception):
        """ """

    class PointTranslateArc1Error(Exception):
        """ """


PointArc1Error = Arc1.PointArc1Error
RadiusArc1Error = Arc1.RadiusArc1Error
NbPointArc1DError = Arc1.NbPointArc1DError
AngleRotationArc1Error = Arc1.AngleRotationArc1Error
PointTranslateArc1Error = Arc1.PointTranslateArc1Error
