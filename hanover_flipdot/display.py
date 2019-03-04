import serial
import time
import sys
from .simulator import Simulator

def print_hex(data):
    hex_bytes = []
    for byte in data:
        hex_bytes.append("0x{:02x}".format(byte))
    print("[", " ".join(hex_bytes), "]")


class Display(object):
    '''
    Driver for the Hanover display.
    Currently, this driver only works with resolution of 128x16, at address 1
    This limitation must be changed in a future version.
    '''
    def __init__(self, serial, address, columns, lines, font, debug=False, simulator=False):
        self.port = serial

        if lines % 8:
            lines = lines + (8-(lines % 8))
        print("Lines", lines)

        self.columns = columns - 1

        self.byte_per_column = lines // 8
        self.buf_size = columns

        assert self.buf_size < 255

        res1, res2 = self.byte_to_ascii(self.buf_size * 2)

        address += 16

        add1, add2 = self.byte_to_ascii(address)
        # Header part
        self.header = [0x2, add1, add2, res1, res2]
        # Footer part
        self.footer = [0x3, 0x00, 0x00]
        # Data buffer initialized to 0
        self.buf = [0] * self.buf_size
        # Fonts object
        self.font = font
        # Debug flag
        self.DEBUG = debug
        # Simulator switch
        self.SIMULATOR = simulator
        if self.SIMULATOR:
            self.sim = Simulator()
        self.connect()

    def connect(self):
        '''
        Connect to the serial device
        '''
        if not self.SIMULATOR:
            try:
                self.ser = serial.Serial(port=self.port, baudrate=4800)
            except:
                print(sys.exc_info())
                print("Error opening serial port")
                self.ser = None
            if self.DEBUG:
                print("Serial port:", self.ser)
        elif self.DEBUG:
            print("Simulator instance", self.sim)

    def set_font(self, font):
        '''
        Set a font
        '''
        self.font = font

    def erase_all(self):
        '''
        Erase all the screen
        '''
        if self.DEBUG:
            print("Erasing all")
        for i in range(len(self.buf)):
            self.buf[i] = 0

    def write_text(self, text, line=0, column=0):
        '''
        Write text on the first line
        '''
        if self.DEBUG:
            print("First line text :  ", text)

        # Detect the size
        mask = 0xff
        for byte in self.font[0x31]:
            if byte.bit_length() >= 9:
                mask = 0xffff
                break

        # Parse all the characters
        for char in text:
            # Fill the buffer
            for i in range(len(self.font[0])):
                if column > self.columns:
                    return 0
                self.buf[column] &= ~((mask << line) & ((1 << self.byte_per_column*8)-1))
                self.buf[column] |= ((self.font[ord(char)][i])<<line) &  (1 << (self.byte_per_column * 8)) - 1
                column += 1

    def byte_to_ascii(self, byte):
        '''
        Convert a byte to its ascii reprensentation.
        The transmission represent each byte by their ASCII representation.
        For example, 0x67 is reprensented by 0x36 0x37 (ascii 6 and ascii 7)
        This is not an elegant way to convert the data, and this function must
        be refactored
        '''
        b1 = 0
        b2 = 0
        b1 = byte >> 4
        if b1 > 9:
            b1 += 0x37
        else:
            b1 += 0x30

        b2 = byte % 16
        if b2 > 9:
            b2 += 0x37
        else:
            b2 += 0x30
        return (b1, b2)

    def __checksum__(self, dsum):
        '''
        Compute the checksum of the data frame
        '''
        # Sum all bytes of the header and the buffer
        csum = sum(self.header)
        csum += dsum

        # Start of text (0x02) must be removed,
        # End of text (0x03) must be added
        csum += 1

        # Result must be casted to 8 bits
        csum = csum & 0xFF

        # Checkcsum is the csum XOR 255 + 1. So, csum of all bytes + checkcsum
        # is equal to 0 (8 bits)
        crc = (csum ^ 255) + 1

        # Transfor the checkcsum in ascii
        crc1, crc2 = self.byte_to_ascii(crc)

        # Add the checkcsum on the footer
        self.footer[1] = crc1
        self.footer[2] = crc2

        if self.DEBUG:
            print("SUM : %d, CRC : %d, SUM + CRC : %d" % (csum, crc, csum+crc))

    def send(self):
        '''
        Send the frame via the serial port
        :return: Return 0 on success, -1 on errors
        '''

        if self.DEBUG:
            print_hex(self.header)
            print_hex(self.buf)
        crc = 0
        # Send the header
        self.ser.write(bytes(self.header))
        # Send the data
        for col in self.buf:
            for i in range(self.byte_per_column):
                b1, b2 = self.byte_to_ascii((col >> (8*i) & 0xFF))
                crc += b1
                crc += b2
                self.ser.write(bytes([b1, b2]))

        # Compute the checksum
        self.__checksum__(crc)

        if self.DEBUG:
            print_hex(self.footer)
        # Send the footer
        self.ser.write(bytes(self.footer))

        return 0
