from typing import Dict
from collections import defaultdict

from hanover_flipdot.redo import Checkerfield


def cycle(n: int, limit: int) -> int:
    if n < 0:
        return limit + n
    elif n >= limit:
        return n - limit
    return n


class GOL:
    field: Dict[int, Dict[int, bool]]
    flipdot: Checkerfield
    rows = 14
    cols = 20

    def __init__(self):
        self.flipdot = Checkerfield("COM4")
        self.field = {}
        for x in range(self.cols):
            self.field[x] = {y: False for y in range(self.rows)}

    def set(self, x: int, y: int, state: bool) -> None:
        assert x < self.cols and y < self.rows

        self.field[x][y] = state
        self.flipdot.set(x, y, state)

    def _surround(self, x: int, y: int):
        print("SURROUND FOR", x, y)
        for xx in range(-1, 2):
            for yy in range(-1, 2):
                if xx == 0 and yy == 0:
                    continue
                yield self.field[cycle(x + xx, self.cols)][cycle(y + yy, self.rows)]

    def step(self) -> None:
        for y in range(self.rows):
            for x in range(self.cols):
                n = self.field[x][y]
                w = "X" if n else "O"
                print(w, end="")
            print()

        new = defaultdict(dict)
        for x, ys in self.field.items():
            for y, alive in ys.items():
                n = len(list(filter(None, self._surround(x, y))))
                if n < 2 or n > 3:
                    alive = False
                elif n == 3:
                    alive = True

                new[x][y] = alive

        for x, ys in new.items():
            for y, alive in ys.items():
                self.set(x, y, alive)

        for y in range(self.rows):
            for x in range(self.cols):
                n = self.field[x][y]
                w = "X" if n else "O"
                print(w, end="")
            print()

        self.flipdot.send()

    def stop(self) -> None:
        self.flipdot.stop()
