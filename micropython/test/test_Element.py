import unittest

from Element import Element
from Message import Message
from StepperMotor import STEPS_PER_REVOLUTION


class TestModuleMethods(unittest.TestCase):

    def setUp(self):
        self.element = Element()

    def step_until_motor_stopped(self,
                                 home_pin_range=range(0, 0),
                                 limit=STEPS_PER_REVOLUTION * 2):
        motor_pins_list = []
        while len(motor_pins_list) < limit:
            self.element.set_home_pin(len(motor_pins_list) in home_pin_range)
            self.element.step()

            motor_pins_list.append(self.element.get_motor_pins())
            if self.element.is_stopped():
                return motor_pins_list

        return motor_pins_list

    def test_empty_message(self):
        self.element.set_message(Message(15, [], []))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.assertEqual(len(motor_pins), 1)
        self.assertEqual(self.element.get_motor_position(), [-2038])

    def test_is_not_stopped(self):
        self.element.set_message(Message(15, [0], [100]))

        self.assertEqual(self.element.is_stopped(), False)

    def test_rotate_to_100(self):
        self.element.set_message(Message(15, [0], [100]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.assertEqual(len(motor_pins), 2 + 100)  # 2 homing steps
        self.assertEqual(self.element.get_motor_position(), [100])

    def test_rotate_to_100_with_delay(self):
        self.element.set_message(Message(15, [100], [100]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(100, 102))

        self.assertEqual(len(motor_pins), 2 + 100 + 100)  # 2 homing steps
        self.assertEqual(self.element.get_motor_position(), [100])

    def test_rotate_to_100_then_200(self):
        self.element.set_message(Message(15, [0], [100]))
        self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.element.set_message(Message(15, [0], [200]))
        motor_pins = self.step_until_motor_stopped()

        self.assertEqual(len(motor_pins), 100)
        self.assertEqual(self.element.get_motor_position(), [200])

    def test_rotate_to_200_then_100(self):
        self.element.set_message(Message(15, [0], [200]))
        self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.element.set_message(Message(15, [0], [100]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(300, 302))

        self.assertEqual(len(motor_pins), 402)
        self.assertEqual(self.element.get_motor_position(), [100])

    def test_rotate_to_100_then_100(self):
        self.element.set_message(Message(15, [0], [100]))
        self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.element.set_message(Message(15, [0], [100]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(300, 302))

        self.assertEqual(len(motor_pins), 1)  # 1 motor stopped
        self.assertEqual(self.element.get_motor_position(), [100])

    def test_rotate_to_100_then_100_with_rotation(self):
        self.element.set_message(Message(15, [0], [100]))
        self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.element.set_message(Message(15, [0], [100 + STEPS_PER_REVOLUTION]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(300, 302))

        self.assertEqual(len(motor_pins), 402)
        self.assertEqual(self.element.get_motor_position(), [100])

    def test_stepper_sequence(self):
        self.element.set_message(Message(15, [0], [100]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(0, 2))

        self.assertEqual(motor_pins[:8], [3, 9, 12, 6, 3, 9, 12, 6])

    def test_rotate_no_home(self):
        self.element.set_message(Message(15, [0], [1000]))
        motor_pins = self.step_until_motor_stopped()

        self.assertTrue(len(motor_pins) > 0)
        self.assertTrue(self.element.is_stopped())
        self.assertEqual(self.element.get_motor_pins(), 0)
        self.assertEqual(self.element.get_motor_position(), [-1])

    def test_task_home_pin_stuck(self):
        self.element.set_message(Message(15, [0], [1000]))
        motor_pins = self.step_until_motor_stopped(home_pin_range=range(0, 500))

        self.assertTrue(len(motor_pins) > 0)
        self.assertTrue(self.element.is_stopped())
        self.assertEqual(self.element.get_motor_pins(), 0)
        self.assertEqual(self.element.get_motor_position(), [-1])

    def test_task_home_pin_not_set(self):
        self.assertRaises(ValueError, lambda: self.element.step())


if __name__ == '__main__':
    unittest.main()
