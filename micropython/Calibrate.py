import time
from math import ceil
from typing import List, Union

from Message import Message
from Panel import Panel
from primary.Display import Display
from StepperMotor import STEPS_PER_REVOLUTION
from Message import _STEPS_PER_LETTER, LETTERS, _letter_position


"""
Split-Flap Display Calibration

This script helps you calculate per-flap mechanical offsets for a split-flap display.

# Background
Each character (e.g., 'A', '3') corresponds to a specific step range on the stepper motor.
However, mechanical variances cause each flap to "tick" into view at slightly different positions.
To correct this, we compute an offset per flap by comparing the actual tick-in position with the theoretical one.

# How It Works
You measure and record:
1. The step number where each flap *starts showing* the letter 'A'
2. The step number where each flap *starts showing* the digit '3'

e.g.
from Calibrate import calibrate, calculate_offsets
step = calibrate(panel, num_elements=24)
step()
# write down position when letter is A

step(1340)
# all letters should show 2
step()
# write down position when letter is 3

We then:
- Compare these with their theoretical tick-in positions:
    - 'A' starts at step 45
    - '3' starts at step 1366
- Compute the per-flap error for both A and 3
- Average them for a robust calibration offset

# Usage Steps
1. Run the `calibrate()` function to manually step your flaps and find:
    - When each flap first shows 'A'
    - When each flap first shows '3'

2. Fill in the `a_steps` and `three_steps` lists below.

3. Run `calculate_offsets()` to generate `display_offsets`.

"""

# Constants based on your system
EXPECTED_TICK_IN_A = _letter_position('A') - _STEPS_PER_LETTER / 2
EXPECTED_TICK_IN_3 = _letter_position('3') - _STEPS_PER_LETTER / 2


def calibrate(panel: Panel, num_elements: int):
    position = 0
    print(f"STEPS_PER_REVOLUTION: {STEPS_PER_REVOLUTION}")
    print(f"STEPS_PER_LETTER: {_STEPS_PER_LETTER}")
    print(f"A: {_letter_position('A')}")
    print(f"3: {_letter_position('3')}")

    def step(new_position: Union[int, None] = None):
        nonlocal position
        if new_position:
            position = new_position
        print(position)
        message = Message(15, [0] * num_elements, [position] * num_elements)

        panel.set_message(message)
        while not panel.is_stopped():
            interval_us = panel.step()
            time.sleep_us(interval_us)

        position = position + 1

    return step


def calculate_offsets():
    a_steps = [
        53, 51, 34, 37, 23, 53, 58, 61, 59, 50, 41, 44,
        37, 45, 61, 27, 31, 17, 67, 45, 39, 39, 43, 46
    ]

    three_steps = [
        1379, 1369, 1354, 1359, 1347, 1366, 1389, 1384, 1374, 1371, 1369, 1361,
        1362, 1369, 1380, 1349, 1344, 1351, 1387, 1363, 1364, 1363, 1369, 1368
    ]

    assert len(a_steps) == len(three_steps), "Mismatch in input lengths."

    offsets = []
    for a, t in zip(a_steps, three_steps):
        offset_a = a - EXPECTED_TICK_IN_A
        offset_3 = t - EXPECTED_TICK_IN_3
        average = round((offset_a + offset_3) / 2)
        offsets.append(average)
    print("display_offsets =", offsets)
