from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import nearest_hundred


def _pick(problem: Problem) -> tuple[int, int, int] | None:
    """(near, other, target): add `target` instead of `near`, then adjust.

    If both numbers are close to a hundred, the one needing the smaller adjustment is rounded.
    """
    candidates = []
    for near, other in ((problem.a, problem.b), (problem.b, problem.a)):
        target = nearest_hundred(near)
        if target is not None and other > 0:
            candidates.append((near, other, target))
    return min(candidates, key=lambda c: (abs(c[2] - c[0]), c[0]), default=None)


@register
class RoundAndCompensate(Technique):
    name = "round_and_compensate"
    title = "Add more or less than needed"
    rule = (
        "If one number is close to a multiple of 100, add that round number instead, then adjust "
        "for the difference: 459 + 97 = 459 + 100 − 3 = 556."
    )
    operation = Operation.ADD
    # Ranks below split_to_round, which handles "larger number just below a hundred" more neatly.
    priority = 1

    def _applies(self, problem: Problem) -> bool:
        return _pick(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        near, other, target = _pick(problem)
        rounded_sum = other + target
        answer = rounded_sum + (near - target)
        if near < target:
            gap = target - near
            near_is = f"{target} − {gap}"
            adjust = Step(
                say=f"That added {gap} too much, so take it away", expr=f"{rounded_sum} − {gap}", result=answer
            )
        else:
            gap = near - target
            near_is = f"{target} + {gap}"
            adjust = Step(
                say=f"That added {gap} too little, so add it on", expr=f"{rounded_sum} + {gap}", result=answer
            )
        return [
            Step(
                say=f"{near} is {near_is}, so add {target} instead",
                expr=f"{other} + {target}",
                result=rounded_sum,
            ),
            adjust,
        ], answer
