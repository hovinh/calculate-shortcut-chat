from decimal import Decimal

from quickmath.models import Operation, Problem, Step, fmt, number
from quickmath.registry import register
from quickmath.base import Technique


@register
class DivideBy5(Technique):
    name = "divide_by_5"
    title = "Dividing by 5"
    rule = (
        "5 is 10 ÷ 2, so dividing by 5 is the same as doubling the number and then dividing by 10: "
        "47 ÷ 5 = 94 ÷ 10 = 9.4."
    )
    operation = Operation.DIVIDE
    priority = 5
    decimals = True

    def _applies(self, problem: Problem) -> bool:
        return problem.b == 5 and problem.a > 0

    def steps(self, problem: Problem) -> tuple[list[Step], int | Decimal]:
        n = problem.a
        doubled = n * 2
        answer = number(Decimal(doubled).scaleb(-1))
        return [
            Step(say=f"Double {fmt(n)}", expr=f"{fmt(n)} × 2", result=doubled),
            Step(say="Divide by 10, since 5 is 10 ÷ 2", expr=f"{fmt(doubled)} ÷ 10", result=answer),
        ], answer
