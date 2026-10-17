from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class SumArithmeticSeries(Technique):
    name = "sum_arithmetic_series"
    title = "Adding a series that goes up by the same difference"
    rule = (
        "To add a series where each number is the one before plus the same difference, count the numbers "
        "as (last − first) ÷ difference + 1, then multiply the count by half of first + last: "
        "2 + 5 + 8 + … + 32 has (32 − 2) ÷ 3 + 1 = 11 numbers, so 11 × (2 + 32) ÷ 2 = 11 × 17 = 187. "
        "If first + last is odd, halve the count instead."
    )
    operation = Operation.SERIES
    # Works for every series, so the narrower series tricks rank above it.
    priority = -1

    def _applies(self, problem: Problem) -> bool:
        return problem.b > problem.a

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b, d = problem.a, problem.b, problem.step
        count = (b - a) // d + 1
        steps = [
            Step(
                say=f"Count the numbers: take the first from the last, divide by the difference, {d}, and add 1",
                expr=f"({b} − {a}) ÷ {d} + 1",
                result=count,
            )
        ]
        ends = a + b
        if ends % 2 == 0:
            half = ends // 2
            steps.append(Step(say="Add the first and last numbers and halve it", expr=f"({a} + {b}) ÷ 2", result=half))
            factors = (count, half)
        else:
            # first + last is odd only when the count is even, so halving the count keeps whole numbers.
            half = count // 2
            steps += [
                Step(say="Add the first and last numbers", expr=f"{a} + {b}", result=ends),
                Step(say=f"{ends} is odd, so halve the count instead", expr=f"{count} ÷ 2", result=half),
            ]
            factors = (half, ends)
        answer = factors[0] * factors[1]
        steps.append(Step(say="Multiply them", expr=f"{factors[0]} × {factors[1]}", result=answer))
        return steps, answer
