from typing import Dict, Tuple, Optional, List
from itertools import count
from abc import ABC, abstractmethod
from enum import Enum
import math

import pygame
from pygame.surface import Surface

from .drawable import GDrawable
from .color import DefaultColors
from .shape import GShape, GShapeType
from ..util import array_chunks


class GAlign(Enum):
    """Object alignment"""

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


def get_align_position(
    screen: pygame.surface.Surface,
    rect: pygame.rect.Rect,
    position: Tuple[int, int],
    align: GAlign,
):
    w, h = screen.get_size()

    if align == GAlign.NoAlign:
        rect.x = position[0]
        rect.y = position[1]
    elif align == GAlign.Top:
        rect.x = int((w / 2) - rect.w / 2) + position[0]
        rect.y = position[1]
    elif align == GAlign.TopLeft:
        rect.x = position[0]
        rect.y = position[1]
    elif align == GAlign.TopRight:
        rect.x = int(w - rect.w) + position[0]
        rect.y = position[1]
    elif align == GAlign.Center:
        rect.x = int((w / 2) - rect.w / 2) + position[0]
        rect.y = int((h / 2) - rect.h / 2) + position[1]
    elif align == GAlign.Left:
        rect.x = position[0]
        rect.y = int((h / 2) - rect.h / 2) + position[1]
    elif align == GAlign.Right:
        rect.x = int(w - rect.w) + position[0]
        rect.y = int((h / 2) - rect.h / 2) + position[1]
    elif align == GAlign.Bottom:
        rect.x = int((w / 2) - rect.w / 2) + position[0]
        rect.y = int(h - rect.h) + position[1]
    elif align == GAlign.BottomLeft:
        rect.x = position[0]
        rect.y = int(h - rect.h) + position[1]
    elif align == GAlign.BottomRight:
        rect.x = int(w - rect.w) + position[0]
        rect.y = int(h - rect.h) + position[1]

    return rect


class GFillDirection(Enum):
    """Container item fill direction"""

    TopLeft = 0
    TopRight = 1
    Left = 2
    Right = 3
    BottomLeft = 4
    BottomRight = 5


class GOverflow(Enum):
    """Container overflow settings"""

    Visible = 0
    Hidden = 1
    # Clip = 2


class GContainerBase(ABC):
    """Base class for Containers

    :param size: Container size
    :type size: Tuple[int, int]
    :param position: Container position
    :type position: Tuple[int, int]
    :param shape: Default container background shape, defaults to None
    :type shape: Optional[GShape], optional
    :param align: Container window aligment, defaults to GAlign.NoAlign
    :type align: GAlign, optional
    :param fill_direction: Container item fill direction, defaults \
        to GFillDirection.TopLeft
    :type fill_direction: GFillDirection, optional
    :param overflow: Container overflow settings, defaults to GOverflow.Visible
    :type overflow: GOverflow, optional
    :param padding: Container inner padding, defaults to 5
    :type padding: int, optional
    :param spacing: Container item spacing, defaults to 5
    :type spacing: int, optional
    :param reverse: Container item order, defaults to False
    :type reverse: bool, optional
    """

    _object_id_counter = count(0)

    def __init__(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        shape: Optional[GShape] = None,
        align: GAlign = GAlign.NoAlign,
        fill_direction: GFillDirection = GFillDirection.TopLeft,
        overflow: GOverflow = GOverflow.Visible,
        padding: int = 5,
        spacing: int = 5,
        reverse: bool = False,
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
        self._spacing = spacing
        self._max_object_size = 0
        self._reverse = reverse

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

    @property
    def spacing(self) -> int:
        return self._spacing

    @spacing.setter
    def spacing(self, s: int):
        if s < 0:
            raise ValueError("Negative spacing supplied")

        self._spacing = s

    @property
    def reverse(self) -> bool:
        return self.reverse

    @reverse.setter
    def reverse(self, r: bool):
        if not isinstance(r, bool):
            raise ValueError("Invalid reverse type supplied")

        self._reverse = r

    # Main functionality

    def enter(self, obj: GDrawable):
        """Add object to this container

        :param obj: Drawable object
        :type obj: GDrawable
        :raises Exception: if object is already in this container
        """
        if f"{id(obj)}" in self._objects:
            raise Exception("Object already in this container")
        self._objects[f"{id(obj)}"] = obj
        self._max_object_size = self._set_max_object_size()

    def leave(self, obj: GDrawable):
        """Remove object from this container

        :param obj: Drawable object
        :type obj: GDrawable
        :raises Exception: if object is not in this container
        """
        if f"{id(obj)}" not in self._objects:
            raise Exception("Object not in this container")
        del self._objects[f"{id(obj)}"]
        self._max_object_size = self._set_max_object_size()

    # Helpers

    def _set_shape(self, s: Optional[GShape]) -> GShape:
        if s is None:
            return GShape(GShapeType.Square, 10, 2, DefaultColors.White._get_color)
        return s

    def _set_max_object_size(self) -> int:
        obj_entries: List[GDrawable] = list(self._objects.values())
        if len(obj_entries) == 0:
            return 0
        biggest_size = list(map(lambda o: o.shape.size, obj_entries))
        biggest_size.sort(reverse=True)
        return biggest_size[0]


class GContainerRow(GContainerBase, GDrawable):
    def __init__(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        shape: Optional[GShape] = None,
        align: GAlign = GAlign.NoAlign,
        fill_direction: GFillDirection = GFillDirection.TopLeft,
        overflow: GOverflow = GOverflow.Visible,
        padding: int = 5,
        spacing: int = 5,
        reverse: bool = False,
    ) -> None:
        super().__init__(
            size,
            position,
            shape,
            align,
            fill_direction,
            overflow,
            padding,
            spacing,
            reverse,
        )

        self._font = pygame.font.Font(None, 20)

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

    def draw(self, screen: Surface, dt: float) -> None:
        x_pos, y_pos = self._position
        width, height = self._size

        bg_rect = pygame.Rect(x_pos, y_pos, width, height)

        position_rect = get_align_position(screen, bg_rect, self._position, self._align)

        x = position_rect.x
        y = position_rect.y

        if self._shape.shape_type == GShapeType.Square:
            pygame.draw.rect(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )
        else:
            pygame.draw.ellipse(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )

        if len(self._objects) == 0:
            return

        obj_entries: List[GDrawable] = list(self._objects.values())

        if self._reverse:
            obj_entries.reverse()

        for i, o in enumerate(obj_entries):
            size = o.shape.size
            x_l = (
                (x + (i * self._max_object_size) + (i * self._spacing) + self._padding)
                if self._fill_direction == GFillDirection.Left
                else (
                    (x + width)
                    - (i * self._max_object_size)
                    - (i * self._spacing)
                    - self._padding
                    - self._max_object_size
                )
            )
            y_l = y + self._padding

            if self._overflow == GOverflow.Hidden:
                if self._fill_direction == GFillDirection.Right:
                    if x_l < x:
                        continue
                else:
                    if x_l + self._max_object_size > x + width:
                        continue

            f_rect = (
                pygame.draw.rect(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, y_l, size, size),
                )
                if o.shape.shape_type == GShapeType.Square
                else pygame.draw.ellipse(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, y_l, size, size),
                )
            )

            text_surface = self._font.render(f"{o.id}", 1, (0, 0, 0))  # type: ignore
            screen.blit(
                text_surface,
                (
                    f_rect.center[0] - (self._max_object_size / 4),
                    f_rect.center[1] - (self._max_object_size / 4),
                ),
            )


class GContainerColumn(GContainerBase, GDrawable):
    def __init__(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        shape: Optional[GShape] = None,
        align: GAlign = GAlign.NoAlign,
        fill_direction: GFillDirection = GFillDirection.TopLeft,
        overflow: GOverflow = GOverflow.Visible,
        padding: int = 5,
        spacing: int = 5,
        reverse: bool = False,
    ) -> None:
        super().__init__(
            size,
            position,
            shape,
            align,
            fill_direction,
            overflow,
            padding,
            spacing,
            reverse,
        )
        self._font = pygame.font.Font(None, 20)

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

    def draw(self, screen: Surface, dt: float) -> None:
        x_pos, y_pos = self._position
        width, height = self._size

        bg_rect = pygame.Rect(x_pos, y_pos, width, height)

        position_rect = get_align_position(screen, bg_rect, self._position, self._align)

        x = position_rect.x
        y = position_rect.y

        if self._shape.shape_type == GShapeType.Square:
            pygame.draw.rect(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )
        else:
            pygame.draw.ellipse(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )

        if len(self._objects) == 0:
            return

        obj_entries: List[GDrawable] = list(self._objects.values())

        if self._reverse:
            obj_entries.reverse()

        for i, o in enumerate(obj_entries):
            size = o.shape.size
            x_l = x + self._padding
            y_l = (
                (y + (i * self._max_object_size) + (i * self._spacing) + self._padding)
                if self._fill_direction == GFillDirection.Left
                else (
                    (y + height)
                    - (i * self._max_object_size)
                    - (i * self._spacing)
                    - self._padding
                    - self._max_object_size
                )
            )

            if self._overflow == GOverflow.Hidden:
                if self._fill_direction == GFillDirection.Right:
                    if y_l < y:
                        continue
                else:
                    if y_l + self._max_object_size > y + height:
                        continue

            f_rect = (
                pygame.draw.rect(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, y_l, size, size),
                )
                if o.shape.shape_type == GShapeType.Square
                else pygame.draw.ellipse(
                    screen,
                    o.shape.color,
                    pygame.Rect(x_l, y_l, size, size),
                )
            )

            text_surface = self._font.render(f"{o.id}", 1, (0, 0, 0))  # type: ignore
            screen.blit(
                text_surface,
                (
                    f_rect.center[0] - (self._max_object_size / 4),
                    f_rect.center[1] - (self._max_object_size / 4),
                ),
            )


class GcontainerGrid(GContainerBase, GDrawable):
    def __init__(
        self,
        size: Tuple[int, int],
        position: Tuple[int, int],
        shape: Optional[GShape] = None,
        align: GAlign = GAlign.NoAlign,
        fill_direction: GFillDirection = GFillDirection.TopLeft,
        overflow: GOverflow = GOverflow.Visible,
        padding: int = 5,
        spacing: int = 5,
        reverse: bool = False,
    ) -> None:
        super().__init__(
            size,
            position,
            shape,
            align,
            fill_direction,
            overflow,
            padding,
            spacing,
            reverse,
        )
        self._font = pygame.font.Font(None, 20)

    @GContainerBase.fill_direction.setter
    def fill_direction(self, f: GFillDirection):
        if not isinstance(f, GFillDirection):
            raise ValueError("Invalid fill direction type supplied")

        if f not in GFillDirection:
            raise ValueError("Invalid fill direction value supplied")

        n_f = f

        if f == GFillDirection.Left:
            n_f = GFillDirection.TopLeft
        elif f == GFillDirection.Right:
            n_f = GFillDirection.TopRight
        else:
            n_f = f

        self._fill_direction = n_f

    def draw(self, screen: Surface, dt: float) -> None:
        x_pos, y_pos = self._position
        width, height = self._size

        bg_rect = pygame.Rect(x_pos, y_pos, width, height)

        position_rect = get_align_position(screen, bg_rect, self._position, self._align)

        x = position_rect.x
        y = position_rect.y

        if self._shape.shape_type == GShapeType.Square:
            pygame.draw.rect(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )
        else:
            pygame.draw.ellipse(
                screen,
                DefaultColors.White._get_color,
                position_rect,
                self.shape.border_size,
            )

        if len(self._objects) == 0:
            return

        obj_entries: List[GDrawable] = list(self._objects.values())

        if self._reverse:
            obj_entries.reverse()

        max_grid_w = 0
        # max_grid_h = 0
        obj_entries_chunked: List[List[GDrawable]] = []

        max_grid_w = math.floor(width / (self._max_object_size + self._spacing))
        obj_entries_chunked = list(array_chunks(obj_entries, max_grid_w))

        # if width >= height:
        #     max_grid_w = math.floor(width / (self._max_object_size + self._spacing))
        #     obj_entries_chunked = list(array_chunks(obj_entries, max_grid_w))
        # elif height > width:
        #     max_grid_h = math.floor(height / (self._max_object_size + self._spacing))
        #     obj_entries_chunked = list(array_chunks(obj_entries, max_grid_h))

        for j, o_a in enumerate(obj_entries_chunked):
            for i, o in enumerate(o_a):
                size = o.shape.size
                x_l = 0
                y_l = 0

                if self._fill_direction == GFillDirection.TopLeft:
                    x_l = (
                        x
                        + (i * self._max_object_size)
                        + (i * self._spacing)
                        + self._padding
                    )
                    y_l = (
                        y
                        + (j * self._max_object_size)
                        + (j * self._spacing)
                        + self._padding
                    )
                elif self._fill_direction == GFillDirection.TopRight:
                    x_l = (
                        (x + width)
                        - (i * self._max_object_size)
                        - (i * self._spacing)
                        - self._padding
                        - self._max_object_size
                    )
                    y_l = (
                        y
                        + (j * self._max_object_size)
                        + (j * self._spacing)
                        + self._padding
                    )
                elif self._fill_direction == GFillDirection.BottomLeft:
                    x_l = (
                        x
                        + (i * self._max_object_size)
                        + (i * self._spacing)
                        + self._padding
                    )
                    y_l = (
                        (y + height)
                        - (j * self._max_object_size)
                        - (j * self._spacing)
                        - self._padding
                        - self._max_object_size
                    )
                elif self._fill_direction == GFillDirection.BottomRight:
                    x_l = (
                        (x + width)
                        - (i * self._max_object_size)
                        - (i * self._spacing)
                        - self._padding
                        - self._max_object_size
                    )
                    y_l = (
                        (y + height)
                        - (j * self._max_object_size)
                        - (j * self._spacing)
                        - self._padding
                        - self._max_object_size
                    )

                if self._overflow == GOverflow.Hidden:
                    if self._fill_direction == GFillDirection.TopLeft:
                        if x_l + self._max_object_size > x + width:
                            continue
                        if y_l + self._max_object_size > y + height:
                            continue
                    elif self._fill_direction == GFillDirection.TopRight:
                        if x_l < x:
                            continue
                        if y_l + self._max_object_size > y + height:
                            continue
                    elif self._fill_direction == GFillDirection.BottomLeft:
                        if x_l + self._max_object_size > x + width:
                            continue
                        if y_l < y:
                            continue
                    elif self._fill_direction == GFillDirection.BottomRight:
                        if x_l < x:
                            continue
                        if y_l < y:
                            continue

                f_rect = (
                    pygame.draw.rect(
                        screen,
                        o.shape.color,
                        pygame.Rect(x_l, y_l, size, size),
                    )
                    if o.shape.shape_type == GShapeType.Square
                    else pygame.draw.ellipse(
                        screen,
                        o.shape.color,
                        pygame.Rect(x_l, y_l, size, size),
                    )
                )

                text_surface = self._font.render(
                    f"{o.id}", True, (0, 0, 0)  # type: ignore
                )
                screen.blit(
                    text_surface,
                    (
                        f_rect.center[0] - (self._max_object_size / 4),
                        f_rect.center[1] - (self._max_object_size / 4),
                    ),
                )
