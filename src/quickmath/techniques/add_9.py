from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class Add9(Technique):
    name = "add_9"
    title = "Adding 9"
    rule = "Adding 9 is the same as adding 10 and then subtracting 1, because 9 = 10 − 1."
    operation = Operation.ADD
    priority = 10

    def _applies(self, problem: Problem) -> bool:
        return 9 in (problem.a, problem.b)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a if problem.b == 9 else problem.b
        plus_10 = n + 10
        answer = plus_10 - 1
        return [
            Step(say="9 is 10 − 1, so first add 10", expr=f"{n} + 10", result=plus_10),
            Step(say="Then take away the extra 1", expr=f"{plus_10} − 1", result=answer),
        ], answer
