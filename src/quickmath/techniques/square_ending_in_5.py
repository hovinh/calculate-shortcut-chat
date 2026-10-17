from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SquareEndingIn5(Technique):
    name = "square_ending_in_5"
    title = "Squaring numbers that end in 5"
    rule = (
        "To square a number that ends in 5, take the part of the number before the 5, multiply it "
        "by one more than itself, and put 25 after the result: 35 × 35 = 3 × 4 | 25 = 1225."
    )
    operation = Operation.MULTIPLY
    # Simpler than multiply_teens for 15 × 15 and multiply_by_25 for 25 × 25.
    priority = 6

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        # 5 × 5 has nothing before the 5.
        return a == b and a >= 15 and a % 10 == 5

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = problem.a
        front = n // 10
        product = front * (front + 1)
        answer = int(f"{product}25")
        return [
            Step(say=f"Take the part of {n} before the 5", expr=f"{n} → {front}", result=front),
            Step(say=f"Multiply {front} by one more than itself, {front + 1}", expr=f"{front} × {front + 1}", result=product),
            Step(say=f"Put 25 after {product}", expr=f"{product} | 25", result=answer),
        ], answer
