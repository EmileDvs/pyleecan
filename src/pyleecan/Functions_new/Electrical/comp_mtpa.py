"""Deprecated alias of LUTdq.comp_MTPA (moved to the class, removed in Phase 2)."""

from warnings import warn


def comp_MTPA(
    machine,
    LUT,
    N0_min,
    N0_max,
    Nspeed,
    Ntorque,
    I_max,
    U_max,
    Rs=None,
    Tsta=20,
    n_Id=100,
    n_Iq=100,
    is_plot=False,
):
    """Deprecated: use LUTdq.comp_MTPA"""
    warn(
        "comp_MTPA is deprecated, use LUTdq.comp_MTPA (removed in Phase 2)",
        DeprecationWarning,
        stacklevel=2,
    )
    return LUT.comp_MTPA(
        machine,
        N0_min,
        N0_max,
        Nspeed,
        Ntorque,
        I_max,
        U_max,
        Rs,
        Tsta,
        n_Id,
        n_Iq,
        is_plot,
    )
