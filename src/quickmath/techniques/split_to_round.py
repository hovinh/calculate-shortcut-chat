from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique

# How far below a multiple of 100 a number may be to count as "close" to it.
MAX_GAP = 9


def _round_up(x: int) -> tuple[int, int] | None:
    """The next multiple of 100 above x and how far away it is, if x is close to it.

    e.g. 197 -> (200, 3), 98 -> (100, 2), 185 -> None.
    """
    if x <= 0 or x % 100 == 0:
        return None
    target = (x // 100 + 1) * 100
    gap = target - x
    return (target, gap) if gap <= MAX_GAP else None


def _split(problem: Problem) -> tuple[int, int, int, int] | None:
    """(near, other, target, gap): round `near` up to `target` using `gap` taken from `other`.

    If both numbers are close to a hundred, the one with the smaller gap is rounded.
    """
    candidates = []
    for near, other in ((problem.a, problem.b), (problem.b, problem.a)):
        rounded = _round_up(near)
        # The other number must have something left after giving away the gap.
        if rounded is not None and rounded[1] < other:
            candidates.append((near, other, *rounded))
    return min(candidates, key=lambda c: (c[3], -c[0]), default=None)


@register
class SplitToRound(Technique):
    name = "split_to_round"
    title = "Split the adder"
    rule = (
        "If one number is just below a multiple of 100, split the other number so that part of it "
        "fills the gap: 197 + 67 = 197 + 3 + 64 = 200 + 64."
    )
    operation = Operation.ADD
    # General fallback; narrower addition tricks rank above it.
    priority = 1

    def _applies(self, problem: Problem) -> bool:
        return _split(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        near, other, target, gap = _split(problem)
        rest = other - gap
        answer = target + rest
        return [
            Step(
                say=f"{near} is {gap} less than {target}, so split {other} into {gap} + {rest}",
                expr=f"{other} − {gap}",
                result=rest,
            ),
            Step(say=f"Give the {gap} to {near} to make {target}", expr=f"{near} + {gap}", result=target),
            Step(say="Add on what's left", expr=f"{target} + {rest}", result=answer),
        ], answer
