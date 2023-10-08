import unittest
from Message import Message
from Panel import Panel


class MockElement:
    def __init__(self):
        self.message = None
        self.motor_position = None
        self.stopped = True
        self.step_called = 0

    def set_message(self, message: Message):
        self.message = message

    def get_motor_position(self) -> str:
        return [self.motor_position]

    def is_stopped(self) -> bool:
        return self.stopped

    def step(self):
        self.step_called += 1


class TestPanel(unittest.TestCase):
    def setUp(self):
        self.elementList = [MockElement(), MockElement()]
        self.panel = Panel(self.elementList)
        self.message = Message(rpm=5, element_delay=[], element_position=[])

    def test_frame(self):
        self.assertIsNone(self.elementList[0].message)
        self.assertIsNone(self.elementList[0].message)

        self.panel.set_message(self.message)

        self.assertEqual(self.elementList[0].message, self.message)
        self.assertEqual(self.elementList[0].message, self.message)

    def test_default_rpm(self):
        self.assertEqual(self.panel.step(), 1962)

    def test_default_set_rpm(self):
        self.panel.set_message(self.message)
        self.assertEqual(self.panel.step(), 5888)

    def test_get_motor_position(self):
        self.elementList[0].motor_position = 1
        self.elementList[1].motor_position = 2
        self.assertEqual(self.panel.get_motor_position(), [1, 2])

    def test_is_stopped(self):
        self.elementList[0].stopped = True
        self.elementList[1].stopped = True
        self.assertTrue(self.panel.is_stopped())

    def test_is_not_stopped(self):
        self.elementList[0].stopped = True
        self.elementList[1].stopped = False
        self.assertFalse(self.panel.is_stopped())

    def test_step(self):
        self.panel.step()
        self.assertEqual(self.elementList[0].step_called, 1)
        self.assertEqual(self.elementList[1].step_called, 1)


if __name__ == '__main__':
    unittest.main()
