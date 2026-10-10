from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_nines


@register
class SubtractFromNines(Technique):
    name = "subtract_from_nines"
    title = "Subtracting from 9, 99, 999, …"
    rule = (
        "When subtracting from a number made only of 9s, there is never any borrowing: "
        "work left to right and take each digit of the other number away from 9."
    )
    operation = Operation.SUBTRACT
    priority = 10

    def _applies(self, problem: Problem) -> bool:
        # The number taken away must fit within the 9s, or the answer would go negative.
        return is_nines(problem.a) and 0 <= problem.b <= problem.a

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        width = len(str(problem.a))
        padded = str(problem.b).zfill(width)
        steps = []
        for i, d in enumerate(padded):
            say = f"Next digit: 9 − {d}"
            if i == 0:
                say = f"Start from the left: 9 − {d}"
                if padded != str(problem.b):
                    say = f"{problem.b} has fewer digits than {problem.a}, so treat it as {padded}. " + say
            steps.append(Step(say=say, expr=f"9 − {d}", result=9 - int(d)))
        digits = "".join(str(s.result) for s in steps)
        answer = int(digits)
        steps.append(Step(say="Read the digits together", expr=" ".join(digits), result=answer))
        return steps, answer
