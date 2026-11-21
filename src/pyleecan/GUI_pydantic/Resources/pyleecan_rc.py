"""Qt resources of the GUI (generated, see generate_gui_new.py).

The compiled resources of the legacy GUI are loaded from their file, without
importing the legacy GUI package (and its classes); GUI_new and GUI_pydantic
register them once.
"""

import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

_NAME = "pyleecan._gui_resources_rc"
if _NAME not in sys.modules:
    _spec = spec_from_file_location(
        _NAME, Path(__file__).resolve().parents[2] / "GUI" / "Resources" / "pyleecan_rc.py"
    )
    sys.modules[_NAME] = module_from_spec(_spec)
    _spec.loader.exec_module(sys.modules[_NAME])
