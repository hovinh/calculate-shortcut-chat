from quickmath import registry
from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SquareEndingIn1(Technique):
    name = "square_ending_in_1"
    title = "Squaring numbers that end in 1"
    rule = (
        "To square a number that ends in 1, square the number 1 less than it, which ends in 0 "
        "(see squaring numbers that end in 0), then add the number and the number 1 less than it: "
        "41 × 41 = 40 × 40 + 41 + 40 = 1600 + 81 = 1681."
    )
    operation = Operation.MULTIPLY
    # Above square_near_50 for 41 × 41, 51 × 51 and 61 × 61, and multiply_by_11 for 11 × 11.
    priority = 7

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        # 1 × 1 has no number ending in 0 below it to square.
        return a == b and a >= 11 and a % 10 == 1

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a
        below = n - 1
        # Square the number ending in 0 the way square_ending_in_0 does.
        square_steps, square = registry.get("square_ending_in_0").steps(
            Problem(a=below, op=Operation.MULTIPLY, b=below)
        )
        answer = square + n + below
        return [
            Step(say=f"Take the number 1 less than {n}", expr=f"{n} − 1", result=below),
            *square_steps,
            Step(say=f"Add {n} and {below} to {square}", expr=f"{square} + {n} + {below}", result=answer),
        ], answer
