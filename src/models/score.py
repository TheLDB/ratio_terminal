from dataclasses import dataclass, field


@dataclass
class Score:
    accepted: int
    declined: int
    final: int = field(init=False)
    accepted_ratio: float = field(init=False, default=0.0)
    declined_ratio: float = field(init=False, default=0.0)

    def __post_init__(self):
        self.final = self.accepted - self.declined
        total = self.accepted + self.declined

        if self.declined is 0:
            # Prevent a ZeroDivisionError
            return
        
        self.accepted_ratio = round((self.accepted / total) * 100, 1)
        self.declined_ratio = round(100 - self.accepted_ratio, 1)
