import math


class Module:

    STEPS_PER_REVOLUTION = 2038  # 28BYJ-48

    LETTERS = ' ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789:.-?!$&#'

    STEPS_PER_LETTER = STEPS_PER_REVOLUTION / len(LETTERS)

    MAX_HOME_STEPS = STEPS_PER_LETTER * 2

    MAX_NON_HOME_STEPS = STEPS_PER_REVOLUTION * 1.1

    MOT_PHASE_A = 0b00001000
    MOT_PHASE_B = 0b00000100
    MOT_PHASE_C = 0b00000010
    MOT_PHASE_D = 0b00000001

    STEP_PATTERN = [
        MOT_PHASE_A | MOT_PHASE_B, MOT_PHASE_B | MOT_PHASE_C,
        MOT_PHASE_C | MOT_PHASE_D, MOT_PHASE_D | MOT_PHASE_A
    ]

    def __init__(self, offset=0, hall_sensor_active=1):
        self.offset = offset
        self.hall_sensor_active = hall_sensor_active

        # True if error is detected
        self.panic_error = False

        # stepper motor pins
        self.motor_pins = 0
        self.force_rotation = False

        # home pin (hall effect sensor)
        self.home_pin = None

        # panic if count home steps exceeds MAX_HOME_STEPS
        self.count_home_steps = 0
        self.count_non_home_steps = 0

        # motor and target letter positions
        self.motor_position = -Module.STEPS_PER_REVOLUTION
        self.letter_position = -Module.STEPS_PER_REVOLUTION

        # stats
        self.max_count_home_steps = 0
        self.max_count_non_home_steps = 0
        self.total_letters = 0
        self.total_steps = 0

    def letter_to_position(self, letter):
        index = Module.LETTERS.find(letter.upper())
        if index == -1:
            raise ValueError('invalid letter')

        return math.ceil((index + 0.5) * Module.STEPS_PER_LETTER)

    def rotate_to_letter(self, letter):
        self.letter_position = (self.letter_to_position(letter) +
                                self.offset) % Module.STEPS_PER_REVOLUTION
        self.force_rotation = True
        self.total_letters += 1

    def set_home_pin(self, home_pin):
        self.home_pin = home_pin

    def get_motor_pins(self):
        return self.motor_pins

    def is_stopped(self):
        return self.motor_pins == 0

    def steps_to_rotate(self):
        if self.panic_error:
            return 0

        if self.motor_position == self.letter_position and self.force_rotation:
            return Module.STEPS_PER_REVOLUTION
        if self.motor_position <= self.letter_position:
            return self.letter_position - self.motor_position
        else:
            return Module.STEPS_PER_REVOLUTION - self.motor_position + self.letter_position

    def is_panic(self):
        return self.panic_error

    def panic(self, error):
        self.motor_pins = 0
        self.panic_error = error
        print('panic: {}'.format(error))
        self.stats()

    def stats(self):
        print('max_count_home_steps: {}'.format(self.max_count_home_steps))
        print('max_count_non_home_steps: {}'.format(
            self.max_count_non_home_steps))
        print('total_letters: {}'.format(self.total_letters))
        print('total_steps: {}'.format(self.total_steps))

    def task(self):
        if self.home_pin == None:
            raise ValueError('home_pin not set')

        if self.motor_pins:
            if self.home_pin == self.hall_sensor_active:
                self.count_home_steps += 1
                self.max_count_home_steps = max(self.max_count_home_steps,
                                                self.count_home_steps)

                if self.count_home_steps > Module.MAX_HOME_STEPS:
                    self.panic('dwell home')
            elif self.count_home_steps > 0:
                # falling edge, found home position
                self.count_home_steps = 0
                self.count_non_home_steps = 0
                self.motor_position = 0
            else:
                self.count_non_home_steps += 1
                self.max_count_non_home_steps = max(
                    self.max_count_non_home_steps, self.count_non_home_steps)

                if self.count_non_home_steps > Module.MAX_NON_HOME_STEPS:
                    self.panic('missed home')

        if self.panic_error:
            return

        if self.motor_position != self.letter_position or self.force_rotation:
            self.motor_pins = Module.STEP_PATTERN[self.motor_position %
                                                  len(Module.STEP_PATTERN)]
            self.force_rotation = False
            self.motor_position += 1
            self.total_steps += 1
        else:
            self.motor_pins = 0

        self.home_pin = None
