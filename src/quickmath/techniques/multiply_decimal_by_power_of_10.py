from decimal import Decimal

from quickmath.models import Operation, Problem, Step, fmt, number
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_power_of_10


@register
class MultiplyDecimalByPowerOf10(Technique):
    name = "multiply_decimal_by_power_of_10"
    title = "Multiplying a decimal by 10, 100, 1000, …"
    rule = (
        "To multiply a decimal by 10, 100, 1000 and so on, move the decimal point to the right "
        "by as many places as there are zeros: one place for 10, two for 100, three for 1000."
    )
    operation = Operation.MULTIPLY
    priority = 10
    decimals = True

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return (isinstance(a, Decimal) and a > 0 and is_power_of_10(b)) or (
            isinstance(b, Decimal) and b > 0 and is_power_of_10(a)
        )

    def steps(self, problem: Problem) -> tuple[list[Step], int | Decimal]:
        if isinstance(problem.a, Decimal):
            n, power = problem.a, problem.b
        else:
            n, power = problem.b, problem.a
        zeros = len(str(power)) - 1
        # Shifting the exponent is exactly "moving the decimal point".
        answer = number(n.scaleb(zeros))
        places = f"{zeros} place{'s' if zeros != 1 else ''}"
        decimal_places = -n.as_tuple().exponent
        fill = ", filling the empty places with zeros" if zeros > decimal_places else ""
        return [
            Step(say=f"Count the zeros in {power}", expr=f"zeros in {power}", result=zeros),
            Step(
                say=f"Move the decimal point in {fmt(n)} {places} to the right{fill}",
                expr=f"{fmt(n)} → {fmt(answer)}",
                result=answer,
            ),
        ], answer
