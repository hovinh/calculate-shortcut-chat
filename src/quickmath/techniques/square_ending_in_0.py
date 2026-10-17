from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def _plural(count: int, word: str) -> str:
    return f"{count} {word}{'s' if count != 1 else ''}"


@register
class SquareEndingIn0(Technique):
    name = "square_ending_in_0"
    title = "Squaring numbers that end in 0"
    rule = (
        "To square a number that ends in 0, count the zeros at its end, ignore them and square the rest "
        "of the number, then put double that many zeros after the result: "
        "300 × 300 = 3 × 3 | 0000 = 90000."
    )
    operation = Operation.MULTIPLY
    # Simpler than square_near_50 for 40 × 40, 50 × 50 and 60 × 60; multiply_by_power_of_10 stays on
    # top for 10 × 10 and 100 × 100.
    priority = 8

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return a == b and a >= 10 and a % 10 == 0

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a
        digits = str(n)
        rest = digits.rstrip("0")
        zeros = len(digits) - len(rest)
        front = int(rest)
        square = front * front
        answer = int(f"{square}{'0' * (2 * zeros)}")
        return [
            Step(say=f"Count the zeros at the end of {n}", expr=f"zeros at the end of {n}", result=zeros),
            Step(say=f"Ignore the zeros and square what is left, {front}", expr=f"{front} × {front}", result=square),
            Step(
                say=f"Put {_plural(2 * zeros, 'zero')} after {square}, double the {_plural(zeros, 'zero')} in {n}",
                expr=f"{square} | {'0' * (2 * zeros)}",
                result=answer,
            ),
        ], answer
