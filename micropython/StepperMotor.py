# 28BYJ-48
from micropython import const

STEPS_PER_REVOLUTION = const(2048)


def stepper_add(x: int, y: int) -> int:
    return (x + y + STEPS_PER_REVOLUTION) % STEPS_PER_REVOLUTION


def stepper_sub(x: int, y: int) -> int:
    return (x - y + STEPS_PER_REVOLUTION) % STEPS_PER_REVOLUTION


def stepper_add_offset(x: int, y: int) -> int:
    return stepper_add(x, y) + (x // STEPS_PER_REVOLUTION) * STEPS_PER_REVOLUTION


def stepper_sub_offset(x: int, y: int) -> int:
    return stepper_sub(x, y) + (x // STEPS_PER_REVOLUTION) * STEPS_PER_REVOLUTION
