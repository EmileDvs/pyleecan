from ....Functions_new.utils.labels import decode_label, STATOR_LAB, ROTOR_LAB, KEY_LAB, HOLEM_LAB, HOLEV_LAB, MAG_LAB, LAM_LAB, VENT_LAB, WEDGE_LAB, BAR_LAB
from ....definitions import config_dict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ....Classes_new.geometry.surface import Surface




@staticmethod
def get_color_legend_from_surface(surf: Surface, is_lam_only: bool = False) -> tuple[str | None, str | None]:
    """Return the color and legend to use for plot the surface

    Parameters
    ----------
    surf : Surface
        Surfaces on which we want the color and legend
    is_lam_only : bool
        True to plot only the lamination (remove the Winding)

    Returns
    -------
    color : str or None
        Color to use on the patch (None: not plotted)
    legend : str or None
        Legend to display for the surface (None: no legend)
    """
    # The colors of the configuration when called (the defaults of the
    # wedges and keys added once)
    color_dict = config_dict["PLOT"]["COLOR_DICT"]
    color_dict.setdefault("WEDGE_COLOR", "y")
    color_dict.setdefault("KEY_COLOR", "y")
    WEDGE_COLOR = color_dict["WEDGE_COLOR"]
    KEY_COLOR = color_dict["KEY_COLOR"]
    VENT_COLOR = color_dict["VENT_COLOR"]
    ROTOR_COLOR = color_dict["ROTOR_COLOR"]
    STATOR_COLOR = color_dict["STATOR_COLOR"]
    MAGNET_COLOR = color_dict["MAGNET_COLOR"]
    BAR_COLOR = color_dict["BAR_COLOR"]
    label_dict = decode_label(surf.label)

    if LAM_LAB in label_dict["surf_type"] and STATOR_LAB in label_dict["lam_type"]:
        return STATOR_COLOR, "Stator"

    elif LAM_LAB in label_dict["surf_type"] and ROTOR_LAB in label_dict["lam_type"]:
        return ROTOR_COLOR, "Rotor"

    elif VENT_LAB in label_dict["surf_type"]:
        return VENT_COLOR, None

    # Before will always be ploted
    elif is_lam_only:
        return None, None

    # After will be ploted only if we do not want the lamination only.
    elif HOLEV_LAB in label_dict["surf_type"]:
        return VENT_COLOR, None

    elif HOLEM_LAB in label_dict["surf_type"] or MAG_LAB in label_dict["surf_type"]:
        return MAGNET_COLOR, "Magnet"

    elif WEDGE_LAB in label_dict["surf_type"]:
        return WEDGE_COLOR, "Wedge"

    elif KEY_LAB in label_dict["surf_type"]:
        return KEY_COLOR, "Key"

    elif BAR_LAB in label_dict["surf_type"]:
        return BAR_COLOR, f"{label_dict['lam_type']} Bar"

    else:
        raise Exception(f"Unknown label for plot {surf.label}")
