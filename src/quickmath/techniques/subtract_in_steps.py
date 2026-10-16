from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def place_parts(x: int) -> list[int]:
    """x split by place value, largest first, skipping zeros: 1205 -> [1000, 200, 5]."""
    s = str(x)
    return [int(d) * 10 ** (len(s) - 1 - i) for i, d in enumerate(s) if d != "0"]


@register
class SubtractInSteps(Technique):
    name = "subtract_in_steps"
    title = "Subtract in steps"
    rule = (
        "Split the number being taken away into parts by place value and take them away one at a "
        "time, largest first: 83 − 27 = 83 − 20 − 7 = 63 − 7 = 56."
    )
    operation = Operation.SUBTRACT
    # The most general subtraction trick, so every other one ranks above it.
    priority = 0

    def _applies(self, problem: Problem) -> bool:
        # More than one part to take away, and every step stays non-negative.
        return 0 < problem.b <= problem.a and len(place_parts(problem.b)) > 1

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        parts = place_parts(b)
        split = " + ".join(str(p) for p in parts)
        steps = []
        left = a
        for i, part in enumerate(parts):
            say = f"Split {b} into {split}, then take away {part} first" if i == 0 else f"Take away {part}"
            steps.append(Step(say=say, expr=f"{left} − {part}", result=left - part))
            left -= part
        return steps, left
