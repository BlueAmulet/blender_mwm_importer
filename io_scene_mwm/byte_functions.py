#!/usr/bin/env python3
import struct


def read_varint(file):
    value = 0
    shift = 0
    while True:
        byte = file.read(1)[0]
        value |= (byte & 0x7F) << shift
        shift += 7
        if (byte & 0x80) == 0:
            break
    return value


def read_string(file):
    nChars = read_varint(file)
    string = file.read(nChars).decode('utf-8')
    return string


def read_hfloat(file):
    bytes = file.read(2)
    f16 = struct.unpack('h', bytes)[0]
    return f16_to_f32(f16)


def f16_to_f32(float16):
    s = int((float16 >> 15) & 0b1)  # sign
    e = int((float16 >> 10) & 0x0000001f)  # exponent
    f = int(float16 & 0x000003ff)  # fraction

    if e == 0 and f != 0:

        while not (f & 0x00000400):
            f = f << 1
            e -= 1
        e += 1
        f &= ~0x00000400

    if (not (e == 0 and f == 0)) and e != 31:

        e = e + (127 - 15)
        e = e << 23

    elif (e == 31):

        e = 0x7f800000

    if not ((e == 0 or e == 31) and f == 0):
        f = f << 13

    s = (s << 31)

    int_var = int(s | e | f)
    float_var = struct.unpack('f', struct.pack('I', int_var))[0]

    return float_var


def read_long(file):
    s = file.read(4)
    long = struct.unpack("<l", s)[0]
    return long


def read_float(file):
    bytes = file.read(4)
    value = struct.unpack('<f', bytes)[0]
    return value


def read_bool(file):
    byte = file.read(1)
    return struct.unpack('?', byte)[0]
