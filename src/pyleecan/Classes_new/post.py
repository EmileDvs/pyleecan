# Experimental dataclass generated from Generator/ClassesRef/Post/Post.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass

from ._pyleecan_class import PyleecanClass
from .simulation import Simulation
from .var_simu import VarSimu


@dataclass(eq=False)
class Post(PyleecanClass):
    """Abstract class for postprocessing

    Attributes
    ----------
    """

    def __post_init__(self):
        super().__post_init__()

    def _assert_parent_type(self, parent):
        if parent is not None and not isinstance(
            parent,
            (
                Simulation,
                VarSimu,
            ),
        ):
            raise TypeError(
                "Post parent must be an instance of Simulation or VarSimu, or None; "
                + f"got {type(parent).__name__}"
            )
