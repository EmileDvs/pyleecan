# Experimental dataclass generated from Generator/ClassesRef/Optimization/OptiGenAlg.csv
"""Generated experimental dataclass; do not edit by hand."""

from dataclasses import dataclass
from typing import Any, Callable

from .opti_solver import OptiSolver


@dataclass(eq=False)
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
    p_cross: float = 0.9
    """Probability of crossover"""
    p_mutate: float = 0.1
    """Probability of mutation """
    size_pop: int = 40
    """Size of the population"""
    nb_gen: int = 100
    """Number of generations"""
