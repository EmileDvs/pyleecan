import numpy as np


def xyz_to_rphiz(values):
    """Converts axis values from cartesian coordinates into cylindrical coordinates

    Parameters
    ----------
    values: array
        Values of the axis to convert (Nx3)
    Returns
    -------
    ndarray of the axis (Nx3)
    """

    x = values[:, 0]
    y = values[:, 1]
    z = values[:, 2]

    affixe = x + 1j * y
    r = np.abs(affixe)
    phi = (np.angle(affixe) + 2 * np.pi) % (2 * np.pi)

    return np.column_stack((r, phi, z))


def rphiz_to_xyz(values):
    """Converts axis values from cylindrical coordinates into cartesian coordinates

    Parameters
    ----------
    values: array
        Values of the axis to convert (Nx3)
    Returns
    -------
    ndarray of the axis (Nx3)
    """

    r = values[:, 0]
    phi = values[:, 1]
    z = values[:, 2]

    affixe = r * np.exp(1j * phi)
    x = np.real(affixe)
    y = np.imag(affixe)

    return np.column_stack((x, y, z))


def xyz_to_rphiz_field(values, phi):
    """Converts field values from cartesian coordinates into cylindrical coordinates

    Parameters
    ----------
    values: array
        Values of the field to convert (Nx3)
    phi: array
        Values of the angle axis (N)
    Returns
    -------
    ndarray of the field (Nx3)
    """

    field_x = values[:, 0]
    field_y = values[:, 1]

    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    field_r = cos_phi * field_x + sin_phi * field_y
    field_phi = -sin_phi * field_x + cos_phi * field_y

    if values.shape[1] == 3:
        field_z = values[:, 2]
        out_field = np.column_stack((field_r, field_phi, field_z))
    else:
        out_field = np.column_stack((field_r, field_phi))

    return out_field


def rphiz_to_xyz_field(values, phi):
    """Converts field values from cylindrical coordinates into cartesian coordinates

    Parameters
    ----------
    values: array
        Values of the field to convert (Nx3)
    phi: array
        Values of the angle axis (N)
    Returns
    -------
    ndarray of the field (Nx3)
    """

    field_r = values[:, 0]
    field_phi = values[:, 1]

    cos_phi = np.cos(phi)
    sin_phi = np.sin(phi)

    field_x = cos_phi * field_r - sin_phi * field_phi
    field_y = sin_phi * field_r + cos_phi * field_phi

    if values.shape[1] == 3:
        field_z = values[:, 2]
        out_field = np.column_stack((field_x, field_y, field_z))
    else:
        out_field = np.column_stack((field_x, field_y))

    return out_field


def cart2pol(values, points):
    """Converts field values from cartesian coordinates into cylindrical coordinates

    Parameters
    ----------
    values: array
        Values of the field to convert (Nx3)
    phi: array
        Values of the angle axis (N)
    Returns
    -------
    ndarray of the field (Nx3)
    """

    phi = xyz_to_rphiz(points)[:, 1]
    return xyz_to_rphiz_field(values, phi)


def pol2cart(values, points):
    """Converts field values from cylindrical coordinates into cartesian coordinates

    Parameters
    ----------
    values: array
        Values of the field to convert (Nx3)
    phi: array
        Values of the angle axis (N)
    Returns
    -------
    ndarray of the field (Nx3)
    """

    phi = xyz_to_rphiz(points)[:, 1]
    return rphiz_to_xyz_field(values, phi)
