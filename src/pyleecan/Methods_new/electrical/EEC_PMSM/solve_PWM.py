from ....classes_common.errors import FieldMissingError
from ....classes_common.logger_context import get_logger
import numpy as np

from ....Classes_new.scidatatool.data_1d import Data1D
from ....Classes_new.scidatatool.data_freq import DataFreq
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.normalization import Normalization
    from ....Classes_new.output.output import Output


def solve_PWM(self, output: Output, is_dqh_freq: bool = False, is_skin_effect_inductance: bool = False) -> DataFreq:
    """Get stator current harmonics due to PWM harmonics
    TODO: validation with transient FEA simulation

    Parameters
    ----------
    self : EEC_PMSM
        an EEC_PMSM object
    output: Output
        An Output object
    is_dqh_freq: bool
        True to consider frequencies in dqh frame (generate resonances in current)
    is_skin_effect_inductance : bool
        True to include skin effect on inductance

    Returns
    ------
    Is_PWM : DataFreq
        Stator current harmonics as DataFreq
    """
    get_logger(self).info("Calculating PWM current harmonics")

    # Get fundamental frequency
    felec = self.OP.get_felec()

    # Get stator winding phase number
    qs = output.simu.machine.stator.winding.qs

    # Get PWM frequencies in abc frame
    if output.elec.Us is None:
        raise FieldMissingError("OutElec.Us is None: the PWM voltage is not computed")
    freqs_n = output.elec.Us.get_axes("freqs")[0].values

    # Get stator voltage harmonics in dqh frame
    Us_PWM = output.elec.get_Us(is_dqh=True, is_harm_only=True, is_freq=True, output=output)
    result = Us_PWM.get_along("freqs", "phase")
    Udqh_val = result[Us_PWM.symbol]
    freqs_dqh = result["freqs"]

    # # Plot Us_n and U_dqh
    # output.elec.Us.plot_2D_Data("freqs", "phase[0]")
    # Us_PWM.plot_2D_Data("freqs=[0,200]", "phase[0]")

    # Filter Udqh_val zeros values
    Udqh_norm = np.linalg.norm(Udqh_val, axis=-1)
    Iamp = Udqh_norm > 1e-6 * Udqh_norm.max()
    freqs_dqh = freqs_dqh[Iamp]
    Udqh_val = Udqh_val[Iamp, :]

    # Init current harmonics matrix
    Idqh_val = np.zeros((freqs_dqh.size, qs), dtype=complex)

    if is_dqh_freq:
        # Take dqh frequency values
        fn_dqh = freqs_dqh
    else:
        # Look for frequency value in n frame for each frequency in dqh frame
        fn_dqh = np.zeros(freqs_dqh.size)
        fn_pos = freqs_dqh + felec
        fn_neg = freqs_dqh - felec
        for ii, (fpos, fneg) in enumerate(zip(fn_pos, fn_neg)):
            fn_ii = None
            jj = 0
            while fn_ii is None and jj < freqs_n.size:
                if (
                    np.abs(fpos - freqs_n[jj]) < 1e-4
                    or np.abs(fneg - freqs_n[jj]) < 1e-4
                ):
                    fn_ii = freqs_n[jj]
                elif (
                    np.abs(fpos + freqs_n[jj]) < 1e-4
                    or np.abs(fneg + freqs_n[jj]) < 1e-4
                ):
                    fn_ii = -freqs_n[jj]
                else:
                    jj += 1
            if fn_ii is None:
                raise Exception("Cannot map dqh frequency back to n frequency")
            else:
                fn_dqh[ii] = fn_ii

        fn_dqh[np.abs(fn_dqh) < felec] = felec

    if self.type_skin_effect:
        CondS = output.simu.machine.stator.winding.conductor
        # Calculate skin effect coefficient on stator resistance
        Xkr_skinS = CondS.comp_skin_effect_resistance(
            freq=fn_dqh, T_op=self.Tsta, T_ref=20
        )
        if is_skin_effect_inductance:
            # Calculate skin effect coefficient on stator inductances
            Xke_skinS = CondS.comp_skin_effect_inductance(
                freq=fn_dqh, T_op=self.Tsta, T_ref=20
            )
        else:
            Xke_skinS = 1
    else:
        Xkr_skinS, Xke_skinS = 1, 1

    # Calculate impedances to solve linear system for all frequencies
    # (from Wenli Liang thesis if is_dqh_freq=True but generate resonances in current harmonics at specific frequencies)
    we = int(is_dqh_freq) * 2 * np.pi * felec
    wh = 2 * np.pi * fn_dqh
    a = self.R1 * Xkr_skinS + 1j * wh * self.Ld * Xke_skinS
    b = -we * self.Lq * Xke_skinS
    c = we * self.Ld * Xke_skinS
    d = self.R1 * Xkr_skinS + 1j * wh * self.Lq * Xke_skinS
    det = a * d - c * b

    # Calculate current harmonics
    # Calculate Id
    Idqh_val[:, 0] = (d * Udqh_val[:, 0] - b * Udqh_val[:, 1]) / det
    # Calculate Iq
    Idqh_val[:, 1] = (-c * Udqh_val[:, 0] + a * Udqh_val[:, 1]) / det

    # Create frequency axis
    if Us_PWM.axes is None:
        raise FieldMissingError("DataFreq.axes is None: the PWM voltage has no axes")
    Freqs_PWM = Us_PWM.axes[0]

    norm_freq: dict[str, Normalization] = dict()
    if Freqs_PWM.normalizations is not None and len(Freqs_PWM.normalizations) > 0:
        for key, val in Freqs_PWM.normalizations.items():
            norm_freq[key] = val.copy()

    Freqs = Data1D(
        name=Freqs_PWM.name,
        symbol=Freqs_PWM.symbol,
        unit=Freqs_PWM.unit,
        values=freqs_dqh,
        normalizations=norm_freq,
    )

    # Create DataFreq in DQH Frame
    Is_PWM_dqh = DataFreq(
        name="Stator current",
        unit="A",
        symbol="I_s",
        axes=[Freqs, Us_PWM.axes[1].copy()],
        values=Idqh_val,
    )

    # # Plot PWM current in dqh frame over frequency
    # Is_PWM_dqh.plot_2D_Data("freqs=[0,20000]", "phase[]")

    # Convert I_dqh spectrum back to stator frame
    if output.elec.OP is None:
        raise FieldMissingError("OutElec.OP is None: the output has no operating point")
    Is_PWM_n = Is_PWM_dqh.dqh2n(
        n=qs,
        phase_dir=output.elec.phase_dir,
        current_dir=output.elec.current_dir,
        felec=output.elec.OP.felec,
        is_n_rms=False,
    )

    # Reduce current to original voltage frequencies
    Is_PWM_n = Is_PWM_n.get_data_along("freqs=" + str(freqs_n.tolist()), "phase")

    return Is_PWM_n
