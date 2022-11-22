from enum import Enum
from dataclasses import dataclass
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
