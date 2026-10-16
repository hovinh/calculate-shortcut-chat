from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class MultiplyBy9(Technique):
    name = "multiply_by_9"
    title = "Multiplying by 9"
    rule = (
        "9 is 10 − 1, so to multiply by 9, put a 0 at the end of the other number and then subtract "
        "the original number: 47 × 9 = 470 − 47 = 423."
    )
    operation = Operation.MULTIPLY
    priority = 5

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return (b == 9 and a > 0) or (a == 9 and b > 0)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a if problem.b == 9 else problem.b
        tens = n * 10
        answer = tens - n
        return [
            Step(say=f"Put a 0 at the end of {n} to multiply it by 10", expr=f"{n} × 10", result=tens),
            Step(say=f"Subtract the original {n}, since 9 is 10 − 1", expr=f"{tens} − {n}", result=answer),
        ], answer
