import unittest
from StepperMotor import stepper_add, stepper_sub


class TestStepperMotor(unittest.TestCase):
    def test_stepper_add(self):
        self.assertEqual(stepper_add(0, 1), 1)
        self.assertEqual(stepper_add(2037, 1), 0)

    def test_stepper_sub(self):
        self.assertEqual(stepper_sub(0, 1), 2037)
        self.assertEqual(stepper_sub(2037, 1), 2036)


if __name__ == '__main__':
    unittest.main()
