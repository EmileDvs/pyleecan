import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_dual import DataDual
from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Classes_new.scidatatool.data_nd import DataND
from ....Classes_new.scidatatool.data_time import DataTime
from ....Functions_new.Winding.gen_phase_list import gen_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.normalization import Normalization


def n2dqh(self, is_dqh_rms: bool = True, phase_dir: int | None = None) -> DataTime:
    """n phases to dqh equivalent coordinate transformation of DataTime object

    Parameters
    ----------
    self : DataTime
        data object containing values over time and phase axes
    is_dqh_rms : boolean
        True to return dq currents in rms value (Pyleecan convention), False to return peak values
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_dqh : DataTime
        data object transformed in dqh frame

    """

    from ....Functions_new.SciDataTool.dqh_transformation import get_phase_dir_DataTime, n2dqh

    if phase_dir is None:
        # Check if input data object is compliant with dqh transformation
        # and get phase_dir from data object
        phase_dir = get_phase_dir_DataTime(self)

    if "angle_elec" not in self.axes[0].normalizations:
        raise Exception("Time axis should contain angle_elec normalization")

    # Get values for one time period converted in electrical angle and for all phases
    angle_elec = self.axes[0].get_values(
        normalization="angle_elec", is_oneperiod=True
    )
    data_n_val = self.get_along("time[oneperiod]", "phase", is_squeeze=False)[
        self.symbol
    ]

    # Convert values to dqh frame
    data_dqh_val = n2dqh(data_n_val, angle_elec, is_dqh_rms, phase_dir)

    # Get time axis on one period
    per_t, is_aper_t = self.axes[0].get_periodicity()
    per_t = int(per_t / 2) if is_aper_t else per_t
    Time = self.axes[0].get_axis_periodic(per_t, is_aper=False)

    # Create DQH axis
    axis_dq = Data1D(
        name="phase",
        unit="",
        values=["direct", "quadrature", "homopolar"],
        is_components=True,
    )

    # Get normalizations
    normalizations: dict[str, Normalization] = dict()
    if self.normalizations is not None and len(self.normalizations) > 0:
        for key, val in self.normalizations.items():
            normalizations[key] = val.copy()

    # Create DataTime object in dqh frame
    data_dqh = DataTime(
        name=self.name + " in DQH frame",
        unit=self.unit,
        symbol=self.symbol,
        values=data_dqh_val,
        axes=[Time, axis_dq],
        normalizations=normalizations,
        is_real=self.is_real,
    )

    return data_dqh


























