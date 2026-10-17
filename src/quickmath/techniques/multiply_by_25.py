from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class MultiplyBy25(Technique):
    name = "multiply_by_25"
    title = "Multiplying by 25"
    rule = (
        "25 × 4 is 100, so multiplying by 25 is the same as multiplying by 100 and dividing by 4. "
        "Put two 0s at the end of the other number and then divide by 4: 48 × 25 = 4800 ÷ 4 = 1200."
    )
    operation = Operation.MULTIPLY
    # Same rank as multiply_by_5; below multiply_by_power_of_10, which is simpler for 25 × 100.
    priority = 5

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return (b == 25 and a > 0) or (a == 25 and b > 0)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a if problem.b == 25 else problem.b
        hundreds = n * 100
        answer = hundreds // 4
        return [
            Step(say=f"Put two 0s at the end of {n} to multiply it by 100", expr=f"{n} × 100", result=hundreds),
            Step(say="Divide by 4, since 25 is 100 ÷ 4", expr=f"{hundreds} ÷ 4", result=answer),
        ], answer
