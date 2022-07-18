from dataclasses import dataclass
from models.leaderboard_entry import LeaderboardEntry

@dataclass
class ServerInfo:
    leaderboard: list[LeaderboardEntry]
    ratio_accepted: float
    ratio_declined: float
    total_accepted: int
    total_declined: float
    total: int
