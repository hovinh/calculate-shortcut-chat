from quickmath import registry
from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def _central(problem: Problem) -> int | None:
    """The multiple of 10 halfway between a and b, if both are less than 10 away from it."""
    a, b = problem.a, problem.b
    if a <= 0 or b <= 0 or a == b or (a + b) % 2:
        return None
    central = (a + b) // 2
    return central if central % 10 == 0 and abs(a - central) < 10 else None


@register
class MultiplyEquidistantFrom10s(Technique):
    name = "multiply_equidistant_from_10s"
    title = "Multiplying numbers the same distance from a multiple of 10"
    rule = (
        "To multiply two numbers the same distance either side of a multiple of 10, the central number, "
        "square the central number (see squaring numbers that end in 0), square the distance of the "
        "numbers from it, and take the second square away from the first: "
        "28 × 32 = 30 × 30 − 2 × 2 = 900 − 4 = 896."
    )
    operation = Operation.MULTIPLY
    # Above multiply_by_5, multiply_by_9 and multiply_by_25 for 5 × 15, 9 × 11 and 15 × 25.
    priority = 6

    def _applies(self, problem: Problem) -> bool:
        return _central(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        central = _central(problem)
        high = max(a, b)
        # Square the central number the way square_ending_in_0 does.
        square_steps, square = registry.get("square_ending_in_0").steps(
            Problem(a=central, op=Operation.MULTIPLY, b=central)
        )
        gap = high - central
        gap_square = gap * gap
        answer = square - gap_square
        return [
            Step(say=f"Find the central number halfway between {a} and {b}", expr=f"({a} + {b}) ÷ 2", result=central),
            *square_steps,
            Step(say=f"Find how far {a} and {b} are from {central}", expr=f"{high} − {central}", result=gap),
            Step(say=f"Square the distance, {gap}", expr=f"{gap} × {gap}", result=gap_square),
            Step(say=f"Take {gap_square} away from {square}", expr=f"{square} − {gap_square}", result=answer),
        ], answer
