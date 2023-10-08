from machine import Pin

from Element import Element
from Message import Message


class ElementGpio:

    def __init__(self,
                 hall_sensor,
                 motor_a,
                 motor_b,
                 motor_c,
                 motor_d,
                 hall_sensor_active=0):
        self.element = Element()
        self.hall_sensor_active = hall_sensor_active
        self.sensor_pin = Pin(hall_sensor, Pin.IN, Pin.PULL_UP)
        self.motor_pin = list(
            map(lambda x: Pin(x, Pin.OUT, value=0),
                [motor_a, motor_b, motor_c, motor_d]))

    def set_message(self, message: Message):
        self.element.set_message(message)

    def get_motor_position(self):
        return self.element.get_motor_position()

    def is_stopped(self):
        return self.element.is_stopped()

    def step(self):
        self.element.set_home_pin(
            self.sensor_pin.value() == self.hall_sensor_active)

        self.element.step()

        motor_state = self.element.get_motor_pins()
        self.motor_pin[0].value(motor_state & (1 << 0))
        self.motor_pin[1].value(motor_state & (1 << 1))
        self.motor_pin[2].value(motor_state & (1 << 2))
        self.motor_pin[3].value(motor_state & (1 << 3))
