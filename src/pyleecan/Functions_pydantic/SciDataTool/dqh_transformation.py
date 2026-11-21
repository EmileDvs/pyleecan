"""Functions merged from Electrical.dqh_transformation, Electrical.dqh_transformation_freq (PLAN.md Step 8)."""

import numpy as np

from ..Winding.gen_phase_list import gen_name
from .set_routines import union1d_tol


def n2dqh(Z_n, angle_elec, is_dqh_rms=True, phase_dir=None):
    """n phases to dqh equivalent coordinate transformation

    Parameters
    ----------
    Z_n : ndarray
        matrix (N x n) of n phases values
    angle_elec : ndarray
        angle of the rotor coordinate system
    is_dqh_rms : boolean
        True to return dq currents in rms value (Pyleecan convention), False to return peak values
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    Z_dqh : ndarray
        transformed matrix (N x 3) of dqh equivalent values
    """

    if phase_dir is None:
        # Get phase_dir from Z_n
        phase_dir = get_phase_dir(Z_n)

    Z_dqh = abc2dqh(n2abc(Z_n, phase_dir), angle_elec)

    if is_dqh_rms:
        # Divide by sqrt(2) to go from (Id_peak, Iq_peak) to (Id_rms, Iq_rms)
        Z_dqh /= np.sqrt(2)

    return Z_dqh


def n2abc(Z_n, phase_dir=None):
    """n phase to 3 phases equivalent coordinate transformation, i.e. Clarke transformation

    Parameters
    ----------
    Z_n : ndarray
        matrix (N x n) of n phase values
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    Z_abc : ndarray
        transformed matrix (N x 3) of 3 phases equivalent values (alpha-beta-gamma)

    """

    n = Z_n.shape[1]

    n_2_abc = comp_Clarke_transform(n, is_inv=False, phase_dir=phase_dir)

    Z_abc = np.matmul(Z_n, n_2_abc)

    return Z_abc


def abc2dqh(Z_abc, angle_elec):
    """alpha-beta-gamma to dqh coordinate transformation

    Parameters
    ----------
    Z_abc : ndarray
        matrix (N x 3) of alpha-beta-gamma - reference frame values
    angle_elec : ndarray
        angle of the rotor coordinate system

    Returns
    -------
    Z_dqh : ndarray
        transformed (dqh) values

    """

    if Z_abc.ndim == 1:
        Z_abc = Z_abc[None, :]

    sin_angle_elec = np.sin(angle_elec)
    cos_angle_elec = np.cos(angle_elec)

    Z_dqh = np.zeros((angle_elec.size, 3))

    # d-axis
    Z_dqh[:, 0] = Z_abc[:, 0] * cos_angle_elec + Z_abc[:, 1] * sin_angle_elec
    # q-axis
    Z_dqh[:, 1] = -Z_abc[:, 0] * sin_angle_elec + Z_abc[:, 1] * cos_angle_elec
    # Homopolar axis
    Z_dqh[:, 2] = Z_abc[:, 2]

    return Z_dqh


def dqh2n(Z_dqh, angle_elec, n, is_n_rms=False, phase_dir=None):
    """dqh to n phase coordinate transformation

    Parameters
    ----------
    Z_dqh : ndarray
        matrix (N x 3) of dqh phase values
    angle_elec : ndarray
        angle of the rotor coordinate system
    n: int
        number of phases
    is_n_rms : boolean
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    Z_n : ndarray
        transformed matrix (N x n) of n phase values
    """

    Z_n = abc2n(dqh2abc(Z_dqh, angle_elec), n, phase_dir)

    if not is_n_rms:
        # Multiply by sqrt(2) to from (I_n_rms) to (I_n_peak)
        Z_n *= np.sqrt(2)

    return Z_n


def abc2n(Z_abc, n=3, phase_dir=None):
    """3 phase equivalent to n phase coordinate transformation, i.e. Clarke transformation

    Parameters
    ----------
    Z_abc : ndarray
        matrix (N x 3) of 3 phase equivalent values in alpha-beta-gamma frame
    n: int
        number of phases
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    Z_n : ndarray
        transformed matrix (N x n) of n phase values

    """

    # Inverse of Clarke transformation matrix
    ab_2_n = comp_Clarke_transform(n, is_inv=True, phase_dir=phase_dir)

    Z_n = np.matmul(Z_abc, ab_2_n)

    return Z_n


def dqh2abc(Z_dqh, angle_elec):
    """dqh to alpha-beta-gamma coordinate transformation

    Parameters
    ----------
    Z_dqh : ndarray
        matrix (N x 3) of dqh - reference frame values
    angle_elec : ndarray
        angle of the rotor coordinate system

    Returns
    -------
    Z_abc : ndarray
        transformed array

    """

    if Z_dqh.ndim == 1:
        Z_dqh = Z_dqh[None, :]

    sin_angle_elec = np.sin(angle_elec)
    cos_angle_elec = np.cos(angle_elec)

    Z_abc = np.zeros((angle_elec.size, 3))

    Z_abc[:, 0] = Z_dqh[:, 0] * cos_angle_elec - Z_dqh[:, 1] * sin_angle_elec
    Z_abc[:, 1] = Z_dqh[:, 0] * sin_angle_elec + Z_dqh[:, 1] * cos_angle_elec
    Z_abc[:, 2] = Z_dqh[:, 2]

    return Z_abc


def comp_Clarke_transform(n, is_inv=False, phase_dir=None):
    """Compute Clarke transformation for given number of phases and rotating direction of phases

    Parameters
    ----------
    n : int
        number of phases
    is_inv: bool
        False to return Clarke transform, True to return inverse of Clarke transform
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce


    Returns
    -------
    mat : ndarray
        Clarke transform matrix of size (n, 3)
    """

    if phase_dir not in [-1, 1]:
        raise Exception("Cannot enforce phase_dir other than +1 or -1")

    # Phasor depending on fundamental field rotation direction
    phasor = np.linspace(0, phase_dir * 2 * np.pi * (n - 1) / n, n)

    # Clarke transformation matrix
    if is_inv:
        mat = np.vstack((np.cos(phasor), -np.sin(phasor), np.ones(n)))
    else:
        mat = 2 / n * np.column_stack((np.cos(phasor), -np.sin(phasor), np.ones(n) / 2))

    return mat


def get_phase_dir_DataTime(data_n):
    """Get the phase rotating direction of input n-phase DataTime object

    Parameters
    ----------
    data_n : DataTime
        data object containing values over time and phase axes

    Returns
    -------
    phase_dir : int
        rotating direction of phases +/-1
    """

    # Extract values from DataTime
    Z_n = data_n.get_along("time[oneperiod]", "phase")[data_n.symbol]

    # Get current_dir
    current_dir = int(np.sign(data_n.axes[0].normalizations["angle_elec"].ref))

    # Get phase direction
    phase_dir = get_phase_dir(Z_n, current_dir)

    return phase_dir


def get_phase_dir(Z_n, current_dir):
    """Get the phase rotating direction of input n-phase quantity by looking at phase of maximum component

    Parameters
    ----------
    Z_n : ndarray
        matrix (N x n) of n phase values
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce

    Returns
    ----------
    phase_dir : int
        rotating direction of phases +/-1
    """

    # Get number of time steps
    N = Z_n.shape[0]

    # Get Fourier transform for all phases
    TF_Zn = np.fft.fft(Z_n, axis=0)[: int(N / 2), :]

    # Calculate phase_dir from FFT components
    phase_dir = get_phase_dir_freq(TF_Zn, current_dir)

    return phase_dir


def n2dqh_freq(Z_n, freqs, phase_dir, current_dir, felec, is_dqh_rms=True):
    """n phases to dqh equivalent coordinate transformation

    Parameters
    ----------
    Z_n : ndarray
        matrix (N x n) of n phases values
    freqs : ndarray
        frequency array in static frame [Hz]
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]
    is_dqh_rms : boolean
        True to return dq currents in rms value (Pyleecan convention), False to return peak values

    Returns
    -------
    Z_dqh : ndarray
        transformed matrix (N x 3) of dqh equivalent values
    freqs_dqh : ndarray
        frequency array in dqh frame [Hz]
    """

    Z_dqh, freqs_dqh = abc2dqh_freq(n2abc(Z_n, phase_dir), freqs, current_dir, felec)

    if is_dqh_rms:
        # Divide by sqrt(2) to go from (Id_peak, Iq_peak) to (Id_rms, Iq_rms)
        Z_dqh /= np.sqrt(2)

    return Z_dqh, freqs_dqh


def abc2dqh_freq(Z_abc, freqs, current_dir, felec):
    """alpha-beta-gamma to dqh coordinate transformation

    Parameters
    ----------
    Z_abc : ndarray
        matrix (N x 3) of phases values in abc static frame
    freqs : ndarray
        frequency array in static frame [Hz]
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]

    Returns
    -------
    Z_dqh : ndarray
        transformed matrix (N x 3) of dqh equivalent values
    freqs_dqh : ndarray
        frequency array in dqh frame [Hz]
    """

    # Create Frequency axes
    from ...Classes_pydantic.scidatatool.data_1d import Data1D
    from ...Classes_pydantic.scidatatool.data_freq import DataFreq

    Freqs = Data1D(name="freqs", unit="Hz", values=freqs)
    Freqs0 = Data1D(name="freqs", unit="Hz", values=np.array([felec]))

    # Build DataFreq for Za and Zb
    df_a = DataFreq(axes=[Freqs], values=Z_abc[:, 0])
    df_b = DataFreq(axes=[Freqs], values=Z_abc[:, 1])

    # Build DataFreq for cos(angle_elec) / sin(angle_elec)
    df_cos = DataFreq(axes=[Freqs0], values=np.array([1]))
    df_sin = DataFreq(axes=[Freqs0], values=np.array([-current_dir * 1j]))
    df_sin_neg = DataFreq(axes=[Freqs0], values=np.array([current_dir * 1j]))

    # Calculate Zd in spectrum domain (Zd = Za*cos + Zb*sin)
    df_d = df_a.conv(df_cos)
    df_d = df_d.sum(df_b.conv(df_sin))

    # Calculate Zq in spectrum domain (Zq = -Za*sin + Zb*cos)
    df_q = df_a.conv(df_sin_neg)
    df_q = df_q.sum(df_b.conv(df_cos))

    # Merge frequencies
    freqs_dqh, Ifdq, Ifh = union1d_tol(df_d.axes[0].values, freqs, return_indices=True)

    # Rebuild dqh values
    Z_dqh = np.zeros((freqs_dqh.size, 3), dtype=complex)
    Z_dqh[Ifdq, 0] = df_d.values
    Z_dqh[Ifdq, 1] = df_q.values
    Z_dqh[Ifh, 2] = Z_abc[:, 2]  # Homopolar axis same as c axis

    # Only return non zero values
    Z_dqh_norm = np.linalg.norm(Z_dqh, axis=1)
    I0 = Z_dqh_norm > 1e-10

    return Z_dqh[I0, :], freqs_dqh[I0]


def dqh2n_freq(Z_dqh, freqs, current_dir, felec, n, phase_dir=None, is_n_rms=False):
    """dqh to n phase coordinate transformation

    Parameters
    ----------
    Z_dqh : ndarray
        matrix (N x 3) of dqh phase values
    freqs : ndarray
        frequency array in dqh frame [Hz]
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]
    n: int
        number of phases
    is_n_rms : boolean
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir: int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    Z_n : ndarray
        transformed matrix (N x n) of n phase values
    freqs_abc : ndarray
        frequency array in static frame [Hz]
    """

    Z_abc, freqs_abc = dqh2abc_freq(Z_dqh, freqs, current_dir, felec)

    Z_n = abc2n(Z_abc, n, phase_dir)

    if not is_n_rms:
        # Multiply by sqrt(2) to from (I_n_rms) to (I_n_peak)
        Z_n *= np.sqrt(2)

    return Z_n, freqs_abc


def dqh2abc_freq(Z_dqh, freqs, current_dir, felec):
    """dqh to alpha-beta-gamma coordinate transformation

    Parameters
    ----------
    Z_dqh : ndarray
        matrix (N x 3) of dqh - reference frame values
    freqs : ndarray
        frequency array in dqh frame [Hz]
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce
    felec: float
        fundamental electrical frequency [Hz]

    Returns
    -------
    Z_abc : ndarray
        transformed array
    freqs_abc : ndarray
        frequency array in static frame [Hz]
    """

    # Create Frequency axes
    from ...Classes_pydantic.scidatatool.data_1d import Data1D
    from ...Classes_pydantic.scidatatool.data_freq import DataFreq

    Freqs = Data1D(name="freqs", unit="Hz", values=freqs)
    Freqs0 = Data1D(name="freqs", unit="Hz", values=np.array([felec]))

    # Build DataFreq for Zd and Zq
    df_d = DataFreq(axes=[Freqs], values=Z_dqh[:, 0])
    df_q = DataFreq(axes=[Freqs], values=Z_dqh[:, 1])

    # Build DataFreq for cos(angle_elec) / sin(angle_elec)
    df_cos = DataFreq(axes=[Freqs0], values=np.array([1]))
    df_sin = DataFreq(axes=[Freqs0], values=np.array([-current_dir * 1j]))
    df_sin_neg = DataFreq(axes=[Freqs0], values=np.array([current_dir * 1j]))

    # Calculate Za with convolution (Za = Zd*cos - Zq*sin)
    df_a = df_d.conv(df_cos)
    df_a = df_a.sum(df_q.conv(df_sin_neg))

    # Calculate Zb with convolution (Zb = Zd*sin + Zq*cos)
    df_b = df_d.conv(df_sin)
    df_b = df_b.sum(df_q.conv(df_cos))

    # Merge frequencies
    freqs_abc, Ifab, Ifc = union1d_tol(
        df_a.axes[0].values, freqs, return_indices=True, tol=1e-4, is_abs_tol=False
    )

    # Rebuild abc values
    Z_abc = np.zeros((freqs_abc.size, 3), dtype=complex)
    Z_abc[Ifab, 0] = df_a.values
    Z_abc[Ifab, 1] = df_b.values
    Z_abc[Ifc, 2] = Z_dqh[:, 2]  # c axis same as homopolar axis

    # Only return non zero values
    Z_abc_norm = np.linalg.norm(Z_abc, axis=1)
    I0 = Z_abc_norm > 1e-10

    return Z_abc[I0, :], freqs_abc[I0]


def get_phase_dir_DataFreq(data_n):
    """Get the phase rotating direction of input n-phase DataFreq object

    Parameters
    ----------
    data_n : DataFreq
        data object containing values over time and phase axes

    Returns
    -------
    phase_dir : int
        rotating direction of phases +/-1
    """

    # Extract values from DataFreq
    Z_n = data_n.get_along("freqs", "phase", is_squeeze=False)[data_n.symbol]

    # Get current_dir
    current_dir = int(np.sign(data_n.axes[0].normalizations["angle_elec"].ref))

    # Get phase direction
    phase_dir = get_phase_dir_freq(Z_n, current_dir)

    return phase_dir


def get_phase_dir_freq(Z_n, current_dir):
    """Get the phase rotating direction of input n-phase quantity by looking at phase of maximum component

    Parameters
    ----------
    Z_n : ndarray
        matrix (N x n) of n phase values
    current_dir: int
        direction of current waveform: +/-1 (-1 clockwise) to enforce

    Returns
    ----------
    phase_dir : int
        rotating direction of phases +/-1
    """

    # Get index of maximum component
    Imax = np.argmax(np.linalg.norm(Z_n, axis=-1))

    # Get phase angle for all phases
    angle_Zn_max = np.unwrap(np.angle(Z_n[Imax, :]) - np.angle(Z_n[Imax, 0]))

    # Differentiate phase angle between phases and taking sign
    phase_shift_sign = np.unique(np.sign(np.diff(angle_Zn_max)))

    if phase_shift_sign.size == 1 and int(phase_shift_sign[0]) in [-1, 1]:
        # phase_dir / current_dir has the sign of phase shift angle
        phase_dir = current_dir * int(phase_shift_sign[0])
    else:
        raise Exception("Cannot calculate phase_dir, please put phase_dir as input")

    return phase_dir
