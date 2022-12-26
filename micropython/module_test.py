import unittest

from module import Module


class TestModuleMethods(unittest.TestCase):

    def setUp(self):
        self.module = Module()

    def run_task_until_motor_stopped(self,
                                     home_pin_range=range(0, 0),
                                     limit=Module.STEPS_PER_REVOLUTION * 2):
        motor_pins = []
        while len(motor_pins) < limit:
            self.module.set_home_pin(Module.HOME_PIN_ACTIVE if len(
                motor_pins) in home_pin_range else ~Module.HOME_PIN_ACTIVE)
            self.module.task()

            motor_pins.append(self.module.get_motor_pins())
            if motor_pins[-1] == 0:
                return motor_pins

        return motor_pins

    def test_letter_to_position(self):
        self.assertEqual(self.module.letter_to_position(' '), 0 + 23)
        self.assertEqual(self.module.letter_to_position('a'), 23 + 45)
        self.assertEqual(self.module.letter_to_position('!'), 23 + 1857)

    def test_rotate_to_a(self):
        self.module.rotate_to_letter('a')
        motor_pins = self.run_task_until_motor_stopped(
            home_pin_range=range(0, 2))

        # 3 homing steps, 23 half module
        self.assertEqual(len(motor_pins), 3 + 23 + 45)
        self.assertFalse(self.module.is_panic())

    def test_rotate_to_a_then_b(self):
        self.module.rotate_to_letter('a')
        self.run_task_until_motor_stopped(home_pin_range=range(0, 2))

        self.module.rotate_to_letter('b')
        motor_pins = self.run_task_until_motor_stopped()

        self.assertEqual(len(motor_pins), 47)
        self.assertFalse(self.module.is_panic())

    def test_rotate_to_a_then_space(self):
        self.module.rotate_to_letter('a')
        self.run_task_until_motor_stopped(home_pin_range=range(0, 2))

        self.module.rotate_to_letter(' ')
        motor_pins = self.run_task_until_motor_stopped(
            home_pin_range=range(1946, 1971))

        # 3 homing steps
        self.assertEqual(len(motor_pins), 3 + 1992)
        self.assertFalse(self.module.is_panic())

    def test_rotate_to_a_then_a(self):
        self.module.rotate_to_letter('a')
        self.run_task_until_motor_stopped(home_pin_range=range(0, 2))

        self.module.rotate_to_letter('a')
        motor_pins = self.run_task_until_motor_stopped(
            home_pin_range=range(1946, 1971))

        self.assertEqual(len(motor_pins), 2040)
        self.assertFalse(self.module.is_panic())

    def test_stepper_sequence(self):
        self.module.rotate_to_letter('a')
        motor_pins = self.run_task_until_motor_stopped(limit=8)

        self.assertEqual(motor_pins, [6, 12, 9, 3, 6, 12, 9, 3])

    def test_rotate_no_home(self):
        self.module.rotate_to_letter('a')
        motor_pins = self.run_task_until_motor_stopped()

        self.assertNotEqual(len(motor_pins), 23 + 45)
        self.assertTrue(self.module.is_panic())
        self.assertEqual(self.module.get_motor_pins(), 0)

    def test_task_home_pin_stuck(self):
        self.module.rotate_to_letter('!')
        motor_pins = self.run_task_until_motor_stopped(
            home_pin_range=range(0, 100))

        self.assertTrue(self.module.is_panic())
        self.assertEqual(self.module.get_motor_pins(), 0)

    def test_task_home_pin_not_set(self):
        self.assertRaises(ValueError, lambda: self.module.task())


if __name__ == '__main__':
    unittest.main()
