from dataclasses import dataclass, field


@dataclass
class Score:
    accepted: int
    declined: int
    final: int = field(init=False)
    accepted_ratio: float = field(init=False)
    declined_ratio: float = field(init=False)

    def __post_init__(self):
        self.final = self.accepted - self.declined
        total = self.accepted + self.declined
        self.accepted_ratio = round((self.accepted / total) * 100, 1)
        self.declined_ratio = round(100 - self.accepted_ratio, 1)
