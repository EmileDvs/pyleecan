# Experimental dataclass generated from Generator/ClassesRef/Import/ImportGenPWM.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import matplotlib.pyplot as plt
import numpy as np
from scipy import integrate, signal

from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportGenPWM(ImportMatrix):
    """To generate a PWM voltage matrix

    Attributes
    ----------
    fs : float
        sample frequency
        Unit: Hz; Default: 96000; Minimum: 0
    duration : float
        duration
        Unit: s; Default: 10; Minimum: 0
    f : float
        fundamental frequency
        Unit: Hz; Default: 50; Minimum: 0
    fmax : float
        maximal fundamental frequency
        Unit: Hz; Default: 0; Minimum: 0
    fmode : int
        speed mode: 0: Fixed speed, 1: Variable speed
        Default: 0; Minimum: 0
    fswimode : int
        switch mode: 0:Fixed fswi, 1:Variable fswi
        Default: 0
    fswi : float
        switching frequency
        Unit: Hz; Default: 1000
    fswi_max : float
        maximal switching frequency
        Unit: Hz; Default: 3000
    typePWM : int
        0: GDPWM 1: DPWMMIN 2: DPWMMAX 3: DPWM0 4: DPWM1 5: DPWM2 6: DPWM3 7: SVPWM 8: SPWM
        Default: 8
    Vdc1 : float
        DC BUS voltage
        Unit: V; Default: 2
    U0 : float or None
        reference voltage amplitude (rms)
        Unit: V; Default: None
    type_carrier : int
        1: forward toothsaw carrier 2: backwards toothsaw carrier 3: toothsaw carrier else: symetrical toothsaw carrier
        Default: 0
    var_amp : int
        percentage of variation of carrier amplitude
        Unit: %; Default: 20
    qs : int
        number of phase
        Default: 3
    is_star : bool
        True if star coupling, False if triangle coupling
        Default: True
    phase_dir : int
        Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)
        Default: -1; Minimum: -1; Maximum: 1
    current_dir : int
        Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)
        Default: -1; Minimum: -1; Maximum: 1
    Phi0 : float
        reference voltage phase (rad)
        Default: 0
    """

    fs: float = 96000
    """sample frequency"""
    duration: float = 10
    """duration"""
    f: float = 50
    """fundamental frequency"""
    fmax: float = 0
    """maximal fundamental frequency"""
    fmode: int = 0
    """speed mode: 0: Fixed speed, 1: Variable speed"""
    fswimode: int = 0
    """switch mode: 0:Fixed fswi, 1:Variable fswi"""
    fswi: float = 1000
    """switching frequency"""
    fswi_max: float = 3000
    """maximal switching frequency"""
    typePWM: int = 8
    """0: GDPWM 1: DPWMMIN 2: DPWMMAX 3: DPWM0 4: DPWM1 5: DPWM2 6: DPWM3 7: SVPWM 8: SPWM"""
    Vdc1: float = 2
    """DC BUS voltage"""
    U0: float | None = None
    """reference voltage amplitude (rms)"""
    type_carrier: int = 0
    """1: forward toothsaw carrier 2: backwards toothsaw carrier 3: toothsaw carrier else: symetrical toothsaw carrier"""
    var_amp: int = 20
    """percentage of variation of carrier amplitude"""
    qs: int = 3
    """number of phase"""
    is_star: bool = True
    """True if star coupling, False if triangle coupling"""
    phase_dir: int = -1
    """Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)"""
    current_dir: int = -1
    """Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)"""
    Phi0: float = 0
    """reference voltage phase (rad)"""

    # Inlined from Methods.Import.ImportGenPWM.comp_carrier
    def comp_carrier(self, time):
        """Function to compute the carrier

        Parameters
        ----------
        time : array
            Time vector

        Returns
        -------
        Y: ndarray
            carrier

        """

        fswi = self.fswi
        type_carrier = self.type_carrier

        T = 1 / fswi
        time = time % T

        if type_carrier == 1:  # forward toothsaw carrier
            Y = (
                20
                * (
                    np.where(time <= 0.5 * T, time, 0) * time
                    + np.where(time > 0.5 * T, time, 0) * (time - T)
                )
                / (0.5 * T)
            )
        elif type_carrier == 2:  # backwards toothsaw carrier
            Y = (
                20
                * -(
                    np.where(time <= 0.5 * T, time, 0) * time
                    + np.where(time > 0.5 * T, time, 0) * (time - T)
                )
                / (0.5 * T)
            )
        elif type_carrier == 3:  # toothsaw carrier
            t1 = (1 + type_carrier) * T / 4
            t2 = T - t1
            Y = (
                np.where(time <= t1, 1, 0) * time / t1
                + np.where(time > t1, 1, 0)
                * np.where(time < t2, 1, 0)
                * (-time + 0.5 * T)
                / (-t1 + 0.5 * T)
                + np.where(time >= t2, 1, 0) * (time - T) / (T - t2)
            )
        else:
            wswiT = 2 * np.pi * time * fswi
            Y = signal.sawtooth(wswiT, 0.5)

        return Y

    # Inlined from Methods.Import.ImportGenPWM.comp_voltage
    def comp_voltage(self, Tpwmu, PF_angle=0, is_sin=True, is_norm=True):
        """Generalized DPWM using numerical method according to
        'Impact of Modulation Schemes on DC-Link Capacitor of VSI in HEV Applications'

        Parameters
        ----------
        Tpwmu : ndarray
            time vector
        PF_angle: float
            power factor angle only for GDPWM, default to 0
        is_sin: bool
            True to generate sine wave, False to generate cosine wave
        is_norm: int
            True to normalize signal between -1 and 1

        Returns
        -------
         v_pwm : ndarray
            n-phase PWM voltage waveform
         Vas : ndarray
            modulation waveform
         M_I : float
            modulation index
         carrier : ndarray
            carrier waveform

        """

        freq0 = self.f
        freq0_max = self.fmax
        fmode = self.fmode
        fswimode = self.fswimode
        fswi = self.fswi
        fswi_max = self.fswi_max
        qs = self.qs
        Vdc1 = self.Vdc1
        phase_dir = self.phase_dir
        type_DPWM = self.typePWM
        var_amp = self.var_amp
        current_dir = self.current_dir
        Phi0 = self.Phi0

        # Check inputs
        if type_DPWM != 8:
            if fswimode in [1, 4]:
                raise Exception(
                    "Only Sine PWM supports the variable fundamental frequency"
                )
            if fmode == 1:
                raise Exception(
                    "Only Sine PWM supports the variable fundamental frequency"
                )

        Npsim = len(Tpwmu)
        carrier = np.ones(len(Tpwmu))

        if fmode == 0:  # Fixed speed:
            ws = current_dir * 2 * np.pi * freq0

        elif fmode == 1:  # Variable speed:
            freq0_array = (freq0_max - freq0) / Tpwmu[-1] * Tpwmu + freq0 * np.ones(
                Npsim
            )
            ws = current_dir * np.pi * freq0_array

        if fswimode == 0:  # Fixed fswi:
            if type_DPWM == 8:
                carrier = Vdc1 / 2 * self.comp_carrier(Tpwmu)
            else:
                Th = 1 / fswi

        elif fswimode == 1:  # Variable fswi (ramp):
            wswiT = current_dir * (
                np.pi * (fswi_max - fswi) / Tpwmu[-1] * Tpwmu**2
                + 2 * np.pi * fswi * Tpwmu
            )
            carrier = Vdc1 / 2 * signal.sawtooth(wswiT, 0.5)

        elif fswimode == 2 or fswimode == 3:  # Random fswi & Symmetrical random fswi
            t1 = round(Tpwmu[-1] * 5000000)  # Number of points
            if fswimode == 3:
                num_slice = round((fswi_max + fswi) / 2 * Tpwmu[-1])
                delta_fswi = np.random.randint(
                    fswi, high=fswi_max + 1, size=num_slice * 2, dtype=int
                )
                delta_fswi[1::2] = delta_fswi[0::2] * -1

            else:
                num_slice = round((fswi_max + fswi) / 2 * Tpwmu[-1])
                delta_fswi = np.random.randint(
                    fswi, high=fswi_max + 1, size=num_slice * 2, dtype=int
                )
                delta_fswi[1::2] = delta_fswi[1::2] * -1

            fswi_base = np.array(np.ones(t1))
            S_delta = 1
            delta_t = S_delta / abs(delta_fswi)
            time = sum(delta_t)
            delta_point = delta_t[:-1] / time * t1
            delta_point = np.array(delta_point)
            delta_point = np.append(delta_point, t1 - sum(delta_point))
            fswi = np.concatenate(
                [
                    fswi_base[0 : round(delta_point[ii])] * delta_fswi[ii]
                    for ii in range(len(delta_fswi))
                ]
            )
            if len(fswi) < t1:
                fswi = np.concatenate((fswi, fswi[-1] * np.ones(t1 - len(fswi))))
            else:
                fswi = fswi[:t1]

            Tpwmu_10 = np.linspace(0, (t1 - 1) / 5000000, t1, endpoint=True)
            np.linspace(0, (t1 - 1) / 5000000, t1, endpoint=True)
            carrier = integrate.cumulative_trapezoid(fswi, Tpwmu_10, initial=0)
            Aml_tri = max(carrier)
            carrier = carrier / Aml_tri * Vdc1 - Vdc1 / 2 * np.ones(np.size(Tpwmu_10))
            carrier = signal.resample(carrier, len(Tpwmu))

        elif fswimode == 4:  # Random amplitude carrier wave
            carrier = Vdc1 / 2 * (self.comp_carrier(Tpwmu))
            num_slice = int(fswi * Tpwmu[-1])
            delta_amp = np.random.randint(
                -var_amp, high=var_amp + 1, size=int(num_slice), dtype=int
            ) / 100 + np.ones(int(num_slice))

            amp_base = np.ones(len(Tpwmu))
            S_delta = 1

            delta_t = S_delta / fswi * np.ones(int(num_slice))

            delta_point = np.round(delta_t / Tpwmu[-1], 4) * len(Tpwmu)
            delta_point = np.array(delta_point).astype(int)
            amp = np.concatenate(
                [
                    amp_base[0 : delta_point[ii]] * delta_amp[ii]
                    for ii in range(len(delta_amp))
                ]
            )
            if len(amp) < len(Tpwmu):
                amp = np.concatenate((amp, amp[-1] * np.ones(len(Tpwmu) - len(amp))))
            else:
                amp = amp[: len(Tpwmu)]
            carrier = carrier * amp

        M_I = self.get_modulation_index()

        k = 1  # 2/sqrt(3)#2/sqrt(3) factor to have higher fundamental compared to SPWM
        if phase_dir == -1:
            Phase = [0, -1, 1]
        else:
            Phase = [0, 1, -1]

        amp = k * M_I * (Vdc1 / 2)
        angle0 = ws * Tpwmu + Phi0

        if is_sin:
            Vas = amp * np.sin(angle0 + Phase[0] * 2 * np.pi / 3)
            Vbs = amp * np.sin(angle0 + Phase[1] * 2 * np.pi / 3)
            Vcs = amp * np.sin(angle0 + Phase[2] * 2 * np.pi / 3)

        else:
            Vas = amp * np.cos(angle0 + Phase[0] * 2 * np.pi / 3)
            Vbs = amp * np.cos(angle0 + Phase[1] * 2 * np.pi / 3)
            Vcs = amp * np.cos(angle0 + Phase[2] * 2 * np.pi / 3)

        if type_DPWM == 8:
            v_pwm = np.zeros((qs, Npsim))
            amp_dc = 1 if is_norm else Vdc1 / 2

            v_pwm[0] = np.where(Vas < carrier, -amp_dc, amp_dc)
            v_pwm[1] = np.where(Vbs < carrier, -amp_dc, amp_dc)
            v_pwm[2] = np.where(Vcs < carrier, -amp_dc, amp_dc)
        else:
            V_min = np.amin(
                np.concatenate((Vas[:, None], Vbs[:, None], Vcs[:, None]), axis=1),
                axis=1,
            )
            V_max = np.amax(
                np.concatenate((Vas[:, None], Vbs[:, None], Vcs[:, None]), axis=1),
                axis=1,
            )

            alpha_rad = 0

            if type_DPWM == 0:  # GDPWM
                if PF_angle >= -np.pi / 6 and PF_angle <= np.pi / 6:
                    alpha_rad = PF_angle
                elif PF_angle > np.pi / 6 and PF_angle <= 5 * np.pi / 12:
                    alpha_rad = np.pi / 6
                elif PF_angle >= -5 * np.pi / 12 and PF_angle < -np.pi / 6:
                    alpha_rad = -np.pi / 6
                elif PF_angle > 5 * np.pi / 12 and PF_angle <= np.pi / 2:
                    alpha_rad = np.pi / 3
                elif PF_angle >= -np.pi / 2 and PF_angle < -5 * np.pi / 12:
                    alpha_rad = -np.pi / 3

            elif type_DPWM == 3:  # elif type_waveform==63 #DPWM0
                alpha_rad = -30 * np.pi / 180
            elif type_DPWM == 4:  # elif type_waveform==64 #DPWM1
                alpha_rad = 0
            elif type_DPWM == 5:  # elif type_waveform==65 #DPWM2
                alpha_rad = 30 * np.pi / 180

            angle1 = angle0 - alpha_rad
            if is_sin:
                Vas_g = amp * np.sin(angle1 + Phase[0] * 2 * np.pi / 3)
                Vbs_g = amp * np.sin(angle1 + Phase[1] * 2 * np.pi / 3)
                Vcs_g = amp * np.sin(angle1 + Phase[2] * 2 * np.pi / 3)
            else:
                Vas_g = amp * np.cos(angle1 + Phase[0] * 2 * np.pi / 3)
                Vbs_g = amp * np.cos(angle1 + Phase[1] * 2 * np.pi / 3)
                Vcs_g = amp * np.cos(angle1 + Phase[2] * 2 * np.pi / 3)

            V_offset = np.zeros(Npsim)

            min_abc = np.squeeze(
                np.amin(
                    np.concatenate(
                        (Vas_g[:, None], Vbs_g[:, None], Vcs_g[:, None]), axis=1
                    ),
                    axis=1,
                )
            )
            max_abc = np.squeeze(
                np.amax(
                    np.concatenate(
                        (Vas_g[:, None], Vbs_g[:, None], Vcs_g[:, None]), axis=1
                    ),
                    axis=1,
                )
            )
            i1 = min_abc + max_abc > 0
            i2 = min_abc + max_abc < 0
            V_offset[i1] = Vdc1 / 2 - V_max[i1]
            V_offset[i2] = -Vdc1 / 2 - V_min[i2]

            # type_DPWM {0, 1, 2, 3, 4, 5, 6, 7} # {GDPWM, DPWMMIN, DPWMMAX, DPWM0, DPWM1, DPWM2, DPWM3, SVPWM)
            if type_DPWM == 1:  # type_waveform==61 #DPWMMIN
                V_offset = -V_min - Vdc1 / 2
            elif type_DPWM == 2:  # elif type_waveform==62 #DPWMMAX
                V_offset = -V_max + Vdc1 / 2
            elif type_DPWM == 6:  # elif type_waveform==66 #DPWM3
                min_abc = np.amin(
                    np.concatenate((Vas[:, None], Vbs[:, None], Vcs[:, None]), axis=1),
                    axis=1,
                )
                max_abc = np.amax(
                    np.concatenate((Vas[:, None], Vbs[:, None], Vcs[:, None]), axis=1),
                    axis=1,
                )
                i1 = min_abc + max_abc < 0
                i2 = min_abc + max_abc > 0
                V_offset[i1] = Vdc1 / 2 - V_max[i1]
                V_offset[i2] = -Vdc1 / 2 - V_min[i2]
            elif type_DPWM == 7:  # elif type_waveform==67 #SVPWM
                V_offset = -1 / 2 * (V_max + V_min)

            Van = Vas + V_offset
            Vbn = Vbs + V_offset
            Vcn = Vcs + V_offset

            T1 = Th / 4 - Th / (2 * Vdc1) * Van
            T2 = Th / 4 - Th / (2 * Vdc1) * Vbn
            T3 = Th / 4 - Th / (2 * Vdc1) * Vcn
            n = np.floor(Tpwmu / Th).astype(int)
            v_pwm = Vdc1 / 2 * np.ones((qs, Npsim))
            v_pwm[0, Tpwmu < (T1 + n * Th)] = -Vdc1 / 2
            v_pwm[0, Tpwmu > ((n + 1) * Th - T1)] = -Vdc1 / 2
            v_pwm[1, Tpwmu < (T2 + n * Th)] = -Vdc1 / 2
            v_pwm[1, Tpwmu > ((n + 1) * Th - T2)] = -Vdc1 / 2
            v_pwm[2, Tpwmu < (T3 + n * Th)] = -Vdc1 / 2
            v_pwm[2, Tpwmu > ((n + 1) * Th - T3)] = -Vdc1 / 2

        return v_pwm, Vas, M_I, carrier

    # Inlined from Methods.Import.ImportGenPWM.get_data
    def get_data(self, is_norm=True, is_plot=False, Time=None):
        """Generate the PWM matrix

        Parameters
        ----------
        self : ImportGenPWM
            An ImportGenPWM object
        is_norm : bool
            True to normalize signal

        Returns
        -------
        vpwm : ndarray
            n-phase PWM voltage waveform
        Vas : ndarray
            modulation waveform
        MI : float
            modulation index
        carrier : ndarray
            carrier waveform
        Tpwmu : ndarray
            time vector
        """

        if Time is None:
            # Number of points
            N = int(self.fs * self.duration)
            # Define time vector
            Tpwmu = np.linspace(0, self.duration, N, endpoint=False)
        else:
            Tpwmu = Time.get_values(is_smallestperiod=True)

        # Get PWM voltage values
        v_pwm, Vas, MI, carrier = self.comp_voltage(
            Tpwmu=Tpwmu, PF_angle=0, is_norm=is_norm, is_sin=False
        )

        if is_norm:
            ref = np.zeros(np.size(v_pwm[0])).astype(np.float32)
            PWM1 = np.where(v_pwm[0] < ref, -1, 1)  # .astype(np.float32)
            PWM2 = np.where(v_pwm[1] < ref, -1, 1)  # .astype(np.float32)
            PWM3 = np.where(v_pwm[2] < ref, -1, 1)  # .astype(np.float32)
        else:
            PWM1 = v_pwm[0]
            PWM2 = v_pwm[1]
            PWM3 = v_pwm[2]
        Vpwm = np.column_stack([PWM1, PWM2, PWM3])

        if self.is_star:  # star coupling
            mean = Vpwm.mean(axis=1)
            PWM1 = PWM1 - mean
            PWM2 = PWM2 - mean
            PWM3 = PWM3 - mean
            Vpwm = np.column_stack([PWM1, PWM2, PWM3])

        if is_plot:
            Nt = 10000
            plt.figure()
            plt.plot(Tpwmu[:Nt], carrier[:Nt])
            plt.plot(Tpwmu[:Nt], v_pwm[0, :Nt])
            plt.plot(Tpwmu[:Nt], Vas[:Nt])

            plt.figure()
            plt.plot(Tpwmu[:Nt], carrier[:Nt])
            plt.plot(Tpwmu[:Nt], Vpwm[:Nt, 0])
            plt.plot(Tpwmu[:Nt], Vas[:Nt])
            plt.show()

            plt.figure()
            plt.plot(Tpwmu[:Nt], mean[:Nt])

        return Vpwm, Vas, MI, carrier, Tpwmu

    # Inlined from Methods.Import.ImportGenPWM.get_modulation_index
    def get_modulation_index(self):
        """Function to compute the carrier

        Parameters
        ----------
        self : ImportGenPWM
            an ImportGenPWM object

        Returns
        -------
        M_I: float
            Modulation index

        """

        if self.U0 is None:
            raise Exception("Cannot calculate modulation index if self.U0 is None")

        if self.Vdc1 is None:
            raise Exception("Cannot calculate modulation index if self.Vdc1 is None")

        return 2 * np.sqrt(2) * self.U0 / self.Vdc1
