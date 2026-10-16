from decimal import Decimal

from quickmath.models import Operation, Problem, Step, fmt, number
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_power_of_10


@register
class DivideByPowerOf10(Technique):
    name = "divide_by_power_of_10"
    title = "Dividing by 10, 100, 1000, …"
    rule = (
        "To divide by 10, 100, 1000 and so on, count the zeros in it and put a decimal point in the "
        "other number that many digits from the right: one digit for 10, two for 100. If the number "
        "already has a decimal point, move it to the left by that many places."
    )
    operation = Operation.DIVIDE
    priority = 10
    decimals = True

    def _applies(self, problem: Problem) -> bool:
        return problem.a > 0 and is_power_of_10(problem.b)

    def steps(self, problem: Problem) -> tuple[list[Step], int | Decimal]:
        n, power = problem.a, problem.b
        zeros = len(str(power)) - 1
        digits = f"{zeros} digit{'s' if zeros != 1 else ''}"
        places = f"{zeros} place{'s' if zeros != 1 else ''}"
        # Shifting the exponent is exactly "moving the decimal point"; it keeps zeros like 45.00.
        shifted = Decimal(n).scaleb(-zeros)
        answer = number(shifted)
        if isinstance(n, int):
            say = f"Put a decimal point in {n}, leaving {digits} to its right"
        else:
            say = f"Move the decimal point in {fmt(n)} {places} to the left"
        # Digits before the decimal point; 0.5 has none worth counting.
        whole_digits = len(str(int(n))) if int(n) else 0
        if zeros > whole_digits:
            say += ", filling the empty places after the point with zeros"
        expr = f"{fmt(n)} → {fmt(shifted)}"
        if fmt(shifted) != fmt(answer):
            say += ", then drop the zeros at the end"
            expr += f" = {fmt(answer)}"
        return [
            Step(say=f"Count the zeros in {power}", expr=f"zeros in {power}", result=zeros),
            Step(say=say, expr=expr, result=answer),
        ], answer
