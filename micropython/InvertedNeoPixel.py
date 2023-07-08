from neopixel import NeoPixel


# invert neopixel data as a logic inverter is used to boost to 5v
class InvertedNeoPixel(NeoPixel):

    def write(self):
        for i in range(len(self.buf)):
            self.buf[i] = ~self.buf[i]
        super().write()
        self.pin.high()
