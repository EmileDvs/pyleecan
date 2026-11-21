import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Functions_new.SciDataTool.dqh_transformation import abc2n, n2abc
from ....Functions_new.SciDataTool.set_routines import union1d_tol
from ....Functions_new.Winding.gen_phase_list import gen_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.normalization import Normalization


def n2dqh(self, current_dir: int, felec: float, is_dqh_rms: bool = True, phase_dir: int | None = None) -> DataFreq:
    """n phases to dqh equivalent coordinate transformation of DataFreq/DataTime object

    Parameters
    ----------
    self : DataFreq/DataTime
        data object containing values over freqs and phase axes
    is_dqh_rms : boolean
        True to return dq currents in rms value (Pyleecan convention), False to return peak values
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]

    Returns
    -------
    data_dqh : DataFreq
        data object transformed in dqh frame

    """

    from ....Functions_new.SciDataTool.dqh_transformation import get_phase_dir_DataFreq, n2dqh_freq as n2dqh_fct

    if phase_dir is None:
        # Check if input data object is compliant with dqh transformation
        # and get phase_dir from data object
        phase_dir = get_phase_dir_DataFreq(self)

    # Get values for one time period converted in electrical angle and for all phases
    result_n = self.get_along("freqs", "phase", is_squeeze=False)

    # Convert values to dqh frame
    Z_dqh, freqs_dqh = n2dqh_fct(
        Z_n=result_n[self.symbol],
        freqs=result_n["freqs"],
        phase_dir=phase_dir,
        current_dir=current_dir,
        felec=felec,
        is_dqh_rms=is_dqh_rms,
    )

    # Create frequency axis
    norm_freq: dict[str, Normalization] = dict()
    ax_freq = self.axes[0]
    if ax_freq.normalizations is not None and len(ax_freq.normalizations) > 0:
        for key, val in ax_freq.normalizations.items():
            norm_freq[key] = val.copy()
    Freqs = Data1D(name="freqs", unit="Hz", values=freqs_dqh, normalizations=norm_freq)

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

    # Create DataFreq object in dqh frame
    data_dqh = DataFreq(
        name=self.name + " in DQH frame",
        unit=self.unit,
        symbol=self.symbol,
        values=Z_dqh,
        axes=[Freqs, axis_dq],
        normalizations=normalizations,
        is_real=self.is_real,
    )

    return data_dqh














