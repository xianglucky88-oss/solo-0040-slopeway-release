from dataclasses import dataclass

FORWARD = 'ab'
BACKWARD = 'ba'
BOTH = 'both'
DIRECTIONS = (FORWARD, BACKWARD, BOTH)


def directions(direction):
    return (FORWARD, BACKWARD) if direction == BOTH else (direction,)


@dataclass(frozen=True)
class Arc:
    segment: str
    direction: str
    start: str
    end: str
    length_m: int

    @property
    def id(self):
        return f'{self.segment}:{self.direction}'


def expand(segments):
    for segment in segments:
        for direction in directions(segment['direction']):
            start, end = (segment['a'], segment['b']) if direction == FORWARD else (segment['b'], segment['a'])
            yield Arc(segment['id'], direction, start, end, segment['length_m'])
