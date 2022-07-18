from dataclasses import dataclass


@dataclass
class LeaderboardEntry:
    id: int | None
    user_id: str
    server_id: str | None = None
    score: int = 0
    accepted_score: int = 0
    declined_score: int = 0