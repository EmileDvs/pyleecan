# File generated according to Generator/ClassesRef/Import/ImportGenPWM.csv
# WARNING! All changes made in this file will be lost!
"""Method code available at https://github.com/Eomys/pyleecan/tree/master/pyleecan/Methods/Import/ImportGenPWM"""

from os import linesep
from sys import getsizeof

import matplotlib.pyplot as plt
import numpy as np
from pyleecan.Classes.ImportMatrix import ImportMatrix
from pyleecan.Classes._check import check_var

from pyleecan.Functions.get_logger import get_logger
from pyleecan.Functions.load import load_init_dict
from pyleecan.Functions.save import save
from scipy import integrate, signal


class ImportGenPWM(ImportMatrix):
    """To generate a PWM voltage matrix"""

    VERSION = 1

    # cf Methods.Import.ImportGenPWM.comp_carrier
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

    # cf Methods.Import.ImportGenPWM.comp_voltage
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

    # cf Methods.Import.ImportGenPWM.get_data
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

    # cf Methods.Import.ImportGenPWM.get_modulation_index
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

    # generic save method is available in all object
    save = save
    # get_logger method is available in all object
    get_logger = get_logger

    def __init__(
        self,
        fs=96000,
        duration=10,
        f=50,
        fmax=0,
        fmode=0,
        fswimode=0,
        fswi=1000,
        fswi_max=3000,
        typePWM=8,
        Vdc1=2,
        U0=None,
        type_carrier=0,
        var_amp=20,
        qs=3,
        is_star=True,
        phase_dir=-1,
        current_dir=-1,
        Phi0=0,
        is_transpose=False,
        init_dict=None,
        init_str=None,
    ):
        """Constructor of the class. Can be use in three ways :
        - __init__ (arg1 = 1, arg3 = 5) every parameters have name and default values
            for pyleecan type, -1 will call the default constructor
        - __init__ (init_dict = d) d must be a dictionary with property names as keys
        - __init__ (init_str = s) s must be a string
        s is the file path to load

        ndarray or list can be given for Vector and Matrix
        object or dict can be given for pyleecan Object"""

        if init_str is not None:  # Load from a file
            init_dict = load_init_dict(init_str)[1]
        if init_dict is not None:  # Initialisation by dict
            assert type(init_dict) is dict
            # Overwrite default value with init_dict content
            if "fs" in list(init_dict.keys()):
                fs = init_dict["fs"]
            if "duration" in list(init_dict.keys()):
                duration = init_dict["duration"]
            if "f" in list(init_dict.keys()):
                f = init_dict["f"]
            if "fmax" in list(init_dict.keys()):
                fmax = init_dict["fmax"]
            if "fmode" in list(init_dict.keys()):
                fmode = init_dict["fmode"]
            if "fswimode" in list(init_dict.keys()):
                fswimode = init_dict["fswimode"]
            if "fswi" in list(init_dict.keys()):
                fswi = init_dict["fswi"]
            if "fswi_max" in list(init_dict.keys()):
                fswi_max = init_dict["fswi_max"]
            if "typePWM" in list(init_dict.keys()):
                typePWM = init_dict["typePWM"]
            if "Vdc1" in list(init_dict.keys()):
                Vdc1 = init_dict["Vdc1"]
            if "U0" in list(init_dict.keys()):
                U0 = init_dict["U0"]
            if "type_carrier" in list(init_dict.keys()):
                type_carrier = init_dict["type_carrier"]
            if "var_amp" in list(init_dict.keys()):
                var_amp = init_dict["var_amp"]
            if "qs" in list(init_dict.keys()):
                qs = init_dict["qs"]
            if "is_star" in list(init_dict.keys()):
                is_star = init_dict["is_star"]
            if "phase_dir" in list(init_dict.keys()):
                phase_dir = init_dict["phase_dir"]
            if "current_dir" in list(init_dict.keys()):
                current_dir = init_dict["current_dir"]
            if "Phi0" in list(init_dict.keys()):
                Phi0 = init_dict["Phi0"]
            if "is_transpose" in list(init_dict.keys()):
                is_transpose = init_dict["is_transpose"]
        # Set the properties (value check and convertion are done in setter)
        self.fs = fs
        self.duration = duration
        self.f = f
        self.fmax = fmax
        self.fmode = fmode
        self.fswimode = fswimode
        self.fswi = fswi
        self.fswi_max = fswi_max
        self.typePWM = typePWM
        self.Vdc1 = Vdc1
        self.U0 = U0
        self.type_carrier = type_carrier
        self.var_amp = var_amp
        self.qs = qs
        self.is_star = is_star
        self.phase_dir = phase_dir
        self.current_dir = current_dir
        self.Phi0 = Phi0
        # Call ImportMatrix init
        super(ImportGenPWM, self).__init__(is_transpose=is_transpose)
        # The class is frozen (in ImportMatrix init), for now it's impossible to
        # add new properties

    def __str__(self):
        """Convert this object in a readeable string (for print)"""

        ImportGenPWM_str = ""
        # Get the properties inherited from ImportMatrix
        ImportGenPWM_str += super(ImportGenPWM, self).__str__()
        ImportGenPWM_str += "fs = " + str(self.fs) + linesep
        ImportGenPWM_str += "duration = " + str(self.duration) + linesep
        ImportGenPWM_str += "f = " + str(self.f) + linesep
        ImportGenPWM_str += "fmax = " + str(self.fmax) + linesep
        ImportGenPWM_str += "fmode = " + str(self.fmode) + linesep
        ImportGenPWM_str += "fswimode = " + str(self.fswimode) + linesep
        ImportGenPWM_str += "fswi = " + str(self.fswi) + linesep
        ImportGenPWM_str += "fswi_max = " + str(self.fswi_max) + linesep
        ImportGenPWM_str += "typePWM = " + str(self.typePWM) + linesep
        ImportGenPWM_str += "Vdc1 = " + str(self.Vdc1) + linesep
        ImportGenPWM_str += "U0 = " + str(self.U0) + linesep
        ImportGenPWM_str += "type_carrier = " + str(self.type_carrier) + linesep
        ImportGenPWM_str += "var_amp = " + str(self.var_amp) + linesep
        ImportGenPWM_str += "qs = " + str(self.qs) + linesep
        ImportGenPWM_str += "is_star = " + str(self.is_star) + linesep
        ImportGenPWM_str += "phase_dir = " + str(self.phase_dir) + linesep
        ImportGenPWM_str += "current_dir = " + str(self.current_dir) + linesep
        ImportGenPWM_str += "Phi0 = " + str(self.Phi0) + linesep
        return ImportGenPWM_str

    def __eq__(self, other):
        """Compare two objects (skip parent)"""

        if type(other) != type(self):
            return False

        # Check the properties inherited from ImportMatrix
        if not super(ImportGenPWM, self).__eq__(other):
            return False
        if other.fs != self.fs:
            return False
        if other.duration != self.duration:
            return False
        if other.f != self.f:
            return False
        if other.fmax != self.fmax:
            return False
        if other.fmode != self.fmode:
            return False
        if other.fswimode != self.fswimode:
            return False
        if other.fswi != self.fswi:
            return False
        if other.fswi_max != self.fswi_max:
            return False
        if other.typePWM != self.typePWM:
            return False
        if other.Vdc1 != self.Vdc1:
            return False
        if other.U0 != self.U0:
            return False
        if other.type_carrier != self.type_carrier:
            return False
        if other.var_amp != self.var_amp:
            return False
        if other.qs != self.qs:
            return False
        if other.is_star != self.is_star:
            return False
        if other.phase_dir != self.phase_dir:
            return False
        if other.current_dir != self.current_dir:
            return False
        if other.Phi0 != self.Phi0:
            return False
        return True

    def compare(self, other, name="self", ignore_list=None, is_add_value=False):
        """Compare two objects and return list of differences"""

        if ignore_list is None:
            ignore_list = list()
        if type(other) != type(self):
            return ["type(" + name + ")"]
        diff_list = list()

        # Check the properties inherited from ImportMatrix
        diff_list.extend(
            super(ImportGenPWM, self).compare(
                other, name=name, ignore_list=ignore_list, is_add_value=is_add_value
            )
        )
        if (
            other._fs is not None
            and self._fs is not None
            and np.isnan(other._fs)
            and np.isnan(self._fs)
        ):
            pass
        elif other._fs != self._fs:
            if is_add_value:
                val_str = " (self=" + str(self._fs) + ", other=" + str(other._fs) + ")"
                diff_list.append(name + ".fs" + val_str)
            else:
                diff_list.append(name + ".fs")
        if (
            other._duration is not None
            and self._duration is not None
            and np.isnan(other._duration)
            and np.isnan(self._duration)
        ):
            pass
        elif other._duration != self._duration:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._duration)
                    + ", other="
                    + str(other._duration)
                    + ")"
                )
                diff_list.append(name + ".duration" + val_str)
            else:
                diff_list.append(name + ".duration")
        if (
            other._f is not None
            and self._f is not None
            and np.isnan(other._f)
            and np.isnan(self._f)
        ):
            pass
        elif other._f != self._f:
            if is_add_value:
                val_str = " (self=" + str(self._f) + ", other=" + str(other._f) + ")"
                diff_list.append(name + ".f" + val_str)
            else:
                diff_list.append(name + ".f")
        if (
            other._fmax is not None
            and self._fmax is not None
            and np.isnan(other._fmax)
            and np.isnan(self._fmax)
        ):
            pass
        elif other._fmax != self._fmax:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._fmax) + ", other=" + str(other._fmax) + ")"
                )
                diff_list.append(name + ".fmax" + val_str)
            else:
                diff_list.append(name + ".fmax")
        if other._fmode != self._fmode:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._fmode) + ", other=" + str(other._fmode) + ")"
                )
                diff_list.append(name + ".fmode" + val_str)
            else:
                diff_list.append(name + ".fmode")
        if other._fswimode != self._fswimode:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._fswimode)
                    + ", other="
                    + str(other._fswimode)
                    + ")"
                )
                diff_list.append(name + ".fswimode" + val_str)
            else:
                diff_list.append(name + ".fswimode")
        if (
            other._fswi is not None
            and self._fswi is not None
            and np.isnan(other._fswi)
            and np.isnan(self._fswi)
        ):
            pass
        elif other._fswi != self._fswi:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._fswi) + ", other=" + str(other._fswi) + ")"
                )
                diff_list.append(name + ".fswi" + val_str)
            else:
                diff_list.append(name + ".fswi")
        if (
            other._fswi_max is not None
            and self._fswi_max is not None
            and np.isnan(other._fswi_max)
            and np.isnan(self._fswi_max)
        ):
            pass
        elif other._fswi_max != self._fswi_max:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._fswi_max)
                    + ", other="
                    + str(other._fswi_max)
                    + ")"
                )
                diff_list.append(name + ".fswi_max" + val_str)
            else:
                diff_list.append(name + ".fswi_max")
        if other._typePWM != self._typePWM:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._typePWM)
                    + ", other="
                    + str(other._typePWM)
                    + ")"
                )
                diff_list.append(name + ".typePWM" + val_str)
            else:
                diff_list.append(name + ".typePWM")
        if (
            other._Vdc1 is not None
            and self._Vdc1 is not None
            and np.isnan(other._Vdc1)
            and np.isnan(self._Vdc1)
        ):
            pass
        elif other._Vdc1 != self._Vdc1:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Vdc1) + ", other=" + str(other._Vdc1) + ")"
                )
                diff_list.append(name + ".Vdc1" + val_str)
            else:
                diff_list.append(name + ".Vdc1")
        if (
            other._U0 is not None
            and self._U0 is not None
            and np.isnan(other._U0)
            and np.isnan(self._U0)
        ):
            pass
        elif other._U0 != self._U0:
            if is_add_value:
                val_str = " (self=" + str(self._U0) + ", other=" + str(other._U0) + ")"
                diff_list.append(name + ".U0" + val_str)
            else:
                diff_list.append(name + ".U0")
        if other._type_carrier != self._type_carrier:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._type_carrier)
                    + ", other="
                    + str(other._type_carrier)
                    + ")"
                )
                diff_list.append(name + ".type_carrier" + val_str)
            else:
                diff_list.append(name + ".type_carrier")
        if other._var_amp != self._var_amp:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._var_amp)
                    + ", other="
                    + str(other._var_amp)
                    + ")"
                )
                diff_list.append(name + ".var_amp" + val_str)
            else:
                diff_list.append(name + ".var_amp")
        if other._qs != self._qs:
            if is_add_value:
                val_str = " (self=" + str(self._qs) + ", other=" + str(other._qs) + ")"
                diff_list.append(name + ".qs" + val_str)
            else:
                diff_list.append(name + ".qs")
        if other._is_star != self._is_star:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._is_star)
                    + ", other="
                    + str(other._is_star)
                    + ")"
                )
                diff_list.append(name + ".is_star" + val_str)
            else:
                diff_list.append(name + ".is_star")
        if other._phase_dir != self._phase_dir:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._phase_dir)
                    + ", other="
                    + str(other._phase_dir)
                    + ")"
                )
                diff_list.append(name + ".phase_dir" + val_str)
            else:
                diff_list.append(name + ".phase_dir")
        if other._current_dir != self._current_dir:
            if is_add_value:
                val_str = (
                    " (self="
                    + str(self._current_dir)
                    + ", other="
                    + str(other._current_dir)
                    + ")"
                )
                diff_list.append(name + ".current_dir" + val_str)
            else:
                diff_list.append(name + ".current_dir")
        if (
            other._Phi0 is not None
            and self._Phi0 is not None
            and np.isnan(other._Phi0)
            and np.isnan(self._Phi0)
        ):
            pass
        elif other._Phi0 != self._Phi0:
            if is_add_value:
                val_str = (
                    " (self=" + str(self._Phi0) + ", other=" + str(other._Phi0) + ")"
                )
                diff_list.append(name + ".Phi0" + val_str)
            else:
                diff_list.append(name + ".Phi0")
        # Filter ignore differences
        diff_list = list(filter(lambda x: x not in ignore_list, diff_list))
        return diff_list

    def __sizeof__(self):
        """Return the size in memory of the object (including all subobject)"""

        S = 0  # Full size of the object

        # Get size of the properties inherited from ImportMatrix
        S += super(ImportGenPWM, self).__sizeof__()
        S += getsizeof(self.fs)
        S += getsizeof(self.duration)
        S += getsizeof(self.f)
        S += getsizeof(self.fmax)
        S += getsizeof(self.fmode)
        S += getsizeof(self.fswimode)
        S += getsizeof(self.fswi)
        S += getsizeof(self.fswi_max)
        S += getsizeof(self.typePWM)
        S += getsizeof(self.Vdc1)
        S += getsizeof(self.U0)
        S += getsizeof(self.type_carrier)
        S += getsizeof(self.var_amp)
        S += getsizeof(self.qs)
        S += getsizeof(self.is_star)
        S += getsizeof(self.phase_dir)
        S += getsizeof(self.current_dir)
        S += getsizeof(self.Phi0)
        return S

    def as_dict(self, type_handle_ndarray=0, keep_function=False, **kwargs):
        """
        Convert this object in a json serializable dict (can be use in __init__).
        type_handle_ndarray: int
            How to handle ndarray (0: tolist, 1: copy, 2: nothing)
        keep_function : bool
            True to keep the function object, else return str
        Optional keyword input parameter is for internal use only
        and may prevent json serializability.
        """

        # Get the properties inherited from ImportMatrix
        ImportGenPWM_dict = super(ImportGenPWM, self).as_dict(
            type_handle_ndarray=type_handle_ndarray,
            keep_function=keep_function,
            **kwargs
        )
        ImportGenPWM_dict["fs"] = self.fs
        ImportGenPWM_dict["duration"] = self.duration
        ImportGenPWM_dict["f"] = self.f
        ImportGenPWM_dict["fmax"] = self.fmax
        ImportGenPWM_dict["fmode"] = self.fmode
        ImportGenPWM_dict["fswimode"] = self.fswimode
        ImportGenPWM_dict["fswi"] = self.fswi
        ImportGenPWM_dict["fswi_max"] = self.fswi_max
        ImportGenPWM_dict["typePWM"] = self.typePWM
        ImportGenPWM_dict["Vdc1"] = self.Vdc1
        ImportGenPWM_dict["U0"] = self.U0
        ImportGenPWM_dict["type_carrier"] = self.type_carrier
        ImportGenPWM_dict["var_amp"] = self.var_amp
        ImportGenPWM_dict["qs"] = self.qs
        ImportGenPWM_dict["is_star"] = self.is_star
        ImportGenPWM_dict["phase_dir"] = self.phase_dir
        ImportGenPWM_dict["current_dir"] = self.current_dir
        ImportGenPWM_dict["Phi0"] = self.Phi0
        # The class name is added to the dict for deserialisation purpose
        # Overwrite the mother class name
        ImportGenPWM_dict["__class__"] = "ImportGenPWM"
        return ImportGenPWM_dict

    def copy(self):
        """Creates a deepcopy of the object"""

        # Handle deepcopy of all the properties
        fs_val = self.fs
        duration_val = self.duration
        f_val = self.f
        fmax_val = self.fmax
        fmode_val = self.fmode
        fswimode_val = self.fswimode
        fswi_val = self.fswi
        fswi_max_val = self.fswi_max
        typePWM_val = self.typePWM
        Vdc1_val = self.Vdc1
        U0_val = self.U0
        type_carrier_val = self.type_carrier
        var_amp_val = self.var_amp
        qs_val = self.qs
        is_star_val = self.is_star
        phase_dir_val = self.phase_dir
        current_dir_val = self.current_dir
        Phi0_val = self.Phi0
        is_transpose_val = self.is_transpose
        # Creates new object of the same type with the copied properties
        obj_copy = type(self)(
            fs=fs_val,
            duration=duration_val,
            f=f_val,
            fmax=fmax_val,
            fmode=fmode_val,
            fswimode=fswimode_val,
            fswi=fswi_val,
            fswi_max=fswi_max_val,
            typePWM=typePWM_val,
            Vdc1=Vdc1_val,
            U0=U0_val,
            type_carrier=type_carrier_val,
            var_amp=var_amp_val,
            qs=qs_val,
            is_star=is_star_val,
            phase_dir=phase_dir_val,
            current_dir=current_dir_val,
            Phi0=Phi0_val,
            is_transpose=is_transpose_val,
        )
        return obj_copy

    def _set_None(self):
        """Set all the properties to None (except pyleecan object)"""

        self.fs = None
        self.duration = None
        self.f = None
        self.fmax = None
        self.fmode = None
        self.fswimode = None
        self.fswi = None
        self.fswi_max = None
        self.typePWM = None
        self.Vdc1 = None
        self.U0 = None
        self.type_carrier = None
        self.var_amp = None
        self.qs = None
        self.is_star = None
        self.phase_dir = None
        self.current_dir = None
        self.Phi0 = None
        # Set to None the properties inherited from ImportMatrix
        super(ImportGenPWM, self)._set_None()

    def _get_fs(self):
        """getter of fs"""
        return self._fs

    def _set_fs(self, value):
        """setter of fs"""
        check_var("fs", value, "float", Vmin=0)
        self._fs = value

    fs = property(
        fget=_get_fs,
        fset=_set_fs,
        doc="""sample frequency

        :Type: float
        :min: 0
        """,
    )

    def _get_duration(self):
        """getter of duration"""
        return self._duration

    def _set_duration(self, value):
        """setter of duration"""
        check_var("duration", value, "float", Vmin=0)
        self._duration = value

    duration = property(
        fget=_get_duration,
        fset=_set_duration,
        doc="""duration

        :Type: float
        :min: 0
        """,
    )

    def _get_f(self):
        """getter of f"""
        return self._f

    def _set_f(self, value):
        """setter of f"""
        check_var("f", value, "float", Vmin=0)
        self._f = value

    f = property(
        fget=_get_f,
        fset=_set_f,
        doc="""fundamental frequency

        :Type: float
        :min: 0
        """,
    )

    def _get_fmax(self):
        """getter of fmax"""
        return self._fmax

    def _set_fmax(self, value):
        """setter of fmax"""
        check_var("fmax", value, "float", Vmin=0)
        self._fmax = value

    fmax = property(
        fget=_get_fmax,
        fset=_set_fmax,
        doc="""maximal fundamental frequency

        :Type: float
        :min: 0
        """,
    )

    def _get_fmode(self):
        """getter of fmode"""
        return self._fmode

    def _set_fmode(self, value):
        """setter of fmode"""
        check_var("fmode", value, "int", Vmin=0)
        self._fmode = value

    fmode = property(
        fget=_get_fmode,
        fset=_set_fmode,
        doc="""speed mode: 0: Fixed speed, 1: Variable speed

        :Type: int
        :min: 0
        """,
    )

    def _get_fswimode(self):
        """getter of fswimode"""
        return self._fswimode

    def _set_fswimode(self, value):
        """setter of fswimode"""
        check_var("fswimode", value, "int")
        self._fswimode = value

    fswimode = property(
        fget=_get_fswimode,
        fset=_set_fswimode,
        doc="""switch mode: 0:Fixed fswi, 1:Variable fswi

        :Type: int
        """,
    )

    def _get_fswi(self):
        """getter of fswi"""
        return self._fswi

    def _set_fswi(self, value):
        """setter of fswi"""
        check_var("fswi", value, "float")
        self._fswi = value

    fswi = property(
        fget=_get_fswi,
        fset=_set_fswi,
        doc="""switching frequency

        :Type: float
        """,
    )

    def _get_fswi_max(self):
        """getter of fswi_max"""
        return self._fswi_max

    def _set_fswi_max(self, value):
        """setter of fswi_max"""
        check_var("fswi_max", value, "float")
        self._fswi_max = value

    fswi_max = property(
        fget=_get_fswi_max,
        fset=_set_fswi_max,
        doc="""maximal switching frequency

        :Type: float
        """,
    )

    def _get_typePWM(self):
        """getter of typePWM"""
        return self._typePWM

    def _set_typePWM(self, value):
        """setter of typePWM"""
        check_var("typePWM", value, "int")
        self._typePWM = value

    typePWM = property(
        fget=_get_typePWM,
        fset=_set_typePWM,
        doc="""0: GDPWM 1: DPWMMIN 2: DPWMMAX 3: DPWM0 4: DPWM1 5: DPWM2 6: DPWM3 7: SVPWM 8: SPWM

        :Type: int
        """,
    )

    def _get_Vdc1(self):
        """getter of Vdc1"""
        return self._Vdc1

    def _set_Vdc1(self, value):
        """setter of Vdc1"""
        check_var("Vdc1", value, "float")
        self._Vdc1 = value

    Vdc1 = property(
        fget=_get_Vdc1,
        fset=_set_Vdc1,
        doc="""DC BUS voltage

        :Type: float
        """,
    )

    def _get_U0(self):
        """getter of U0"""
        return self._U0

    def _set_U0(self, value):
        """setter of U0"""
        check_var("U0", value, "float")
        self._U0 = value

    U0 = property(
        fget=_get_U0,
        fset=_set_U0,
        doc="""reference voltage amplitude (rms)

        :Type: float
        """,
    )

    def _get_type_carrier(self):
        """getter of type_carrier"""
        return self._type_carrier

    def _set_type_carrier(self, value):
        """setter of type_carrier"""
        check_var("type_carrier", value, "int")
        self._type_carrier = value

    type_carrier = property(
        fget=_get_type_carrier,
        fset=_set_type_carrier,
        doc="""1: forward toothsaw carrier 2: backwards toothsaw carrier 3: toothsaw carrier else: symetrical toothsaw carrier

        :Type: int
        """,
    )

    def _get_var_amp(self):
        """getter of var_amp"""
        return self._var_amp

    def _set_var_amp(self, value):
        """setter of var_amp"""
        check_var("var_amp", value, "int")
        self._var_amp = value

    var_amp = property(
        fget=_get_var_amp,
        fset=_set_var_amp,
        doc="""percentage of variation of carrier amplitude

        :Type: int
        """,
    )

    def _get_qs(self):
        """getter of qs"""
        return self._qs

    def _set_qs(self, value):
        """setter of qs"""
        check_var("qs", value, "int")
        self._qs = value

    qs = property(
        fget=_get_qs,
        fset=_set_qs,
        doc="""number of phase

        :Type: int
        """,
    )

    def _get_is_star(self):
        """getter of is_star"""
        return self._is_star

    def _set_is_star(self, value):
        """setter of is_star"""
        check_var("is_star", value, "bool")
        self._is_star = value

    is_star = property(
        fget=_get_is_star,
        fset=_set_is_star,
        doc="""True if star coupling, False if triangle coupling

        :Type: bool
        """,
    )

    def _get_phase_dir(self):
        """getter of phase_dir"""
        return self._phase_dir

    def _set_phase_dir(self, value):
        """setter of phase_dir"""
        check_var("phase_dir", value, "int", Vmin=-1, Vmax=1)
        self._phase_dir = value

    phase_dir = property(
        fget=_get_phase_dir,
        fset=_set_phase_dir,
        doc="""Rotation direction of the stator phases (phase_dir*(n-1)*pi/qs, default value given by PHASE_DIR_REF)

        :Type: int
        :min: -1
        :max: 1
        """,
    )

    def _get_current_dir(self):
        """getter of current_dir"""
        return self._current_dir

    def _set_current_dir(self, value):
        """setter of current_dir"""
        check_var("current_dir", value, "int", Vmin=-1, Vmax=1)
        self._current_dir = value

    current_dir = property(
        fget=_get_current_dir,
        fset=_set_current_dir,
        doc="""Rotation direction of the stator currents (current_dir*2*pi*felec*time, default value given by CURRENT_DIR_REF)

        :Type: int
        :min: -1
        :max: 1
        """,
    )

    def _get_Phi0(self):
        """getter of Phi0"""
        return self._Phi0

    def _set_Phi0(self, value):
        """setter of Phi0"""
        check_var("Phi0", value, "float")
        self._Phi0 = value

    Phi0 = property(
        fget=_get_Phi0,
        fset=_set_Phi0,
        doc="""reference voltage phase (rad)

        :Type: float
        """,
    )
