# Experimental pydantic model generated from Generator/ClassesRef/Import/ImportGenToothSaw.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import ClassVar

import numpy as np
from pydantic import Field

from .import_matrix import ImportMatrix


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

    type_signal: int = Field(default=0, ge=0, le=2)
    """0: Forward toothsaw, 1: Backwards toothsaw, 2: symmetrical toothsaw"""
    f: float = Field(default=100, ge=0, json_schema_extra={"unit": "Hz"})
    """Frequency of the signal to generate"""
    A: float = 1
    """Amplitude of the signal to generate"""
    N: int = Field(default=1024, ge=0)
    """Length of the signal to generate"""
    Tf: float = Field(default=1, ge=0, json_schema_extra={"unit": "s"})
    """End time of the signal generation"""
    Dt: float = Field(default=0, json_schema_extra={"unit": "s"})
    """Time offset"""

    _package: ClassVar[str] = "Import"
    """Name of the package of the legacy class module"""

    # Inlined from Methods.Import.ImportGenToothSaw.get_data
    def get_data(self) -> np.ndarray:
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
