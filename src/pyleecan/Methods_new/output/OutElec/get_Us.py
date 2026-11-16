from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.scidatatool.data import Data
    from ....Classes_new.scidatatool.data_nd import DataND


def get_Us(
    self, Time: Data | None = None, is_dqh: bool = False, is_fund_only: bool = False, is_harm_only: bool = False, is_freq: bool | None = None
) -> DataND:
    """Return the fundamental stator voltage as DataND object

    Parameters
    ----------
    self : OutElec
        an OutElec object
    Time : Data
        Time axis
    is_dqh : bool
        True to rotate in DQH frame
    is_fund_only : bool
        True to return only fundamental component
    is_harm_only : bool
        True to return only components at higher frequencies than fundamental component
    is_freq: bool
        True to calculate dqh transformation in frequency domain

    Returns
    -------
    Us: DataND
        stator voltage
    """

    label = self.parent.simu.machine.stator.get_label()
    Udq_dict = self.OP.get_Ud_Uq()

    data_dict = {
        "name": "Stator voltage",
        "unit": "V",
        "symbol": "U_s",
        "lam_label": label,
        "Ad": Udq_dict["Ud"],
        "Aq": Udq_dict["Uq"],
    }

    Us = self.get_electrical(
        data_dict,
        Time=Time,
        is_dqh=is_dqh,
        is_fund_only=is_fund_only,
        is_harm_only=is_harm_only,
        is_freq=is_freq,
    )

    return Us
