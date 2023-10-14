# 28BYJ-48
from micropython import const

STEPS_PER_REVOLUTION = const(2038)


def stepper_add(x: int, y: int) -> int:
    return (x + y + STEPS_PER_REVOLUTION) % STEPS_PER_REVOLUTION


def stepper_sub(x: int, y: int) -> int:
    return (x - y + STEPS_PER_REVOLUTION) % STEPS_PER_REVOLUTION
