import array

# crc16 from https://forum.micropython.org/viewtopic.php?t=12837&p=69890
PRESET = const(0xFFFF)
POLYNOMIAL = const(0xA001)  # bit reverse of 0x8005


def __initial(c):
    crc = 0
    for j in range(8):
        if (crc ^ c) & 0x1:
            crc = (crc >> 1) ^ POLYNOMIAL
        else:
            crc = crc >> 1
        c = c >> 1
    return crc


__tab = array.array('H', [__initial(i) for i in range(256)])


def crc16(str):
    crc = PRESET
    for c in str:
        crc = (crc >> 8) ^ __tab[(crc ^ c) & 0xff]
    return crc
