from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_power_of_10
from quickmath.techniques.subtract_from_nines import SubtractFromNines


@register
class SubtractFromPowerOf10(Technique):
    name = "subtract_from_power_of_10"
    title = "Subtracting from 10, 100, 1000, …"
    rule = (
        "Think of 100 as 99 + 1 (and 1000 as 999 + 1, and so on): subtract from the 9s instead, "
        "which needs no borrowing, then add the 1 back."
    )
    operation = Operation.SUBTRACT
    priority = 10

    def _applies(self, problem: Problem) -> bool:
        # b must fit within the 9s, i.e. b < a.
        return is_power_of_10(problem.a) and 0 <= problem.b < problem.a

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        nines = problem.a - 1
        first = Step(
            say=f"Think of {problem.a} as {nines} + 1, so subtract from {nines} instead and add the 1 back at the end",
            expr=f"{problem.a} − 1",
            result=nines,
        )
        nine_steps, from_nines = SubtractFromNines().steps(Problem(a=nines, op=Operation.SUBTRACT, b=problem.b))
        answer = from_nines + 1
        last = Step(say="Add back the 1", expr=f"{from_nines} + 1", result=answer)
        return [first, *nine_steps, last], answer
