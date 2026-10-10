from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SumEvens(Technique):
    name = "sum_evens"
    title = "Sum of the first n even numbers"
    rule = "The first n even numbers add up to n × (n + 1): 2 + 4 + … + 20 is the first 10, so 10 × 11 = 110."
    operation = Operation.SERIES

    def _applies(self, problem: Problem) -> bool:
        return problem.a == 2 and problem.step == 2 and problem.b >= 4

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        last = problem.b
        n = last // 2
        answer = n * (n + 1)
        return [
            Step(say=f"Count the even numbers up to {last}: there are {last} ÷ 2 of them", expr=f"{last} ÷ 2", result=n),
            Step(say="Multiply n by the next number, n + 1", expr=f"{n} × {n + 1}", result=answer),
        ], answer
