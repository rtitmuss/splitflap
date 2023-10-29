import unittest
from StepperMotor import stepper_add, stepper_sub, stepper_add_offset, stepper_sub_offset


class TestStepperMotor(unittest.TestCase):
    def test_stepper_add(self):
        self.assertEqual(stepper_add(0, 1), 1)
        self.assertEqual(stepper_add(2037, 1), 0)

    def test_stepper_sub(self):
        self.assertEqual(stepper_sub(0, 1), 2037)
        self.assertEqual(stepper_sub(2037, 1), 2036)

    def test_stepper_add_offset(self):
        self.assertEqual(stepper_add_offset(0, 1), 1)
        self.assertEqual(stepper_add_offset(2038, 1), 2039)

    def test_stepper_sub_offset(self):
        self.assertEqual(stepper_sub_offset(0, 1), 2037)
        self.assertEqual(stepper_sub_offset(2038, 1), 2038 + 2037)


if __name__ == '__main__':
    unittest.main()
