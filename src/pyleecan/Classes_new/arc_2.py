# Experimental dataclass generated from Generator/ClassesRef/Geometry/Arc2.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .arc import Arc


@dataclass(eq=False)
class Arc2(Arc):
    """An arc between two points (defined by the begin  point and a center and angle)

    Attributes
    ----------
    begin : complex
        begin point of the arc
        Default: 0
    center : complex
        center of the arc
        Default: 0
    angle : float
        opening angle of the arc
        Unit: rad; Default: 1.57079633; Minimum: -6.283185308; Maximum: 6.283185308
    """

    begin: complex = 0
    """begin point of the arc"""
    center: complex = 0
    """center of the arc"""
    angle: float = 1.57079633
    """opening angle of the arc"""

    # Inlined from Methods.Geometry.Arc2.check
    def check(self):
        """assert that the arc is correct (begin != center)

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        None

        Raises
        ------
        PointArc2Error
            The beginning point and the ending point of an Arc2
            can't be the same
        AngleArc2Error
            An Arc2 can't have a null opening angle
        """

        if self.begin == self.center or (
            abs(self.begin) == 0 and abs(self.center) == 0
        ):
            raise self.PointArc2Error
            ("The beginning point and the center of an Arc2 can't be the same")
        if self.angle == 0:
            raise self.AngleArc2Error("An arc can't have a null opening angle")
        if self.angle == 2 * np.pi:
            raise self.AngleArc2Error("You can't draw a circle with an Arc2")

    # Inlined from Methods.Geometry.Arc2.comp_length
    def comp_length(self):
        """Compute the length of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        length: float
            length of the arc
        """

        R = abs(self.comp_radius())  # Radius of the arc
        angle = self.angle

        # 2*pi*R is the length of the total circle
        # The arc is an alpha / 2pi portion of the cercle
        return float(2 * np.pi * R * (abs(angle) / (2 * np.pi)))

    # Inlined from Methods.Geometry.Arc2.comp_radius
    def comp_radius(self):
        """Compute the radius of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        radius: float
            radius of the arc
        """

        self.check()

        z1 = self.begin
        zc = self.center
        return float(np.abs(z1 - zc))  # Radius of the arc

    # Inlined from Methods.Geometry.Arc2.discretize
    def discretize(self, nb_point=Arc.ARC_NPOINT_D):
        """Return the discretize version of the Arc.
        Begin and end are always returned

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        nb_point : int
            Number of points to add to discretize the arc (Default value = ARC_NPOINT_D)

        Returns
        -------
        list_point: list
            list of complex coordinate of the points

        Raises
        ------
        NbPointArc2DError
            nb_point must be an integer >=0
        """

        self.check()
        if not isinstance(nb_point, int):
            raise self.NbPointArc2DError("discretize : nb_point must be an integer")
        if nb_point < 0:
            raise self.NbPointArc2DError("nb_point must be >=0")

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.center

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        t = np.linspace(0, self.angle, nb_point + 2)
        list_point = Zstart * np.exp(1j * t)

        # Geometric transformation : return to the main axis
        list_point = list_point * np.exp(1j * np.angle(z1 - zc)) + zc

        return list_point

    # Inlined from Methods.Geometry.Arc2.get_angle
    def get_angle(self, is_deg=False):
        """Return the angle of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        is_deg: bool
            True to convert to degree

        Returns
        -------
        angle: float
            Angle of the arc
        """

        if is_deg:
            return self.angle * 180 / np.pi
        else:
            return self.angle

    # Inlined from Methods.Geometry.Arc2.get_begin
    def get_begin(self):
        """Return the begin point of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        begin: complex
            begin point of the Arc2
        """

        return self.begin

    # Inlined from Methods.Geometry.Arc2.get_center
    def get_center(self):
        """Return the center point of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        center: complex
            center point of the Arc2
        """

        return self.center

    # Inlined from Methods.Geometry.Arc2.get_end
    def get_end(self):
        """Return the end of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        end: complex
            Complex coordinates of the end of the Arc2
        """

        self.check()

        # the center is on the bisection of [begin, end]
        z1 = self.begin
        zc = self.center
        angle = self.angle

        # Geometric transformation : center is the origine (-zc)
        # Then rotation of begin of the correct angle (*exp(i*pi*angle))
        # Then return to the main axis (+zc)
        z2 = (z1 - zc) * np.exp(1j * angle) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(z2) < 1e-6:
            z2 = 0
        return z2

    # Inlined from Methods.Geometry.Arc2.get_middle
    def get_middle(self):
        """Return the point at the middle of the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        Zmid: complex
            Complex coordinates of the middle of the Arc2
        """

        self.check()

        # We use the complex representation of the point
        z1 = self.begin
        zc = self.center

        # Geometric transformation : center is the origine, angle(begin) = 0
        Zstart = (z1 - zc) * np.exp(-1j * np.angle(z1 - zc))

        # Generation of the point by rotation
        Zmid = Zstart * np.exp(1j * self.angle / 2.0)

        # Geometric transformation : return to the main axis
        Zmid = Zmid * np.exp(1j * np.angle(z1 - zc)) + zc

        # Return (0,0) if the point is too close from 0
        if np.abs(Zmid) < 1e-6:
            Zmid = 0

        return Zmid

    # Inlined from Methods.Geometry.Arc2.reverse
    def reverse(self):
        """Reverse the begin and end point of the Line

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Returns
        -------
        """

        self.begin = self.get_end()
        self.angle = -self.angle

    # Inlined from Methods.Geometry.Arc2.rotate
    def rotate(self, angle):
        """Rotation of the Arc2 of angle

        Parameters
        ----------
        self : Arc2
            An Arc2 Object

        angle : float
            the angle of rotation [rad]

        Returns
        -------
        None
        """
        if not isinstance(angle, float) and not isinstance(angle, int):
            raise self.AngleRotationArc2Error("The angle must be a float or int")

        # check if Arc2 is correct"
        self.check()

        # Modification from the rotation  of the object
        self.begin = self.begin * np.exp(1j * angle)
        self.center = self.center * np.exp(1j * angle)

    # Inlined from Methods.Geometry.Arc2.scale
    def scale(self, scale_factor):
        """Scale the coordinates of the begin/end

        Parameters
        ----------
        self : Arc2
            An Arc2 Object
        scale_factor : float
            the Scale factor [-]

        Returns
        -------
        None
        """

        self.begin = self.begin * scale_factor
        self.center = self.center * scale_factor

    # Inlined from Methods.Geometry.Arc2.split_half
    def split_half(self, is_begin=True):
        """Cut the line in half (modify the object)

        Parameters
        ----------
        self : Arc2
            An Arc2 object
        is_begin : bool
            True to keep the part begin=>middle, False for the part middle=>end

        Returns
        -------
        """

        if not is_begin:
            self.begin = self.get_middle()
        self.angle = self.angle / 2

    # Inlined from Methods.Geometry.Arc2.split_point
    def split_point(self, Z1, is_begin=True):
        """Cut the Arc according to a point on the arc

        Parameters
        ----------
        self : Arc2
            An Arc2 object
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

        if is_begin:
            self.angle = np.angle((Z1 - Zc) * np.exp(-1j * np.angle(self.begin)))
        else:
            self.angle = np.angle((self.get_end() - Zc) * np.exp(-1j * np.angle(Z1)))
            self.begin = Z1

    # Inlined from Methods.Geometry.Arc2.translate
    def translate(self, Zt):
        """Translate the Arc2 object with

        Parameters
        ----------
        self : Arc2
            An Arc2 object

        Zt : complex
            Complex coordinates value for translation

        Returns
        -------
        None
        """
        if (
            not isinstance(Zt, complex)
            and not isinstance(Zt, int)
            and not isinstance(Zt, float)
        ):
            raise self.PointTranslateArc2Error(
                "The point must be a complex number or int or float"
            )

        # check if the Arc2 is correct
        self.check()

        # Modification from the translation of Arc2
        self.begin = self.begin + Zt
        self.center = self.center + Zt

    class AngleArc2Error(Exception):
        """ """

    class AngleRotationArc2Error(Exception):
        """ """

    class NbPointArc2DError(Exception):
        """ """

    class PointArc2Error(Exception):
        """ """

    class PointTranslateArc2Error(Exception):
        """ """
