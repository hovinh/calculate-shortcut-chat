from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique

# How far from 50 still counts as near: up to 15² = 225, so at most a 2 to carry.
_NEAR = 15


@register
class SquareNear50(Technique):
    name = "square_near_50"
    title = "Squaring numbers near 50"
    rule = (
        "To square a number near 50, subtract 50 from it and add the result to 25. Then square how far "
        "the number is from 50 and put it after, as two digits: with a 0 in front if it is a single "
        "digit, or carrying the extra digit to the left if it has three: "
        "47 × 47 = 25 − 3 | 3 × 3 = 22 | 09 = 2209, and 62 × 62 = 25 + 12 | 144 = 37 + 1 | 44 = 3844."
    )
    operation = Operation.MULTIPLY
    # Below square_ending_in_5 and multiply_ends_add_to_10, which are as quick for 45 × 45.
    priority = 6

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return a == b and abs(a - 50) <= _NEAR

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a
        diff = n - 50
        gap = abs(diff)
        front = 25 + diff
        square = gap * gap
        sign = "+" if diff >= 0 else "−"
        steps = [
            Step(say=f"Subtract 50 from {n}", expr=f"{n} − 50", result=diff),
            Step(say=f"Add {diff} to 25", expr=f"25 {sign} {gap}", result=front),
            Step(say=f"Square the difference of {n} from 50, {gap}", expr=f"{gap} × {gap}", result=square),
        ]
        carry, tail = divmod(square, 100)
        if carry:
            steps.append(
                Step(
                    say=f"Keep the right two digits of {square}, {tail:02d}, and carry {carry} over to {front}",
                    expr=f"{front} + {carry}",
                    result=front + carry,
                )
            )
            front += carry
        answer = front * 100 + tail
        say = f"Put {tail:02d} after {front}"
        if square < 10:
            say += f", with a 0 in front of the {square} since it is a single digit"
        steps.append(Step(say=say, expr=f"{front} | {tail:02d}", result=answer))
        return steps, answer
