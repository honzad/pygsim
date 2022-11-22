from typing import Optional
from abc import ABC, abstractmethod

import pygame
from pygame.surface import Surface

from .shape import GShape, GShapeType


class GDrawable(ABC):
    """Base class providing drawable functions to simulation classes"""

    def __init__(self, shape: Optional[GShape] = None) -> None:
        self._shape = self._set_shape(shape)

    @property
    def shape(self) -> GShape:
        return self._shape

    @shape.setter
    def shape(self, s: GShape) -> None:
        if s.size <= 0:
            raise ValueError("Zero or negative size of a shape supplied")

        vals = [v.name for v in GShapeType]
        if s.shape_type.name not in vals:
            raise ValueError("Invalid shape type supplied")

        self._shape = s

    @property
    def Shape(self) -> Optional[GShape]:
        """Default shape for this instance. (can be overidden)"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # Shape = GShape(GShapeType.Circle, 10)  # type: ignore
        return None

    def __call__(self, screen: Surface) -> None:
        """Calls the drawing function when class called as function

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        self.draw(screen)

    @abstractmethod
    def draw(self, screen: Surface) -> None:
        """Drawing function, can be overidden.

        This draw call function is called `fps` times per second as \
            specified in :class:`~pysg.environment.GEnvironment` .

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        pass

    def _set_shape(self, shape: Optional[GShape]) -> GShape:
        if shape is None:
            if self.Shape is None:
                return GShape(GShapeType.Circle, 10, -1, pygame.Color(255, 255, 255))
            return self.Shape
        return shape
