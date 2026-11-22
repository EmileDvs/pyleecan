"""LUTdq.comp_MTPA is deprecated (Step 15): it warns when called."""

import pytest

from pyleecan.Classes_new.output.lut_dq import LUTdq


def test_comp_mtpa_warns():
    with pytest.warns(DeprecationWarning, match="comp_MTPA is deprecated"):
        with pytest.raises(Exception):  # Older EEC API: it does not run
            LUTdq().comp_MTPA(None, 0, 1, 1, 1, 1, 1)
