"""Legacy bugs of the Functions modules fixed by the functions generator
(FUNCTION_LEGACY_FIXES, Step 15): the cases that raised now run."""

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pytest  # noqa: E402

from pyleecan.Functions_new.SciDataTool.Plot.plot_2d import plot_2D  # noqa: E402
from pyleecan.Functions_new.SciDataTool.Plot.plot_3d import plot_3D  # noqa: E402
from pyleecan.Functions_new.SciDataTool.Plot.plot_4d import plot_4D  # noqa: E402
from pyleecan.Generator.ClassGenerator.New.legacy_fixes import (  # noqa: E402
    FUNCTION_LEGACY_FIXES,
)

X = np.linspace(1, 10, 10)


@pytest.fixture(autouse=True)
def close_figures():
    yield
    plt.close("all")


def test_plot_2d_with_figure_only():
    fig = plt.figure()
    fig.add_subplot()
    plot_2D(X, [X**2], fig=fig, is_show_fig=False)
    assert len(fig.axes[0].lines) == 1


def test_plot_2d_with_axes_only(tmp_path):
    _, ax = plt.subplots()
    plot_2D(X, [X**2], ax=ax, is_show_fig=False, save_path=str(tmp_path / "a.png"))
    assert (tmp_path / "a.png").is_file()


def test_plot_3d_stem_with_log_z():
    # matplotlib.cm.get_cmap (stem) and Axes3D.zscale (is_logscale_z) raised
    plot_3D(X, X, X, type_plot="stem", is_logscale_z=True, is_show_fig=False)


def test_plot_3d_log_scale_x_y():
    Xg, Yg = np.meshgrid(X, X)
    fig, ax = plt.subplots()
    plot_3D(
        Xg, Yg, Xg * Yg, type_plot="pcolormesh", fig=fig, ax=ax,
        is_logscale_x=True, is_logscale_y=True, is_show_fig=False,
    )
    assert ax.get_xscale() == "log" and ax.get_yscale() == "log"


def test_plot_4d_log_scale_x():
    fig, ax = plt.subplots()
    plot_4D(
        X, X, X, Sdata=X, type_plot="scatter", fig=fig, ax=ax,
        is_logscale_x=True, is_show_fig=False,
    )
    assert ax.get_xscale() == "log"


def test_fixes_target_existing_legacy_modules():
    from pyleecan.definitions import MAIN_DIR
    from pathlib import Path

    for module in FUNCTION_LEGACY_FIXES:
        assert (Path(MAIN_DIR) / "Functions" / module).is_file()
