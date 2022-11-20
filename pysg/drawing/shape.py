from enum import Enum
from dataclasses import dataclass

class GShapeType(Enum):
	Square = 0
	Circle = 1

@dataclass
class GShape():
	shape_type: GShapeType
	size: int

