from os.path import join

import pytest
from numpy import cos, linspace, meshgrid, pi, sin, zeros

from SciDataTool import Data1D, DataLinspace, DataTime, Norm_affine
from Tests import save_validation_path


@pytest.mark.validation
# @pytest.mark.DEV
@pytest.mark.parametrize(
    ("axis1", "axis2", "plot_name"),
    [
        ("time", "angle=[0,pi/4,pi/2]", "plot_2D"),
        ("freqs", "angle=[0,pi/4,pi/2]", "plot_2D_freqs"),
        ("wavenumber", "", "plot_2D_wavenumber"),
        ("wavenumber", r"freqs=1{Hz}", "plot_2D_wavenumber_freq"),
    ],
)
def test_plot_2D(axis1, axis2, plot_name):
    """Test plot"""
    Time = DataLinspace(name="time", unit="s", initial=0, final=10, number=1001)
    Angle = DataLinspace(name="angle", unit="rad", initial=0, final=2 * pi, number=2001)
    angle, time = meshgrid(Angle.get_values(), Time.get_values())
    field = time + angle
    Field = DataTime(name="Example field", symbol="Z", axes=[Time, Angle], values=field)

    Field.plot_2D_Data(
        axis1,
        axis2,
        is_show_fig=False,
        save_path=join(save_validation_path, f"{plot_name}.png"),
    )


@pytest.mark.validation
# @pytest.mark.DEV
@pytest.mark.parametrize(
    ("axis1", "axis2", "view_2D", "plot_name"),
    [
        ("time", r"angle{°}", True, "plot_3D_flat"),
        ("time", r"angle{°}", False, "plot_3D"),
        ("freqs", "wavenumber", True, "plot_3D_freqs_wavenumber_flat"),
        pytest.param(
            "freqs",
            "wavenumber",
            False,
            "plot_3D_freqs_wavenumber_stem",
            marks=pytest.mark.xfail(
                reason="There is some issue with the axis data configuration in 3D plot "
                "when using fft and is_2D_view=False"
            ),
        ),
    ],
)
def test_plot_3D(axis1, axis2, view_2D, plot_name):
    """Test plot"""
    Time = DataLinspace(name="time", unit="s", initial=0, final=2, number=1001)
    Angle = DataLinspace(name="angle", unit="rad", initial=0, final=2 * pi, number=2001)
    angle, time = meshgrid(Angle.get_values(), Time.get_values())

    # wave parameters
    f = 1
    omega = 2 * pi * f  # angular frequency (rad/s)
    k = 1.0  # angular wavenumber (rad⁻¹)
    phi = 0.0  # phase offset

    field = 3 * sin(omega * time + 1 * angle) + cos(2 * omega * time + 5 * angle)
    Field = DataTime(name="Example field", symbol="Z", axes=[Time, Angle], values=field)

    Field.plot_3D_Data(
        axis1,
        axis2,
        is_2D_view=view_2D,
        is_show_fig=False,
        save_path=join(save_validation_path, f"{plot_name}.png"),
    )


def test_normalization():
    Time = DataLinspace(name="time", unit="s", initial=0, final=10, number=1001)
    time = Time.get_values()
    Time.normalizations = {"rpm": Norm_affine(slope=5, offset=2)}
    Angle = DataLinspace(name="angle", unit="rad", initial=0, final=2 * pi, number=2001)
    angle, time = meshgrid(Angle.get_values(), Time.get_values())
    field = time + angle
    Field = DataTime(name="Example field", symbol="Z", axes=[Time, Angle], values=field)

    Field.plot_2D_Data(
        "time->rpm",
        is_show_fig=False,
        save_path=join(save_validation_path, "plot_norm.png"),
    )
    Field.plot_3D_Data(
        "time->rpm",
        "angle{°}",
        is_2D_view=True,
        is_show_fig=False,
        save_path=join(save_validation_path, "plot_norm_3D.png"),
    )


def test_strings():
    Modes = Data1D(
        name="modes",
        unit="",
        values=["(0,0)", "(1,0)", "(2,0)", "(3,0)", "(4,0)"],
        is_components=True,
        is_overlay=False,
    )
    field = linspace(1, 5, 5)
    Field = DataTime(name="Example field", symbol="Z", axes=[Modes], values=field)

    Field.plot_2D_Data(
        "modes",
        type_plot="bargraph",
        is_show_fig=False,
        save_path=join(save_validation_path, "plot_str.png"),
    )

    Freqs = DataLinspace(
        name="freqs",
        unit="Hz",
        initial=0,
        final=1000,
        number=11,
    )
    Modes.is_overlay = True
    field_2d = zeros((11, 5))
    for i in range(11):
        field_2d[i, :] = i * linspace(1, 5, 5)
    Field_2d = DataTime(
        name="Example field", symbol="Z", axes=[Freqs, Modes], values=field_2d
    )

    Field_2d.plot_2D_Data(
        "freqs",
        "modes",
        is_show_fig=False,
        save_path=join(save_validation_path, "plot_str_2d.png"),
    )

    Field_2d.plot_3D_Data(
        "freqs",
        "modes",
        is_show_fig=False,
        save_path=join(save_validation_path, "plot_str_3d.png"),
    )


if __name__ == "__main__":
    test_normalization()
    test_strings()
