from dataclasses import dataclass, field


@dataclass
class Score:
    accepted: int
    declined: int
    final: int
    accepted_ratio: float = field(init=False)
    declined_ratio: float = field(init=False)

    def __post_init__(self):
        self.accepted_ratio = round((self.accepted / (self.final)) * 100, 1)
        self.declined_ratio = 100 - self.accepted_ratio
