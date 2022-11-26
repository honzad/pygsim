from enum import Enum, EnumMeta
import colorsys
import math
from typing import Dict, Union, Tuple, List
import pygame

from ..util import clamp, is_valid_hex, hex_to_rgb


def validate_enumerations(d: Dict[str, Union[str, int]]) -> None:
    """Validates :class:`~pysg.drawing.GStateColorMapper` color values

    :param d: Color values from Enum
    :type d: Dict[str, Union[str, int]]
    :raises ValueError: If string value is not a valid HEX color format
    :raises ValueError: If negative int value is supplied
    :raises ValueError: If int value is larger than number of Enum values
    :raises ValueError: If invalid type other than int or string supplied as color
    """
    for data in d.values():
        if isinstance(data, str):
            if not is_valid_hex(data):
                raise ValueError(f"Hex value '{data}' is not valid")
        elif isinstance(data, int):
            if data < 0:
                raise ValueError("Negative number supplied")
            if data >= len(d):
                raise ValueError("Value bigger or equal than count of enum values")
        else:
            raise ValueError(
                "Invalid color type supplied, has to be either int or string"
            )


def generate_color_palette(n: int = 5) -> List[Tuple[int, int, int]]:
    """Generates color pallete of size n

    :param n: Number of samples of pallete, defaults to 5
    :type n: int, optional
    :return: List of RGB tuples
    :rtype: List[Tuple[int, int, int]]
    """
    HSV_tuples = [(x * 1.0 / n, 0.5, 0.5) for x in range(n)]
    RGB_tuples = map(lambda x: colorsys.hsv_to_rgb(*x), HSV_tuples)
    return list(
        map(
            lambda x: tuple(clamp(math.ceil(255.0 * elem), 0, 255) for elem in x),
            RGB_tuples,
        )
    )


def color_enumerations_to_colors(
    d: Dict[str, Union[str, int]]
) -> Dict[str, pygame.Color]:
    """Creates :class:`~pysg.drawing.GStateColorMapper` color values

    :param d: Color values from Enum
    :type d: Dict[str, Union[str, int]]
    :return: Dictionary mapping, Enum keys to :class:`~pygame.Color`
    :rtype: Dict[str, pygame.Color]
    """
    color_palette = generate_color_palette(len(d))
    color_dict: Dict[str, pygame.Color] = {}
    for i, (key, data) in enumerate(d.items()):
        if isinstance(data, str):
            color_dict.update({key: pygame.Color(hex_to_rgb(data))})
        else:
            color_dict.update({key: pygame.Color(color_palette[i])})
    return color_dict


class GStateColorMapperMeta(EnumMeta):
    """Meta class for :class:`~.GStateColorMapper`"""

    def __new__(cls, cls_str: str, bases, classdict, **kwds):
        enumerations = {x: y for x, y in classdict.items() if not x.startswith("_")}
        validate_enumerations(enumerations)
        enum = super().__new__(cls, cls_str, bases, classdict, **kwds)
        enum._enumerations = enumerations  # type: ignore
        enum._colors = color_enumerations_to_colors(enumerations)  # type: ignore
        return enum

    def __getitem__(cls, key):
        return getattr(cls, key)

    def __iter__(cls):
        return (name for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)


class GStateColorMapper(Enum, metaclass=GStateColorMapperMeta):
    """Maps Enum values to color values, takes string or int as value

    String values HAS to be in hex format.
    Int values HAS to be less than count of all key in enum

    Examples
    --------
    >>> class TestState(GStateColorMapper): Online = "#fff"; Offline = 1
    >>> TestState.Online._get_color
    (255, 255, 255, 255)
    >>> TestState.Offline._get_color
    (64, 128, 128, 255)
    """

    def __get__(self, instance, owner):
        return self.__class__.__members__[self.name]

    @property
    def _get_value(self) -> Union[str, int]:
        return self.__class__.__members__[self.name].value

    @property
    def _get_color(self) -> pygame.Color:
        return self.__class__._colors[self.name]  # type: ignore


class DefaultColors(GStateColorMapper):
    White = "#fff"
    Black = "#000"
    Red = "#FF0000"
    Green = "#00FF00"
    Blue = "#0000FF"
    LightBlue = "#ADD8E6"
    Yellow = "#FFFF00"
    Orange = "#FFA500"
