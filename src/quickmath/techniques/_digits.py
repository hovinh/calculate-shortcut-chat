"""Digit helpers shared by several techniques."""


def is_nines(x: int) -> bool:
    """True for 9, 99, 999, ..."""
    return x > 0 and set(str(x)) == {"9"}


def is_power_of_10(x: int) -> bool:
    """True for 10, 100, 1000, ..."""
    s = str(x)
    return x >= 10 and s == "1" + "0" * (len(s) - 1)


# How far from a multiple of 100 a number may be to count as "close" to it.
NEAR_HUNDRED_GAP = 9


def nearest_hundred(x: int) -> int | None:
    """The multiple of 100 that x is close to (within NEAR_HUNDRED_GAP), e.g. 197 -> 200, 103 -> 100.

    None if x is not close to one, is one already, or is not positive.
    """
    if x <= 0 or x % 100 == 0:
        return None
    target = (x + 50) // 100 * 100
    return target if target > 0 and abs(target - x) <= NEAR_HUNDRED_GAP else None
