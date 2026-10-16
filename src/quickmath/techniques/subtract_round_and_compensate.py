from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import nearest_hundred


def _target(problem: Problem) -> int | None:
    """The round number to subtract instead of b, if b is close to one."""
    target = nearest_hundred(problem.b)
    # Keep every step non-negative: the round number and b must both fit within a.
    if target is None or target > problem.a or problem.b > problem.a:
        return None
    return target


@register
class SubtractRoundAndCompensate(Technique):
    name = "subtract_round_and_compensate"
    title = "Subtract more or less than needed"
    rule = (
        "If the number being taken away is close to a multiple of 100, subtract that round number "
        "instead, then adjust for the difference: 176 − 98 = 176 − 100 + 2 = 78."
    )
    operation = Operation.SUBTRACT
    # General fallback; the narrower subtract-from-9s/10s tricks rank above it.
    priority = 2

    def _applies(self, problem: Problem) -> bool:
        return _target(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        target = _target(problem)
        rounded_diff = a - target
        answer = rounded_diff + (target - b)
        if b < target:
            gap = target - b
            b_is = f"{target} − {gap}"
            adjust = Step(
                say=f"That took away {gap} too much, so add it back", expr=f"{rounded_diff} + {gap}", result=answer
            )
        else:
            gap = b - target
            b_is = f"{target} + {gap}"
            adjust = Step(
                say=f"That took away {gap} too little, so take away {gap} more",
                expr=f"{rounded_diff} − {gap}",
                result=answer,
            )
        return [
            Step(say=f"{b} is {b_is}, so subtract {target} instead", expr=f"{a} − {target}", result=rounded_diff),
            adjust,
        ], answer
