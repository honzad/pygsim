from enum import Enum
from dataclasses import dataclass, fields
import pygame


class GShapeType(Enum):
    Square = 0
    Circle = 1


@dataclass
class GShape:
    shape_type: GShapeType
    size: int
    border_size: int
    color: pygame.Color

    def copy(self) -> "GShape":
        clone = GShape(GShapeType.Circle, 10, -1, pygame.Color(0, 0, 0))
        for field in fields(GShape):
            setattr(clone, field.name, getattr(self, field.name))
        return clone
