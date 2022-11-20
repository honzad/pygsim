from enum import Enum, EnumMeta
import colorsys
import math
from typing import Dict, Union, Tuple, List
import pygame

from pysg.util import clamp, is_valid_hex, hex_to_rgb


def validate_enumerations(d: Dict[str, Union[str, int]]) -> None:
    for data in d.values():
        data_type = f"{type(data).__name__}"
        if data_type == str.__name__:
            if not is_valid_hex(data):
                raise ValueError(f"Hex value '{data}' is not valid")
        elif data_type == int.__name__:
            if data < 0:
                raise ValueError("Negative number supplied")
            if data >= len(d):
                raise ValueError("Value bigger or equal than count of enum values")
        else:
            raise ValueError(
                "Invalid color type supplied, has to be either int or string"
            )


def generate_color_palette(n: int = 5) -> List[Tuple[int, int, int]]:
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
    color_palette = generate_color_palette(len(d))
    color_dict: Dict[str, pygame.Color] = {}
    for i, (key, data) in enumerate(d.items()):
        data_type = f"{type(data).__name__}"
        if data_type == str.__name__:
            color_dict.update({key: pygame.Color(hex_to_rgb(data))})
        else:
            color_dict.update({key: pygame.Color(color_palette[i])})
    return color_dict


class GStateColorMapperMeta(EnumMeta):
    def __new__(metacls, cls: str, bases, classdict, **kwds):
        enumerations = {x: y for x, y in classdict.items() if not x.startswith("_")}
        validate_enumerations(enumerations)
        enum = super().__new__(metacls, cls, bases, classdict, **kwds)
        enum._enumerations = enumerations
        enum._colors = color_enumerations_to_colors(enumerations)
        return enum

    def __getitem__(cls, key):
        return getattr(cls, key)

    def __iter__(cls):
        return (name for name in cls._member_names_)

    def __len__(cls):
        return len(cls._member_names_)


class GStateColorMapper(Enum, metaclass=GStateColorMapperMeta):
    def __get__(self, instance, owner):
        return self.__class__.__members__[self.name]

    @property
    def _get_value(self) -> Union[str, int]:
        return self.__class__.__members__[self.name].value

    @property
    def _get_color(self) -> pygame.Color:
        return self.__class__._colors[self.name]
