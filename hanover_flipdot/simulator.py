# /usr/bin/python


class Simulator(object):
    def __init__(self):
        print("\033[2J")

    def __unascii__(self, byte):
        if byte > 0x40:
            return byte - 0x37
        else:
            return byte - 0x30

    def display(self, frame, lines):
        # Parse each column
        for i in range(len(frame) / ((lines * 2))):
            byte = 0
            for j in range(lines):
                b1 = frame[i * ((lines * 2)) + 1 + 2 * j]
                b2 = frame[i * ((lines * 2)) + 0 + 2 * j]
                b1 = self.__unascii__(b1)
                b2 = self.__unascii__(b2)
                byte += b1 << ((j * 8) + 4)
                byte += b2 << (j * 8)
            # Combine the four ASCII bytes into one hex byte
            r = (lines * 8) - 1
            for k in range(r, -1, -1):
                if byte & (1 << (k)):
                    print("\033[43m\033[%d;%dH \033[0m" % ((k + 1), i))
                else:
                    print("\033[100m\033[%d;%dH \033[0m" % ((k + 1), i))
