from typing import Optional
from abc import ABC, abstractmethod

from pygame.surface import Surface

from .shape import GShape, GShapeType
from .color import DefaultColors


class GDrawable(ABC):
    """Base class providing drawable functions to simulation classes"""

    def __init__(self, shape: Optional[GShape] = None) -> None:
        self._shape = self._set_shape(shape)

    def __call__(self, screen: Surface, dt: float) -> None:
        """Calls the drawing function when class called as function

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        self.draw(screen, dt)

    # Properities

    @property
    def shape(self) -> GShape:
        return self._shape

    @shape.setter
    def shape(self, s: GShape) -> None:
        self._shape = self._set_shape(s)

    @property
    def Shape(self) -> Optional[GShape]:
        """Default shape for this instance. (can be overidden)"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # Shape = GShape(GShapeType.Circle, 10)  # type: ignore
        return None

    # Overidable

    @abstractmethod
    def draw(self, screen: Surface, dt: float) -> None:
        """Drawing function, can be overidden.

        This draw call function is called `fps` times per second as \
            specified in :class:`~pysg.environment.GEnvironment` .

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        pass

    # Helpers

    def _set_shape(self, shape: Optional[GShape]) -> GShape:
        target_shape = None

        if self.Shape is not None:
            target_shape = self.Shape

        if shape is not None:
            target_shape = shape

        if target_shape is None:
            target_shape = GShape(
                GShapeType.Circle, 10, -1, DefaultColors.White._get_color
            )

        if target_shape.size <= 0:
            raise ValueError("Zero or negative size of a shape supplied")

        vals = [v.name for v in GShapeType]
        if target_shape.shape_type.name not in vals:
            raise ValueError("Invalid shape type supplied")

        return target_shape.copy()
