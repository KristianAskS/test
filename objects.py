from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class Teacher:
    name: str
    img_url: str
    school: str
    local_rating: int = 1500
    rating: int = 1500
    role: Optional[str] = None
    school: Optional[str] = None
    img_path: Optional[str] = None
    predicted_age: Optional[int] = None

    def __post_init__(self):
        self.img_path = f"./images/{self.name}.jpg"

    def __str__(self):
        return str({k: v for k, v in self.__dict__.items() if v is not None})

    def won(self, opponent: Teacher, k: int = 32) -> None:
        self.rating = round(self.rating + k * (1 - self.expected(opponent)))
        opponent.rating = round(opponent.rating + k * (0 - opponent.expected(self)))

    def expected(self, opponent: "Teacher") -> float:
        return 1 / (1 + 10 ** ((opponent.rating - self.rating) / 400))

    def won_local(self, opponent: "Teacher", k: int = 32) -> None:
        self.local_rating = round(self.local_rating + k * (1 - self.expected(opponent)))
        opponent.local_rating = round(
            opponent.local_rating + k * (0 - opponent.expected(self))
        )
