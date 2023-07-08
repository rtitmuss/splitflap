from machine import Pin
from Letter import Letter


class LetterGpio:

    def __init__(self,
                 hall_sensor,
                 motor_a,
                 motor_b,
                 motor_c,
                 motor_d,
                 offset=0,
                 hall_sensor_active=0):
        self.hall_sensor_active = hall_sensor_active
        self.state = Letter(offset=offset)
        self.sensor_pin = Pin(hall_sensor, Pin.IN, Pin.PULL_UP)
        self.motor_pin = list(
            map(lambda x: Pin(x, Pin.OUT, value=0),
                [motor_a, motor_b, motor_c, motor_d]))

    def set_offset(self, offset):
        self.state.set_offset(offset)

    def set_letter(self, letter, rotate_always=None):
        self.state.set_letter(letter, rotate_always)

    def task(self):
        self.state.set_home_pin(
            self.sensor_pin.value() == self.hall_sensor_active)
        self.state.task()

    def step(self):
        motor_state = self.state.get_motor_pins()
        #print('pins {0:04b}'.format(motor_state))
        self.motor_pin[0].value(motor_state & (1 << 0))
        self.motor_pin[1].value(motor_state & (1 << 1))
        self.motor_pin[2].value(motor_state & (1 << 2))
        self.motor_pin[3].value(motor_state & (1 << 3))

    def steps_to_rotate(self):
        return self.state.steps_to_rotate()

    def is_panic(self):
        return self.state.is_panic()

    def is_stopped(self):
        return self.state.is_stopped()

    def get_status(self):
        if self.state.is_panic():
            return 'p'
        if self.state.is_stopped():
            return '_'
        return '|'
