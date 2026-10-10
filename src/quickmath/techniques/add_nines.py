from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_nines


@register
class AddNines(Technique):
    name = "add_nines"
    title = "Adding 99, 999, …"
    rule = (
        "Adding a number made only of 9s is the same as adding the next power of 10 and then "
        "subtracting 1, because 99 = 100 − 1, 999 = 1000 − 1, and so on."
    )
    operation = Operation.ADD
    # The general form of add_9, so it ranks below it.
    priority = 5

    def _applies(self, problem: Problem) -> bool:
        return is_nines(problem.a) or is_nines(problem.b)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        nines, n = (problem.b, problem.a) if is_nines(problem.b) else (problem.a, problem.b)
        round_up = nines + 1
        plus_round = n + round_up
        answer = plus_round - 1
        return [
            Step(
                say=f"{nines} is {round_up} − 1, so first add {round_up}",
                expr=f"{n} + {round_up}",
                result=plus_round,
            ),
            Step(say="Then take away the extra 1", expr=f"{plus_round} − 1", result=answer),
        ], answer
