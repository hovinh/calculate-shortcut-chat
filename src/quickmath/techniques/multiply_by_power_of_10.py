from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique
from quickmath.techniques._digits import is_power_of_10


@register
class MultiplyByPowerOf10(Technique):
    name = "multiply_by_power_of_10"
    title = "Multiplying by 10, 100, 1000, …"
    rule = (
        "To multiply by 10, 100, 1000 and so on, count the zeros in it "
        "and write that many zeros at the end of the other number."
    )
    operation = Operation.MULTIPLY
    priority = 10

    def _applies(self, problem: Problem) -> bool:
        a, b = problem.a, problem.b
        return (is_power_of_10(b) and a > 0) or (is_power_of_10(a) and b > 0)

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        if is_power_of_10(problem.b):
            n, power = problem.a, problem.b
        else:
            n, power = problem.b, problem.a
        zeros = len(str(power)) - 1
        answer = int(f"{n}{'0' * zeros}")
        return [
            Step(say=f"Count the zeros in {power}", expr=f"zeros in {power}", result=zeros),
            Step(
                say=f"Write {zeros} zero{'s' if zeros != 1 else ''} at the end of {n}",
                expr=f"{n} followed by {'0' * zeros}",
                result=answer,
            ),
        ], answer
