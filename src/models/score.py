from dataclasses import dataclass, field


@dataclass
class Score:
    accepted: int
    declined: int
    final: int
    ratio: float = field(init=False)

    def __postinit__(self):
        self.ratio = round((self.accepted / (self.final)) * 100, 1)