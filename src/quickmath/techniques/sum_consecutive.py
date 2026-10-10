from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SumConsecutive(Technique):
    name = "sum_consecutive"
    title = "Adding 1 + 2 + 3 + … + n"
    rule = "To add every number from 1 to n, work out n × (n + 1) ÷ 2: 1 + 2 + … + 100 = 100 × 101 ÷ 2 = 5050."
    operation = Operation.SERIES

    def _applies(self, problem: Problem) -> bool:
        return problem.a == 1 and problem.step == 1 and problem.b >= 2

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.b
        product = n * (n + 1)
        answer = product // 2
        return [
            Step(
                say=f"The numbers go from 1 to {n}, so n = {n}. Multiply n by the next number, n + 1",
                expr=f"{n} × {n + 1}",
                result=product,
            ),
            Step(say="Then halve it", expr=f"{product} ÷ 2", result=answer),
        ], answer
