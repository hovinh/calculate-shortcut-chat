from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


@register
class AddInParts(Technique):
    name = "add_in_parts"
    title = "Add in parts"
    rule = (
        "Split each number into its tens and its ones, add the two kinds of parts separately, "
        "then put them together: 123 + 46 = (120 + 40) + (3 + 6) = 160 + 9."
    )
    operation = Operation.ADD
    # The most general addition trick, so every other one ranks above it.
    priority = 0

    def _applies(self, problem: Problem) -> bool:
        # Both numbers need a tens part and a ones part, or one of the sums is "+ 0".
        return all(x >= 10 and x % 10 != 0 for x in (problem.a, problem.b))

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        a_tens, a_ones = a - a % 10, a % 10
        b_tens, b_ones = b - b % 10, b % 10
        tens = a_tens + b_tens
        ones = a_ones + b_ones
        answer = tens + ones
        return [
            Step(
                say=f"Split {a} into {a_tens} + {a_ones} and {b} into {b_tens} + {b_ones}, then add the tens parts",
                expr=f"{a_tens} + {b_tens}",
                result=tens,
            ),
            Step(say="Separately, add the ones parts", expr=f"{a_ones} + {b_ones}", result=ones),
            Step(say="Put the two parts together", expr=f"{tens} + {ones}", result=answer),
        ], answer
