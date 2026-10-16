from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def _other(problem: Problem) -> int | None:
    """The number being multiplied by 11, if it has at least two digits to add."""
    a, b = problem.a, problem.b
    for eleven, n in ((b, a), (a, b)):
        if eleven == 11 and n >= 10:
            return n
    return None


@register
class MultiplyBy11(Technique):
    name = "multiply_by_11"
    title = "Multiplying by 11"
    rule = (
        "11 is 10 + 1, so multiplying by 11 adds the number to itself shifted one place left, which "
        "is the same as adding each digit to the one on its left. Write down the rightmost digit as "
        "it is, then, moving left, write the sum of each digit and the one to its right (carrying if "
        "it is 10 or more), and finish with the leftmost digit: 2341 × 11 = 2 | 2+3 | 3+4 | 4+1 | 1 = 25751."
    )
    operation = Operation.MULTIPLY
    # Simpler than multiply_teens for 11 × 13; 11 is not a power of 10, so that trick never applies.
    priority = 6

    def _applies(self, problem: Problem) -> bool:
        return _other(problem) is not None

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        n = _other(problem)
        d = [int(c) for c in str(n)]
        # The answer line, filled in from the right.
        line = [d[-1]]
        steps = [Step(say=f"Write down the rightmost digit of {n}, {d[-1]}, as it is", expr=f"{d[-1]}", result=d[-1])]
        carry = 0
        for i in range(len(d) - 1, 0, -1):
            left, right = d[i - 1], d[i]
            total = left + right + carry
            say = f"Add {left} to the digit on its right, {right}"
            expr = f"{left} + {right}"
            if carry:
                say += f", plus the {carry} carried"
                expr += f" + {carry}"
            say += f", write {total % 10} and carry {total // 10}" if total >= 10 else f", write {total}"
            steps.append(Step(say=say, expr=expr, result=total))
            line.append(total % 10)
            carry = total // 10
        leftmost = d[0] + carry
        if carry:
            say, expr = f"Write the leftmost digit, {d[0]}, plus the {carry} carried", f"{d[0]} + {carry}"
        else:
            say, expr = f"Write the leftmost digit, {d[0]}", f"{d[0]}"
        steps.append(Step(say=say, expr=expr, result=leftmost))
        line.append(leftmost)
        line.reverse()
        answer = int("".join(map(str, line)))
        steps.append(
            Step(say="Read the answer line from left to right", expr=" | ".join(map(str, line)), result=answer)
        )
        return steps, answer
