from typing import Dict, Tuple, Optional, List
from itertools import count
from abc import ABC, abstractmethod
from enum import Enum

import pygame
from pygame.surface import Surface

from .drawable import GDrawable
from .color import DefaultColors
from .shape import GShape, GShapeType


class GAlign(Enum):
    NoAlign = 0
    Top = 1
    TopLeft = 2
    TopRight = 3
    Center = 4
    Left = 5
    Right = 6
    Bottom = 7
    BottomLeft = 8
    BottomRight = 9


class GFillDirection(Enum):
    TopLeft = 0
    TopRight = 1
    Left = 2
    Right = 3
    BottomLeft = 4
    BottomRight = 5


class GOverflow(Enum):
    Visible = 0
    Hidden = 1
    # Clip = 2


class GContainerBase(ABC):
    _object_id_counter = count(0)

    def __init__(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        shape: Optional[GShape] = None,
        align: GAlign = GAlign.NoAlign,
        fill_direction: GFillDirection = GFillDirection.TopLeft,
        overflow: GOverflow = GOverflow.Visible,
        padding: int = 5
    ) -> None:
        self._id = next(self._object_id_counter)
        self._objects: Dict[str, GDrawable] = {}
        self._size = size
        self._position = position
        self._shape = self._set_shape(shape)
        self._align = align
        self._fill_direction = fill_direction
        self._overflow = overflow
        self._padding = padding

    def __len__(self):
        return len(self._objects)

    # Properities

    @property
    def id(self) -> int:
        return self._id

    @property
    def size(self) -> Tuple[int, int]:
        return self._position

    @size.setter
    def size(self, s: Tuple[int, int]):
        if (s[0] <= 0) or (s[1] <= 0):
            raise ValueError("Negative or zero values supplied to size")

        self._size = s

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, p: Tuple[int, int]):
        if self._align == GAlign.NoAlign:
            if (p[0] < 0) or (p[1] < 0):
                raise ValueError("Negative values supplied to position")

        self._position = p

    @property
    def shape(self) -> GShape:
        return self._shape

    @shape.setter
    def shape(self, s: GShape) -> None:
        vals = [v.name for v in GShapeType]
        if s.shape_type.name not in vals:
            raise ValueError("Invalid shape type supplied")

        if s.border_size < -1:
            s.border_size = -1

        self._shape = s

    @property
    def align(self) -> GAlign:
        return self._align

    @align.setter
    def align(self, a: GAlign):
        if not isinstance(a, GAlign):
            raise ValueError("Invalid align type supplied")

        if a not in GAlign:
            raise ValueError("Invalid align value supplied")

        self._align = a

    @property
    def fill_direction(self) -> GFillDirection:
        return self._fill_direction

    @fill_direction.setter
    @abstractmethod
    def fill_direction(self, f: GFillDirection):
        pass

    @property
    def overflow(self) -> GOverflow:
        return self._overflow

    @overflow.setter
    def overflow(self, o: GOverflow):
        if not isinstance(o, GOverflow):
            raise ValueError("Invalid overflow type supplied")

        if o not in GOverflow:
            raise ValueError("Invalid overflow value supplied")

        self._overflow = o

    @property
    def padding(self) -> int:
        return self._padding

    @padding.setter
    def padding(self, p: int):
        if p < 0:
            raise ValueError("Negative padding supplied")

        self._padding = p

    # Main functionality

    def enter(self, obj: GDrawable):
        if f"{id(obj)}" in self._objects:
            raise Exception("Object already in this container")
        self._objects[f"{id(obj)}"] = obj

    def leave(self, obj: GDrawable):
        if f"{id(obj)}" not in self._objects:
            raise Exception("Object not in this container")
        del self._objects[f"{id(obj)}"]

    # Helpers

    def _set_shape(self, s: Optional[GShape]) -> GShape:
        if s is None:
            return GShape(GShapeType.Square, 10, 2, DefaultColors.White._get_color)
        return s


class GContainerRow(GContainerBase, GDrawable):
    @GContainerBase.fill_direction.setter
    def fill_direction(self, f: GFillDirection):
        if not isinstance(f, GFillDirection):
            raise ValueError("Invalid fill direction type supplied")

        if f not in GFillDirection:
            raise ValueError("Invalid fill direction value supplied")

        n_f = f

        if (f == GFillDirection.TopLeft) or (f == GFillDirection.BottomLeft):
            n_f = GFillDirection.Left
        elif (f == GFillDirection.TopRight) or (f == GFillDirection.BottomRight):
            n_f = GFillDirection.Right
        else:
            n_f = f

        self._fill_direction = n_f

    def draw(self, screen: Surface) -> None:
        x, y = self._position
        width, height = self._size

        if self._shape.shape_type == GShapeType.Square:
            pygame.draw.rect(
                screen,
                DefaultColors.White._get_color,
                pygame.Rect(x, y, width, height),
                self.shape.border_size,
            )
        else:
            pygame.draw.ellipse(
                screen,
                DefaultColors.White._get_color,
                pygame.Rect(x, y, width, height),
                self.shape.border_size,
            )

        if len(self._objects) == 0:
            return

        obj_entries: List[GDrawable] = list(self._objects.values())
        biggest_size = list(map(lambda o: o.shape.size, obj_entries))
        biggest_size.sort(reverse=True)
        biggest_size = biggest_size[0]

        spacer = 5  # TODO: Replace for global

        for i, o in enumerate(obj_entries):
            size = o.shape.size
            x_l = x + (i * biggest_size) + (i * spacer) + self._padding
            x_r = y + self._padding

            if self._overflow == GOverflow.Hidden:
                if x_l > self._size[0]:
                    continue

            if o.shape.shape_type == GShapeType.Square:
                pygame.draw.rect(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, x_r, size, size),
                )
            else:
                pygame.draw.ellipse(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, x_r, size, size),
                )


class GContainerColumn(GContainerBase, GDrawable):
    @GContainerBase.fill_direction.setter
    def fill_direction(self, f: GFillDirection):
        if not isinstance(f, GFillDirection):
            raise ValueError("Invalid fill direction type supplied")

        if f not in GFillDirection:
            raise ValueError("Invalid fill direction value supplied")

        n_f = f

        if (f == GFillDirection.TopLeft) or (f == GFillDirection.BottomLeft):
            n_f = GFillDirection.Left
        elif (f == GFillDirection.TopRight) or (f == GFillDirection.BottomRight):
            n_f = GFillDirection.Right
        else:
            n_f = f

        self._fill_direction = n_f

    def draw(self, screen: Surface) -> None:
        pass


class GcontainerGrid(GContainerBase, GDrawable):
    @GContainerBase.fill_direction.setter
    def fill_direction(self, f: GFillDirection):
        if not isinstance(f, GFillDirection):
            raise ValueError("Invalid fill direction type supplied")

        if f not in GFillDirection:
            raise ValueError("Invalid fill direction value supplied")

        if (f == GFillDirection.Left) or (f == GFillDirection.Right):
            raise ValueError("Invalid align for grid object, choose Top_ or Bottom_")

        self._fill_direction = f

    def draw(self, screen: Surface) -> None:
        pass
