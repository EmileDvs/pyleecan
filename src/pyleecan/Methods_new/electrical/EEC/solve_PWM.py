from . import AbstractClassError
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data_freq import DataFreq
    from ....Classes_new.output.output import Output


def solve_PWM(self, output: Output) -> DataFreq:
    """Get stator current harmonics due to PWM harmonics

    Parameters
    ----------
    self : EEC
        an EEC object
    output: Output
        An Output object
    is_dqh_freq: bool
        True to consider frequencies in dqh frame

    Returns
    ------
    Is_PWM : DataFreq
        Stator current harmonics as DataFreq
    """
    raise AbstractClassError(
        "EEC is an abstract class, please create one of its daughters."
    )
