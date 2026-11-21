from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_time import DataTime


def n2dqh(self, is_dqh_rms: bool = True, phase_dir: int | None = None) -> DataTime:
    """n phases to dqh equivalent coordinate transformation of the time data

    Parameters
    ----------
    self : DataDual
        A DataDual object
    is_dqh_rms : bool
        True to return dq currents in rms value (Pyleecan convention), False to return peak values
    phase_dir : int
        direction of phase distribution: +/-1 (-1 clockwise) to enforce

    Returns
    -------
    data_dqh : DataTime
        data object transformed in dqh frame
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
    return data_time.n2dqh(is_dqh_rms=is_dqh_rms, phase_dir=phase_dir)
