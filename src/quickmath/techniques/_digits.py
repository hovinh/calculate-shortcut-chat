"""Digit helpers shared by several techniques."""


def is_nines(x: int) -> bool:
    """True for 9, 99, 999, ..."""
    return x > 0 and set(str(x)) == {"9"}


def is_power_of_10(x: int) -> bool:
    """True for 10, 100, 1000, ..."""
    s = str(x)
    return x >= 10 and s == "1" + "0" * (len(s) - 1)
