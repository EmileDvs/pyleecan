# Experimental dataclass generated from Generator/ClassesRef/Import/ImportGenToothSaw.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

import numpy as np

from .import_matrix import ImportMatrix


@dataclass(eq=False)
class ImportGenToothSaw(ImportMatrix):
    """To generate a toothsaw vector

    Attributes
    ----------
    type_signal : int
        0: Forward toothsaw, 1: Backwards toothsaw, 2: symmetrical toothsaw
        Default: 0; Minimum: 0; Maximum: 2
    f : float
        Frequency of the signal to generate
        Unit: Hz; Default: 100; Minimum: 0
    A : float
        Amplitude of the signal to generate
        Default: 1
    N : int
        Length of the signal to generate
        Default: 1024; Minimum: 0
    Tf : float
        End time of the signal generation
        Unit: s; Default: 1; Minimum: 0
    Dt : float
        Time offset
        Unit: s; Default: 0
    """

    type_signal: int = 0
    """0: Forward toothsaw, 1: Backwards toothsaw, 2: symmetrical toothsaw"""
    f: float = 100
    """Frequency of the signal to generate"""
    A: float = 1
    """Amplitude of the signal to generate"""
    N: int = 1024
    """Length of the signal to generate"""
    Tf: float = 1
    """End time of the signal generation"""
    Dt: float = 0
    """Time offset"""

    # Inlined from Methods.Import.ImportGenToothSaw.get_data
    def get_data(self):
        """Generate the toothsaw vector

        Parameters
        ----------
        self : ImportGenToothSaw
            An ImportGenToothSaw object

        Returns
        -------
        vect: ndarray
            The generated toothsaw vector

        """

        time = np.linspace(start=0, stop=self.Tf, num=self.N, endpoint=False)

        T = 1 / self.f
        time = (time + self.Dt) % T

        if self.type_signal == 0:  # forward toothsaw carrier
            Y = (
                np.where(time <= 0.5 * T, 1, 0) * time
                + np.where(time > 0.5 * T, 1, 0) * (time - T)
            ) / (0.5 * T)
        elif self.type_signal == 1:  # backwards toothsaw carrier
            Y = -(
                np.where(time <= 0.5 * T, 1, 0) * time
                + np.where(time > 0.5 * T, 1, 0) * (time - T)
            ) / (0.5 * T)
        elif self.type_signal == 2:  # symmetrical toothsaw carrier
            t1 = T / 4
            t2 = T - t1
            Y = (
                np.where(time <= t1, 1, 0) * time / t1
                + np.where(time > t1, 1, 0)
                * np.where(time < t2, 1, 0)
                * (-time + 0.5 * T)
                / (-t1 + 0.5 * T)
                + np.where(time >= t2, 1, 0) * (time - T) / (T - t2)
            )

        return self.edit_matrix(self.A * Y)
