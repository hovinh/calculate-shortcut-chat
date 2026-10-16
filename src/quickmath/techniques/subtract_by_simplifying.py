from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SubtractBySimplifying(Technique):
    name = "subtract_by_simplifying"
    title = "Subtract by simplifying"
    rule = (
        "Taking the same amount away from both numbers doesn't change the difference, so keep doing "
        "that until the subtraction is easy: 1103 − 38 = 1100 − 35 = 1095 − 30 = 1065."
    )
    operation = Operation.SUBTRACT
    # Narrower than subtract_in_steps, but subtracting a nearby hundred is simpler still.
    priority = 1

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        # Only worth it when the ones would need borrowing; b keeps a tens part to take away at the end.
        return 10 <= b <= a and a % 10 < b % 10

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        steps = []
        # First make a end in 0, then b.
        for shift in (a % 10, (b - a % 10) % 10):
            if shift == 0:
                continue
            steps.append(
                Step(
                    say=f"Take {shift} away from both numbers, so {a} − {b} becomes {a - shift} − {b - shift}",
                    expr=f"{a} − {shift}",
                    result=a - shift,
                )
            )
            a, b = a - shift, b - shift
        answer = a - b
        steps.append(Step(say="Now take away the round number", expr=f"{a} − {b}", result=answer))
        return steps, answer
