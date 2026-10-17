from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class MultiplyEndsAddTo10(Technique):
    name = "multiply_ends_add_to_10"
    title = "Multiplying two numbers with the same front and last digits that add to 10"
    rule = (
        "When two numbers are the same apart from their last digits, and those last digits add up to "
        "10, multiply the part that is the same by one more than itself, then multiply the last digits "
        "and put the result after it, with a 0 in front if it is a single digit: "
        "28 × 22 = 2 × 3 | 8 × 2 = 616, and 11 × 19 = 1 × 2 | 1 × 9 = 209."
    )
    operation = Operation.MULTIPLY
    # Below square_ending_in_5, its special case; above multiply_by_11 and multiply_teens,
    # which need carrying for 11 × 19.
    priority = 7

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return a >= 10 and b >= 10 and a // 10 == b // 10 and a % 10 + b % 10 == 10

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        front = a // 10
        ua, ub = a % 10, b % 10
        product = front * (front + 1)
        units = ua * ub
        tail = f"{units:02d}"
        answer = int(f"{product}{tail}")
        say = f"Put {tail} after {product}"
        if units < 10:
            say += f", with a 0 in front of the {units} since it is a single digit"
        return [
            Step(say=f"Take the part that is the same in {a} and {b}", expr=f"{a}, {b} → {front}", result=front),
            Step(say=f"Multiply {front} by one more than itself, {front + 1}", expr=f"{front} × {front + 1}", result=product),
            Step(say="Multiply the last digits, which add up to 10", expr=f"{ua} × {ub}", result=units),
            Step(say=say, expr=f"{product} | {tail}", result=answer),
        ], answer
