from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def is_teen(x: int) -> bool:
    """True for 10 to 19."""
    return 10 <= x <= 19


@register
class MultiplyTeens(Technique):
    name = "multiply_teens"
    title = "Multiplying two numbers between 10 and 19"
    rule = (
        "To multiply two numbers between 10 and 19, add the units digit of one to the other number "
        "and multiply by 10, then add the product of the two units digits."
    )
    operation = Operation.MULTIPLY
    # Below multiply_by_power_of_10, which is simpler for 10 × 17.
    priority = 5

    def _applies(self, problem: Problem) -> bool:
        return is_teen(problem.a) and is_teen(problem.b)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        ua, ub = a % 10, b % 10
        total = a + ub
        tens = total * 10
        units = ua * ub
        answer = tens + units
        return [
            Step(say=f"Add the units digit of {b} to {a}", expr=f"{a} + {ub}", result=total),
            Step(say="Multiply that by 10", expr=f"{total} × 10", result=tens),
            Step(say=f"Multiply the units digits of {a} and {b}", expr=f"{ua} × {ub}", result=units),
            Step(say="Add the two results", expr=f"{tens} + {units}", result=answer),
        ], answer
