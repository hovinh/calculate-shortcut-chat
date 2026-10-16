from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class MultiplyBy5(Technique):
    name = "multiply_by_5"
    title = "Multiplying by 5"
    rule = (
        "5 is half of 10, so to multiply by 5, put a 0 at the end of the other number "
        "and then halve it: 48 × 5 = 480 ÷ 2 = 240."
    )
    operation = Operation.MULTIPLY
    # Below multiply_by_power_of_10, which is simpler for 5 × 100.
    priority = 5

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return (b == 5 and a > 0) or (a == 5 and b > 0)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a if problem.b == 5 else problem.b
        tens = n * 10
        answer = tens // 2
        return [
            Step(say=f"Put a 0 at the end of {n} to multiply it by 10", expr=f"{n} × 10", result=tens),
            Step(say="Halve it, since 5 is half of 10", expr=f"{tens} ÷ 2", result=answer),
        ], answer
