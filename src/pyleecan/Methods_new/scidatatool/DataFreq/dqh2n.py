import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_freq import DataFreq
from ....Functions_new.SciDataTool.dqh_transformation import abc2n, n2abc
from ....Functions_new.SciDataTool.set_routines import union1d_tol
from ....Functions_new.Winding.gen_phase_list import gen_name
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.normalization import Normalization








def dqh2n(self, n: int, current_dir: int, felec: float, is_n_rms: bool = False, phase_dir: int | None = None) -> DataFreq:
    """dqh to n phase coordinate transformation of DataFreq object

    Parameters
    ----------
    self : DataFreq
        data object containing values over time in dqh frame
    n: int
        number of phases
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]
    is_n_rms : boolean
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_n : DataFreq
        data object containing values over time and phase axes
    """


    # Get values for one time period converted in electrical angle and for all phases
    from ....Functions_new.SciDataTool.dqh_transformation import dqh2n_freq as dqh2n_fct

    result_dqh = self.get_along("freqs", "phase", is_squeeze=False)

    # Convert values to dqh frame
    Z_abc, freqs_abc = dqh2n_fct(
        Z_dqh=result_dqh[self.symbol],
        freqs=result_dqh["freqs"],
        phase_dir=phase_dir,
        current_dir=current_dir,
        felec=felec,
        n=n,
        is_n_rms=is_n_rms,
    )

    # Create frequency axis
    norm_freq: dict[str, Normalization] = dict()
    ax_freq = self.axes[0]
    if ax_freq.normalizations is not None and len(ax_freq.normalizations) > 0:
        for key, val in ax_freq.normalizations.items():
            norm_freq[key] = val.copy()
    Freqs = Data1D(name="freqs", unit="Hz", values=freqs_abc, normalizations=norm_freq)

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

    # Create DataFreq object in dqh frame
    data_n = DataFreq(
        name=self.name.replace(" in DQH frame", ""),
        unit=self.unit,
        symbol=self.symbol,
        values=Z_abc,
        axes=[Freqs, Phase],
        normalizations=normalizations,
        is_real=self.is_real,
    )

    return data_n








