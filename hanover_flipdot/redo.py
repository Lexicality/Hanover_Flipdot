from bitarray import bitarray
from serial import Serial


class Checkerfield:
    data: bitarray
    rows: int
    columns: int
    address: int
    _serial: Serial

    def __init__(self, port: str, address: int = 0, rows=16, columns=20):
        self.data = bitarray("0" * rows * columns)
        self.rows = rows
        self.columns = columns
        self.address = address
        self._serial = Serial(port, 4800)

    def clear(self) -> None:
        self.data.setall(False)

    def set(self, x: int, y: int, state: bool) -> None:
        """
            Rows 7 and 8 are invisible
        """
        assert x < self.columns
        assert y < self.rows - 2
        if y < 7:
            row = 6 - y
        else:
            # 15 = 7
            # 9 = 13
            row = 22 - y
        col = x * self.rows

        self.data[row + col] = state

    def send(self) -> int:
        return self._serial.write(generate_packet(self.address, self.data))

    def stop(self) -> None:
        self._serial.close()


def generate_packet(address: int, data: bitarray) -> bytearray:
    packet = bytearray(b"\x02" + encode_byte(address + 17))
    packet += encode_byte(len(data) // 8)
    data_bytes = data.tobytes()
    for value in data_bytes:
        packet += encode_byte(value)
    csum = checksum(packet)
    packet += b"\x03" + encode_byte(csum)
    return packet


def encode_byte(value: int) -> bytes:
    """ Protocol encodes each byte as an uppercase, ASCII representation of the
        hex value. So, one input byte becomes two output bytes.
    """
    if value >= 256:
        print("ERROR! ", value)
        assert value < 256
    return "{:02X}".format(value).encode("ascii")


def checksum(data: bytes) -> int:
    csum = sum(data)

    # Start of text (0x02) must be removed,
    # End of text (0x03) must be added
    csum += 1

    # Result must be casted to 8 bits
    csum = csum & 0xFF

    # Checksum is the sum XOR 255 + 1. So, sum of all bytes + checksum
    # is equal to 0 (8 bits)
    csum = (csum ^ 255) + 1

    # Result must be casted to 8 bits
    csum = csum & 0xFF

    return csum
