from logging import getLogger
from typing import Dict, List

import numpy as np


def matrice_D(t: np.ndarray, f: np.ndarray) -> np.ndarray:
    """
    Construct discrete Fourier transform matrix
    """
    return np.exp(-1j * np.outer(f * 2 * np.pi, t))


def nudftn(a: np.ndarray, axes_dict: Dict[int, List[np.ndarray]]) -> np.ndarray:
    """
    Compute the non uniform discrete Fourier Transform

    Parameter
    ---------

    a: Input data
    axes_dict: Axes to perform dft with corresponding space and freqsampling

    Returns
    res: DFT result
    """
    # Copy data
    res = a.copy()

    axes_fft = []
    # Iterate on each axe to compute 1D DFT
    for idx_axe, axes in axes_dict.items():
        if idx_axe not in axes_fft:  # Check if DFT has to be performed
            # Extract space sampling and frequency sampling
            s, f = axes

            # Check aliasing with criteria frequency < 1/2*mean(spacestep)
            # Other criteria may be used with min instead of mean : max(f)>(1/(2*min(space)))
            space = s[1:] - s[:-1]
            if np.nanmax(f) > (1 / (2 * np.mean(space))):
                # Display warning
                print(
                    f"The maximum frequency ({np.nanmax(f)}) is greater than the 1/(2*mean of each timestep) ({1 / (2 * np.mean(space))}), aliasing may occur."
                )

            # TODO criteria to have only positive freq or approximatively 50% of negative frequencies

            # Construct DFT matrix
            D = matrice_D(s, f)

            # Operate the matrix multiplication and move axis to keep the good shaê
            res = np.tensordot(D, res, ((1,), (idx_axe)))
            res = np.moveaxis(res, 0, idx_axe)

            # Normalize by the number of frequencies
            res /= len(s)

            # Check if every frequency is >=0 (rfft equivalent)
            if np.all(f >= 0):
                idx = np.where(f != 0)
                slice_list = tuple(
                    slice(None) if i != idx_axe else idx[0] for i in range(res.ndim)
                )
                res[slice_list] *= 2

    return res


def matrice_E(t: np.ndarray, f: np.ndarray) -> np.ndarray:
    """Construct inverse discrete Fourier transform matrix"""

    return np.exp(1j * np.outer(t, f * 2 * np.pi))


def inudftn(a: np.ndarray, axes_dict: Dict[int, List[np.ndarray]]) -> np.ndarray:
    """
    Compute the non uniform discrete Fourier Transform

    Parameter
    ---------

    a: Input data
    axes_dict: Axes to perform dft with corresponding space and freqsampling

    Returns
    res: DFT result
    """

    res = a.copy()

    # TODO check axes to perform ifft if space and freq sampling are matching
    # /!\ Normalization is done in inudft and not in fft, look in SciDataTool to find the
    # right normalization
    axes_fft = []

    # Iterate on each axe to compute 1D DFT
    for idx_axe, axes in axes_dict.items():
        if idx_axe not in axes_fft:  # Check if DFT has to be performed
            # Extract space sampling and frequency sampling
            s, f = axes

            # Construct DFT matrix
            E = matrice_E(s, f)

            # Operate the matrix multiplication and move axis to keep the good shape
            res = np.tensordot(E, res, ((1,), (idx_axe)))
            res = np.moveaxis(res, 0, idx_axe)

    return res


def is_uniform(vect_a, rtol=1e-05, atol=1e-8):
    """
    Tests if the array vect_a is uniform
    Parameters
    ----------
    vect_a: array
        Time or space vector
    rtol: float
        Relative tolerance parameter
    atol: float
        Absolut tolerance parameter
    Returns
    -------
    y: boolean
    boolean True if absolute(a - b) <= (atol + rtol * absolute(b))
    """

    assert type(vect_a) == type(np.ndarray(shape=())), TypeError(
        "Time or space vector given must be a ndarray"
    )
    n = len(vect_a)

    minimum = np.nanmin(vect_a)
    maximum = np.nanmax(vect_a)

    y_target = np.linspace(minimum, maximum, n)

    if 0 not in y_target:
        return False

    y = np.allclose(
        vect_a,
        y_target,
        rtol=rtol,
        atol=atol,
        equal_nan=False,
    )

    return y
