# Experimental dataclass generated from Generator/ClassesRef/Output/OutInternal.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, ClassVar

from .._legacy_class import LegacyClass


@dataclass(eq=False)
class OutInternal(LegacyClass):
    """Abstract class whose childs enable to store outputs related to a specific model

    Attributes
    ----------
    """

    _package: ClassVar[str] = "Output"
    """Name of the package of the legacy class module"""

    if TYPE_CHECKING:
        # Members of the daughter classes, for the type checkers
        # (not defined at runtime: no field, no method)

        @property
        def handler_list(self) -> list[Any]: ...
        @handler_list.setter
        def handler_list(self, value: list[Any]) -> None: ...

        @property
        def FEMM_dict(self) -> dict[str, Any]: ...
        @FEMM_dict.setter
        def FEMM_dict(self, value: dict[str, Any]) -> None: ...
