from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_time import DataTime


def dqh2n(self, n: int, is_n_rms: bool = False, phase_dir: int | None = None) -> DataTime:
    """dqh to n phase coordinate transformation of the time data

    Parameters
    ----------
    self : DataDual
        A DataDual object
    n : int
        number of phases
    is_n_rms : bool
        True to return n currents in rms value, False to return peak values (Pyleecan convention)
    phase_dir : int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_n : DataTime
        data object containing values over time in n phase frame
    """
    from ....Classes_new.scidatatool.data_time import DataTime

    data_time = DataTime(
        name=self.name,
        unit=self.unit,
        symbol=self.symbol,
        axes=self.axes_dt,
        values=self.values_dt,
        normalizations=self.normalizations,
        is_real=self.is_real,
    )
    return data_time.dqh2n(n=n, is_n_rms=is_n_rms, phase_dir=phase_dir)
