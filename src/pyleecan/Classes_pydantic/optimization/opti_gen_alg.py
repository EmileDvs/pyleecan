# Experimental pydantic model generated from Generator/ClassesRef/Optimization/OptiGenAlg.csv
"""Generated experimental pydantic model; do not edit by hand."""

from typing import Any, Callable, ClassVar

from pydantic import Field

from .opti_solver import OptiSolver


class OptiGenAlg(OptiSolver):
    """Genetic algorithm class

    Attributes
    ----------
    selector : function or None
        Selector of the genetic algorithm
        Default: None
    crossover : function or None
        Crossover of the genetic algorithm
        Default: None
    mutator : function or None
        Mutator of the genetic algorithm
        Default: None
    p_cross : float
        Probability of crossover
        Default: 0.9; Minimum: 0; Maximum: 1
    p_mutate : float
        Probability of mutation
        Default: 0.1; Minimum: 0; Maximum: 1
    size_pop : int
        Size of the population
        Default: 40; Minimum: 1
    nb_gen : int
        Number of generations
        Default: 100; Minimum: 1
    """

    selector: Callable[..., Any] | None = None
    """Selector of the genetic algorithm"""
    crossover: Callable[..., Any] | None = None
    """Crossover of the genetic algorithm"""
    mutator: Callable[..., Any] | None = None
    """Mutator of the genetic algorithm"""
    p_cross: float = Field(default=0.9, ge=0, le=1)
    """Probability of crossover"""
    p_mutate: float = Field(default=0.1, ge=0, le=1)
    """Probability of mutation """
    size_pop: int = Field(default=40, ge=1)
    """Size of the population"""
    nb_gen: int = Field(default=100, ge=1)
    """Number of generations"""

    _package: ClassVar[str] = "Optimization"
    """Name of the package of the legacy class module"""
