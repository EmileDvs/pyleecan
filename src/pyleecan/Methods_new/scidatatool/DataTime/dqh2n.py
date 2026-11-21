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










def dqh2n(self, n: int, is_n_rms: bool = False, phase_dir: int | None = None) -> DataTime:
    """dqh to n phase coordinate transformation of DataTime object

    Parameters
    ----------
    self : DataTime
        data object containing values over time in dqh frame
    n: int
        number of phases
    is_n_rms : boolean
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_n : DataTime
        data object containing values over time and phase axes
    """


    from ....Functions_new.SciDataTool.dqh_transformation import dqh2n as dqh2n_fct

    if "angle_elec" not in self.axes[0].normalizations:
        raise Exception("Time axis should contain angle_elec normalization")

    # Get values for one time period converted in electrical angle and for all phases
    angle_elec = self.axes[0].get_values(
        normalization="angle_elec", is_oneperiod=True
    )
    data_dqh_val = self.get_along("time[oneperiod]", "phase", is_squeeze=False)[
        self.symbol
    ]

    # Convert values to dqh frame
    data_n_val = dqh2n_fct(data_dqh_val, angle_elec, n, is_n_rms, phase_dir)

    # Get time axis on one period
    per_t, is_aper_t = self.axes[0].get_periodicity()
    per_t = int(per_t / 2) if is_aper_t else per_t
    Time = self.axes[0].get_axis_periodic(per_t, is_aper=False)

    # Create DQH axis
    Phase = Data1D(
        name="phase",
        unit="",
        values=np.array(gen_name(n)),
        is_components=True,
    )

    # Get normalizations
    normalizations: dict[str, Normalization] = dict()
    if self.normalizations is not None and len(self.normalizations) > 0:
        for key, val in self.normalizations.items():
            normalizations[key] = val.copy()

    # Create DataTime object in dqh frame
    data_n = DataTime(
        name=self.name.replace(" in DQH frame", ""),
        unit=self.unit,
        symbol=self.symbol,
        values=data_n_val,
        axes=[Time, Phase],
        normalizations=normalizations,
        is_real=self.is_real,
    )

    return data_n


















