from ....definitions import config_dict
from ....Functions_new.labels import decode_label
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import numpy as np

PHASE_COLORS = config_dict["PLOT"]["COLOR_DICT"]["PHASE_COLORS"]


@staticmethod
def find_wind_phase_color(label: str, wind_mat: np.ndarray | None) -> tuple[str | list, str | None]:
    """Returns Color phase of the Winding surface

    Parameters
    ----------
    label : str
        the label of the surface

    wind_mat : numpy.ndarray
        A matrix [Nrad,Ntan,Zs,qs] representing the winding

    Returns
    -------
    color: str
        Color of the zone

    """
    from ....Classes_new.machine.winding import Winding
    label_dict = decode_label(label)
    Nrad = label_dict["R_id"]
    Ntan = label_dict["T_id"]
    Zs_id = label_dict["S_id"]
    if wind_mat is not None:
        q_id = Winding._get_phase_id(wind_mat, Nrad, Ntan, Zs_id)
        if q_id is None:  # No phase => White
            color = "w"
            sign = None
        else:
            # Looping colors when there are more than 8 phases
            color = PHASE_COLORS[q_id % len(PHASE_COLORS)]
            if wind_mat[Nrad, Ntan, Zs_id, q_id] > 0:
                sign = "+"
            elif wind_mat[Nrad, Ntan, Zs_id, q_id] < 0:
                sign = "-"
            else:
                sign = None
    else:
        color = PHASE_COLORS[0]
        sign = None

    return color, sign


