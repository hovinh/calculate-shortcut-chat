from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import nearest_hundred


def _split(problem: Problem) -> tuple[int, int, int, int] | None:
    """(big, small, target, gap): round `big` up to `target` using `gap` taken from `small`.

    Only the larger number is rounded, so what's left is a round number plus a smaller one
    (when the smaller number is the close one, round_and_compensate fits better).
    """
    big, small = (problem.a, problem.b) if problem.a >= problem.b else (problem.b, problem.a)
    target = nearest_hundred(big)
    if target is None or target < big:
        return None
    gap = target - big
    # The smaller number must have something left after giving away the gap.
    if gap >= small:
        return None
    return big, small, target, gap


@register
class SplitToRound(Technique):
    name = "split_to_round"
    title = "Split the adder"
    rule = (
        "If the larger number is just below a multiple of 100, split the other number so that part of it "
        "fills the gap: 197 + 67 = 197 + 3 + 64 = 200 + 64."
    )
    operation = Operation.ADD
    # General fallback; narrower addition tricks rank above it.
    priority = 2

    def _applies(self, problem: Problem) -> bool:
        return _split(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        big, small, target, gap = _split(problem)
        rest = small - gap
        answer = target + rest
        return [
            Step(
                say=f"{big} is {gap} less than {target}, so split {small} into {gap} + {rest}",
                expr=f"{small} − {gap}",
                result=rest,
            ),
            Step(say=f"Give the {gap} to {big} to make {target}", expr=f"{big} + {gap}", result=target),
            Step(say="Add on what's left", expr=f"{target} + {rest}", result=answer),
        ], answer
