from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SumConsecutiveFromA(Technique):
    name = "sum_consecutive_from_a"
    title = "Adding a + (a + 1) + (a + 2) + … + b"
    rule = (
        "To add every number from a to b, where a is positive, take the square of a away from the square "
        "of b, add a and b, then halve it: 11 + 12 + … + 20 = (20 × 20 − 11 × 11 + 11 + 20) ÷ 2 "
        "= (400 − 121 + 31) ÷ 2 = 155."
    )
    operation = Operation.SERIES

    def _applies(self, problem: Problem) -> bool:
        # From 1, sum_consecutive is quicker; the method needs a positive first number.
        return problem.a >= 2 and problem.step == 1 and problem.b > problem.a

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        last_square = b * b
        first_square = a * a
        difference = last_square - first_square
        total = difference + a + b
        answer = total // 2
        return [
            Step(say=f"Square the last number, {b}", expr=f"{b} × {b}", result=last_square),
            Step(say=f"Square the first number, {a}", expr=f"{a} × {a}", result=first_square),
            Step(say=f"Take {first_square} away from {last_square}", expr=f"{last_square} − {first_square}", result=difference),
            Step(say=f"Add the first and last numbers, {a} and {b}", expr=f"{difference} + {a} + {b}", result=total),
            Step(say="Then halve it", expr=f"{total} ÷ 2", result=answer),
        ], answer
