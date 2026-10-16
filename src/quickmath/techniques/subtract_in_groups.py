from quickmath.models import Operation, Problem, Step
from quickmath.registry import register
from quickmath.base import Technique


def groups(x: int, count: int) -> list[int]:
    """x split into `count` two-digit groups, front first: 6218 -> [62, 18]; 38 with count 2 -> [0, 38]."""
    return [x // 100**i % 100 for i in reversed(range(count))]


def group_count(x: int) -> int:
    return (len(str(x)) + 1) // 2


@register
class SubtractInGroups(Technique):
    name = "subtract_in_groups"
    title = "Subtract in groups"
    rule = (
        "Split both numbers into groups of two digits from the right and subtract each group on its "
        "own, always taking the smaller number from the bigger one so there is no borrowing between "
        "groups. If a group of the number being taken away is bigger, subtract the other way round and "
        "take that result away at the end: 6218 − 4753: 62 − 47 = 15, 53 − 18 = 35, 1500 − 35 = 1465."
    )
    operation = Operation.SUBTRACT
    # Narrower than subtract_in_steps; the round-number tricks are simpler when they apply.
    priority = 1

    def _applies(self, problem: Problem) -> bool:
        # b needs at least two groups, or there is nothing to split.
        return 100 <= problem.b <= problem.a

    def steps(self, problem: Problem) -> tuple[list[Step], int]:
        a, b = problem.a, problem.b
        count = group_count(a)
        top, bottom = groups(a, count), groups(b, count)
        split = f"{' | '.join(map(str, top))} and {' | '.join(map(str, bottom))}"
        steps = []
        # Each group's part of the answer, already scaled by its place value: +1500, −35, ...
        parts = []
        for i, (x, y) in enumerate(zip(top, bottom)):
            place = 100 ** (count - 1 - i)
            if x >= y:
                say = f"Subtract the groups: {x} − {y}"
                expr, diff, sign = f"{x} − {y}", x - y, 1
            else:
                say = f"{x} is smaller than {y}, so subtract the other way round and take this away at the end"
                expr, diff, sign = f"{y} − {x}", y - x, -1
            if i == 0:
                say = f"Split into groups of two digits: {split}. {say}"
            steps.append(Step(say=say, expr=expr, result=diff))
            parts.append(sign * diff * place)
        answer = sum(parts)
        # Groups that cancel out add nothing; the first part left is never negative since a >= b.
        shown = [p for p in parts if p] or [0]
        combined = str(shown[0]) + "".join(f" {'+' if p > 0 else '−'} {abs(p)}" for p in shown[1:])
        steps.append(
            Step(say="Put the groups back in their places and add or take away", expr=combined, result=answer)
        )
        return steps, answer
