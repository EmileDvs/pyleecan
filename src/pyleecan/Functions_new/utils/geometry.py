"""Functions merged from Geometry.inter_line_circle, Geometry.inter_line_line, Geometry.inter_circle_circle, Geometry.circle_from_3_points, Geometry.comp_flower_arc, Geometry.cut_lines_between_angle, Geometry.comp_surface_num (PLAN.md Step 8)."""

from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from ...Classes_new.geometry.line import Line


def inter_line_circle(Z1: complex, Z2: complex, R: float, Zc: complex = 0) -> list:
    """INTER_LINE_CIRCLE find the intersection between a circle of center Zc
    and radius r with a line defined by two points

    Parameters
    ----------
    Z1 : complex
        Complex coordinate of a point on the line
    Z2 : complex
        Complex coordinate of another point on the line
    R : float
        Radius of the circle [m]
    Zc : complex
        Complex coordinate of the center

    Returns
    -------
    Zlist: list
        List of the complex coordinates of the intersection
    """
    # Set the coordinate system on the circle center
    if np.abs(Zc) > 1e-6:
        Z1 = Z1 - Zc
        Z2 = Z2 - Zc
    else:
        Zc = 0

    x1 = Z1.real
    y1 = Z1.imag
    x2 = Z2.real
    y2 = Z2.imag

    dx = x2 - x1
    dy = y2 - y1
    dr = np.sqrt(dx**2 + dy**2)
    D = x1 * y2 - x2 * y1

    delta = R**2 * dr**2 - D**2
    if delta < 0:  # 0 point
        return []
    elif delta == 0:  # 1 point(tangent)
        return [(D * dy - 1j * D * dx) / dr**2 + Zc]

    else:  # 2 points
        if dy < 0:
            xs1 = (D * dy - dx * np.sqrt(delta)) / dr**2
            xs2 = (D * dy + dx * np.sqrt(delta)) / dr**2
        else:
            xs1 = (D * dy + dx * np.sqrt(delta)) / dr**2
            xs2 = (D * dy - dx * np.sqrt(delta)) / dr**2
        ys1 = (-D * dx + abs(dy) * np.sqrt(delta)) / dr**2
        ys2 = (-D * dx - abs(dy) * np.sqrt(delta)) / dr**2

        return [xs1 + 1j * ys1 + Zc, xs2 + 1j * ys2 + Zc]


def inter_line_line(Z1: complex, Z2: complex, Z3: complex, Z4: complex) -> list:
    """INTER_LINE_LINE find the intersection between two lines defined by two
    complex

    Parameters
    ----------
    Z1 : complex
        Complex coordinate of a point on the first line
    Z2 : complex
        Complex coordinate of another point on the first line
    Z3 : complex
        Complex coordinate of a point on the second line
    Z4 : complex
        Complex coordinate of another point on the second line

    Returns
    -------
        Zlist: list
            List of the complex coordinates of the intersection
            return [Z1, Z2] if the 4 points are aligned
    """

    # Check if the points are aligned
    Z12 = Z1 - Z2
    Z13 = Z1 - Z3
    Z14 = Z1 - Z4
    if (
        Z12.real * Z13.imag - Z12.imag * Z13.real == 0
        and Z12.real * Z14.imag - Z12.imag * Z14.real == 0
    ):
        return [Z1, Z2]

    # Compute the line equation
    (A1, B1, C1) = find_line_eq(Z1, Z2)
    (A2, B2, C2) = find_line_eq(Z3, Z4)
    # Compute the intersection
    D = A1 * B2 - B1 * A2
    Dx = C1 * B2 - B1 * C2
    Dy = A1 * C2 - C1 * A2
    if D != 0:
        x = Dx / D
        y = Dy / D
        return [x + 1j * y]
    else:
        return []


def find_line_eq(Z1: complex, Z2: complex):
    """Find the line equation (Ax+By=C)

    Parameters
    ----------
    Z1 : complex
        Complex coordinate of a point on the line
    Z2 : complex
         Complex coordinate of another point on the line

    Returns
    -------
    A, B, C : (float, float, float)
        Line equation parameters
    """
    A = Z1.imag - Z2.imag
    B = Z2.real - Z1.real
    C = Z1.real * Z2.imag - Z2.real * Z1.imag
    return (A, B, -C)


def inter_circle_circle(Zc1: complex, R1: float, Zc2: complex, R2: float) -> list:
    """INTER_CIRCLE_CIRCLE find the intersection between two circles
    defined by center and radius

    Parameters
    ----------
    Zc1 : complex
        Complex coordinate of the center of the first circle
    R1 : float
        Radius of the first circle
    Zc2 : complex
        Complex coordinate of the center of the second circle
    R2 : float
        Radius of the second circle

    Returns
    -------
    Zlist: list
        List of the complex coordinates of the intersection
    """

    D = abs(Zc1 - Zc2)

    # # Plot for debug
    # Circle = import_class("pyleecan.Classes", "Circle")
    # C1 = Circle(radius=R1, center=Zc1)
    # C2 = Circle(radius=R2, center=Zc2)
    # fig, ax = C1.plot(color=PATCH_COLOR_ALPHA, edgecolor="r")
    # C2.plot(fig=fig, ax=ax, color=PATCH_COLOR_ALPHA, edgecolor="b")
    # ax.plot(0, 0, "kx", zorder=0)
    # ax.plot(Zc1.real, Zc1.imag, "rx", zorder=0)
    # ax.plot(Zc2.real, Zc2.imag, "bx", zorder=0)
    # plt.show()

    # Set the coordinate system center Zc1, Zc2 on Ox+
    Zc1p = 0
    Zc2p = (Zc2 - Zc1) * np.exp(-1j * np.angle(Zc2 - Zc1))

    if D > R1 + R2:
        # The two circle are not big enought
        return []
    elif D == (R1 + R2):
        # Only one point between the two circles
        return [(Zc2p - R2) * np.exp(1j * np.angle(Zc2 - Zc1)) + Zc1]
    elif R2 > D + R1:
        # Particular cases First circle inside second circle
        return []
    elif R1 > D + R2:
        # Particular cases Second circle inside first circle
        return []
    elif R2 == D + R1:
        # Particular cases First circle inside second circle and one intersection
        return [(-R1) * np.exp(1j * np.angle(Zc2 - Zc1)) + Zc1]
    elif R1 == D + R2:
        # Particular cases First circle inside second circle and one intersection
        return [(Zc2p + R2) * np.exp(1j * np.angle(Zc2 - Zc1)) + Zc1]
    else:  # D < R1 and D < R2:
        # Intersection between the two circles
        # cf https://mathworld.wolfram.com/Circle-CircleIntersection.html
        x = (D**2 - R2**2 + R1**2) / (2 * D)
        y = np.sqrt(R1**2 - x**2)
        Z1 = (x + 1j * y) * np.exp(1j * np.angle(Zc2 - Zc1)) + Zc1
        Z2 = (x - 1j * y) * np.exp(1j * np.angle(Zc2 - Zc1)) + Zc1
        return [Z1, Z2]


def circle_from_3_points(Z1, Z2, Z3):
    """Return the center and radius of a circle defined by 3 points

    Parameters:
    -----------
    Z1 : complex
        First point coordinates
    Z2 : complex
        Second point coordinates
    Z3 : complex
        Third point coordinates

    Returns:
    --------
    R : float
        Radius of the circle [m]
    Zc : complex
        Coordinate of the circle center
    """

    if Z1.imag == Z2.imag and Z1.imag == Z3.imag:
        raise Exception("Error: The 3 points are aligned !")
    if Z1.real == Z2.real and Z1.real == Z3.real:
        raise Exception("Error: The 3 points are aligned !")

    # Avoid div by 0
    if Z3.imag == Z1.imag:
        # Change Z1 and Z2
        tmp = Z2
        Z2 = Z1
        Z1 = tmp

    X1 = Z1.real
    Y1 = Z1.imag

    X2 = Z2.real
    Y2 = Z2.imag

    X3 = Z3.real
    Y3 = Z3.imag

    # All three points are on the circle :
    # (X1-Xc)² + (Y1-Yc)² - R² =0  (Eq1)
    # (X2-Xc)² + (Y2-Yc)² - R² =0  (Eq2)
    # (X3-Xc)² + (Y3-Yc)² - R² =0  (Eq3)

    # (Eq1-Eq2)
    # (X1² -2*X1*Xc + Xc² + Y1² -2*Y1*Yc + Yc² - R²) - (X2² -2*X2*Xc + Xc² + Y2² -2*Y2*Yc + Yc² - R²) = 0
    # X1² - X2² + 2*(X2-X1)*Xc + Y1² - Y2² + 2*(Y2-Y1)*Yc = 0

    # (Eq1-Eq3)
    # X1² - X3² + 2*(X3-X1)*Xc + Y1² - Y3² + 2*(Y3-Y1)*Yc = 0
    # Yc = (-X1² + X3² - 2*(X3-X1)*Xc - Y1² + Y3²)/2*(Y3-Y1)

    # Yc into (Eq1-Eq2)
    # X1² - X2² + 2*(X2-X1)*Xc + Y1² - Y2² + 2*(Y2-Y1)*(-X1² + X3² - 2*(X3-X1)*Xc - Y1² + Y3²)/2*(Y3-Y1)= 0
    # A = (Y2-Y1)/(Y3-Y1)
    # -X1² + X2² - Y1² + Y2² = 2*(X2-X1)*Xc  + A(-X1² + X3² - 2*(X3-X1)*Xc - Y1² + Y3²)
    # -X1² + X2² - Y1² + Y2² + A(X1² -X3² +Y1² -Y3²) = 2*(X2-X1)*Xc - 2*A*(X3-X1)*Xc
    A = (Y2 - Y1) / (Y3 - Y1)
    Xc = (-(X1**2) + X2**2 - Y1**2 + Y2**2 + A * (X1**2 - X3**2 + Y1**2 - Y3**2)) / (
        2 * (X2 - X1) - 2 * A * (X3 - X1)
    )

    # Eq1-Eq3
    Yc = (-(X1**2) + X3**2 - 2 * (X3 - X1) * Xc - Y1**2 + Y3**2) / (2 * (Y3 - Y1))

    # Eq1
    R = np.sqrt((X1 - Xc) ** 2 + (Y1 - Yc) ** 2)

    return (R, Xc + 1j * Yc)


def comp_flower_arc(alpha: float, Rarc: float, Rext: float):
    """Compute the angle and end of a "flower arc".

    Parameters
    ----------
    alpha : float
        Angular width of the arc (angle(z_top_feft)=alpha/2)
    Rarc : float
        The radius of the arc to draw [m]
    Rext : float
        The radius of the external arc ((Rext,0) is on the
        flower arc) [m]

    Returns
    -------
    (alpha_lim,z_top_left,z_top_right) : (float, complex, complex)
        alpha_lim: angle of the arc [ard]
        z_top_left: first point of the arc
        z_top_right: second point fo the arc

    """
    # For readibility
    R = Rarc
    T = np.tan(alpha / 2)

    # Computation of the angle of the Arc (analitical solution for
    # equation : tan(alpha_mag/2) = Rsin(alpha)/(Rext-R(1-cos(alpha))
    alpha_lim1 = -2 * np.arctan(
        (R + np.sqrt(R**2 + 2 * R * Rext * T**2 - Rext**2 * T**2))
        / (T * (2 * (R - Rext)))
    )
    alpha_lim2 = -2 * np.arctan(
        (R - np.sqrt(R**2 + 2 * R * Rext * T**2 - Rext**2 * T**2))
        / (T * (2 * R - Rext))
    )
    alpha_lim = min(abs(alpha_lim1), abs(alpha_lim2))

    z_top_left = R * np.exp(+1j * alpha_lim) + (Rext - R)
    z_top_right = R * np.exp(-1j * alpha_lim) + (Rext - R)

    return (alpha_lim, z_top_left, z_top_right)


def cut_lines_between_angles(
    line_list: list[Line], begin_angle: float, end_angle: float
) -> list[Line]:
    """Cut a list of lines between two angles
    Assume that the lines draw a closed surface centered on O
    Constraint: end_angle - begin_angle < pi (first cut remove half the lines)

    Parameters
    ----------
    line_list : [Line]
        list of line to cut
    begin_angle : float
        Begin angle of the cut [rad]
    end_angle : float
        End angle of the cut [rad]

    Returns
    -------
    cut_lines : [Line]
        Cut lines between the two angles
    """

    first_cut = []
    cut_lines = []
    # First cut
    for line in line_list:
        top_split_list, _ = line.split_line(0, np.exp(1j * begin_angle))
        first_cut.extend(top_split_list)
    # Second cut
    for line in first_cut:
        _, bot_split_list = line.split_line(0, np.exp(1j * end_angle))
        cut_lines.extend(bot_split_list)

    # Check that lines are in the correct way
    if (np.angle(cut_lines[0].get_begin()) % (2 * np.pi)) - (
        begin_angle % (2 * np.pi)
    ) > 1e-6:
        cut_lines = cut_lines[::-1]

    return cut_lines


def comp_surface_num(point_list: list) -> float:
    """Compute the surface of the Polygon defined by the points

    Parameters
    ----------
    point_list : list
        List of complex coordinate of the points

    Returns
    -------
    S: float
        Surface of the closed surface [m**2]

    """

    # We have to be sure that the surface is closed
    # (ie point_list[0]=point_list[end]) If it's already the case Xi+1 - Xi =0
    point_list.append(point_list[0])

    point_array = np.array(point_list)

    # We translate the points so every point have imag >=0
    min_imag = min(point_array.imag)
    if min_imag < 0:
        point_array += abs(min_imag) * 1j

    S_acc = 0
    for ii in range(point_array.size - 1):
        Var_X = point_array[ii + 1].real - point_array[ii].real
        Var_Y = point_array[ii + 1].imag + point_array[ii].imag

        S_acc += Var_Y * Var_X

    return abs(S_acc / 2.0)
