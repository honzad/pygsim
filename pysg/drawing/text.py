from typing import Tuple, Optional

import pygame
from pygame.surface import Surface

from .drawable import GDrawable
from .shape import GShape
from .color import DefaultColors

# from .container import GAlign


class GText(GDrawable):
    def __init__(
        self,
        position: Tuple[int, int],
        text: Optional[str] = None,
        size: Optional[int] = None,
        color: Optional[pygame.Color] = None,
        shape: Optional[GShape] = None,
    ) -> None:
        super().__init__(shape)  # ToDo: Allow custom background with shape?
        self._position = self._set_position(position)
        self._text = self._set_text(text)
        self._size = self._set_size(size)
        self._color = self._set_color(color)
        self._font = self._set_font(self._size)

    # Properities

    @property
    def position(self) -> Tuple[int, int]:
        return self._position

    @position.setter
    def position(self, p: Tuple[int, int]):
        if (not isinstance(p[0], int)) or (not isinstance(p[1], int)):
            raise ValueError("Invalid type for position supplied")

        if (p[0] < 0) or (p[1] < 0):
            raise ValueError("Negative values supplied to position")

        self._position = p

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, t: Optional[str]):
        self._text = self._set_text(t)

    @property
    def size(self) -> int:
        return self._size

    @size.setter
    def size(self, s: Optional[int]):
        self._size = self._set_size(s)
        self._font = self._set_font(self._size)

    @property
    def color(self) -> pygame.Color:
        return self._color

    @color.setter
    def color(self, c: Optional[pygame.Color]):
        self._color = self._set_color(c)

    # Overides

    def draw(self, screen: Surface) -> None:
        if not (self._text and self._text.strip()):
            return
        text_surface = self._font.render(self._text, True, self._color)
        # ToDo: Render background shape -> set text by align in the bounding box
        screen.blit(text_surface, (self._position[0], self._position[1]))

    # Helpers

    def _set_position(self, p: Tuple[int, int]) -> Tuple[int, int]:
        if (not isinstance(p[0], int)) or (not isinstance(p[1], int)):
            raise ValueError("Invalid type for position supplied")

        if (p[0] < 0) or (p[1] < 0):
            raise ValueError("Negative values supplied to position")

        return p

    def _set_text(self, t: Optional[str]) -> str:
        return "" if t is None else t

    def _set_size(self, s: Optional[int]) -> int:
        if s is None:
            return 20  # ToDo: replace magic number

        if not isinstance(s, int):
            raise ValueError("Invalid type for size supplied")

        return s

    def _set_color(self, c: Optional[pygame.Color]) -> pygame.Color:
        if c is None:
            return DefaultColors.White._get_color

        if not isinstance(c, pygame.Color):
            raise ValueError("Invalid color type supplied")

        return c

    def _set_font(self, size: int):
        return pygame.font.Font(None, size)
