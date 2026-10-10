from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SumOdds(Technique):
    name = "sum_odds"
    title = "Sum of the first n odd numbers"
    rule = "The first n odd numbers add up to n × n: 1 + 3 + … + 19 is the first 10, so 10 × 10 = 100."
    operation = Operation.SERIES

    def _applies(self, problem: Problem) -> bool:
        return problem.a == 1 and problem.step == 2 and problem.b >= 3

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        last = problem.b
        n = (last + 1) // 2
        answer = n * n
        return [
            Step(
                say=f"Count the odd numbers up to {last}: there are ({last} + 1) ÷ 2 of them",
                expr=f"({last} + 1) ÷ 2",
                result=n,
            ),
            Step(say="Square n", expr=f"{n} × {n}", result=answer),
        ], answer
