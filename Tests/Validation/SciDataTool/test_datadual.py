import numpy as np
import pytest
from numpy.testing import assert_array_almost_equal

from pyleecan.Classes.Data1D import Data1D
from pyleecan.Classes.DataDual import DataDual
from pyleecan.Classes.DataFreq import DataFreq
from pyleecan.Classes.DataLinspace import DataLinspace
from pyleecan.Classes.DataTime import DataTime


@pytest.mark.validation
def test_datadual():
    f = 50
    time = np.linspace(0, 1 / f, 10, endpoint=False)
    Time = DataLinspace(
        name="time",
        unit="s",
        initial=0,
        final=1 / f,
        number=10,
        include_endpoint=False,
    )
    field = 3 * np.cos(2 * np.pi * f * time + 3 * np.pi / 4)
    Field = DataTime(
        name="field",
        symbol="X",
        axes=[Time],
        values=field,
        unit="m",
    )

    freqs = np.array([50])
    Freqs = Data1D(
        name="freqs",
        unit="Hz",
        values=freqs,
    )
    field_ft = np.array([3 * np.cos(3 * np.pi / 4) * (1 - 1j)])
    Field_ft = DataFreq(
        name="field",
        symbol="X",
        axes=[Freqs],
        values=field_ft,
        unit="m",
    )

    Field_dual = DataDual(
        name="field",
        symbol="X",
        axes_dt=[Time],
        values_dt=field,
        axes_df=[Freqs],
        values_df=field_ft,
        unit="m",
    )

    result = Field_dual.get_along("time")
    assert_array_almost_equal(result["X"], field)
    assert_array_almost_equal(result["time"], time)

    result = Field_dual.get_along("freqs")
    assert_array_almost_equal(result["X"], field_ft)
    assert_array_almost_equal(result["freqs"], freqs)

    result = Field_dual.get_magnitude_along("freqs")
    assert_array_almost_equal(result["X"], np.array([3]))

    Field_dual.plot_2D_Data("time")
    Field_dual.plot_2D_Data("freqs")

    # test to_datadual
    Field_dual_1 = Field.to_datadual(datafreq=Field_ft)
    Field_dual_2 = Field_ft.to_datadual(datatime=Field)

    assert_array_almost_equal(Field_dual_1.values_dt, Field.values)
    assert_array_almost_equal(Field_dual_1.values_df, Field_ft.values)
    assert_array_almost_equal(Field_dual_2.values_df, Field_ft.values)
    assert_array_almost_equal(Field_dual_2.values_dt, Field.values)

    Field_dual_1.plot_2D_Data("time")
    Field_dual_1.plot_2D_Data("freqs")
    Field_dual_2.plot_2D_Data("time")
    Field_dual_2.plot_2D_Data("freqs")


if __name__ == "__main__":
    test_datadual()
