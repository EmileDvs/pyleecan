from typing import Optional

from ....Classes_new.mesh.solution import Solution


def replace_solution(self, solution: Solution, label: Optional[str] = "") -> None:
    """Replace the solution in the solution_didct

    Parameters
    ----------
    solution : Solution
        solution to insert
    label : Optional[str], optional
        label of the solution corresponding , by default ""
    """
    if not label:
        label = solution.label

    self[label] = solution
