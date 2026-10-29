from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Memory:
    id: str
    text: str
    created_at: datetime
    score: float | None = None
