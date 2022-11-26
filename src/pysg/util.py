import re
from PIL import ImageColor
from typing import Tuple, Any, List, TypeVar


def clamp(num, min_value, max_value):
    """Will clamp value between two numbers

    :param num: input number
    :type num: Union[float, int]
    :param min_value: minimum range number
    :type min_value: Union[float, int]
    :param max_value: maximum range number
    :type max_value: Union[float, int]
    :return: clamped value
    :rtype: Union[float, int]
    """
    return max(min(num, max_value), min_value)


# https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/
def is_valid_hex(string: str) -> bool:
    """Validates hex string

    :param string: hex string, should be in format "#000000" or "#000"
    :type string: str
    :return: if the string is valid
    :rtype: bool
    """

    regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
    p = re.compile(regex)

    if string is None:
        return False

    if re.search(p, string):
        return True
    else:
        return False


def hex_to_rgb(h: str) -> Tuple[int, int, int]:
    """Converts HEX string to RGB tuple

    :param h: HEX string
    :type h: str
    :return: RGB tuple
    :rtype: Tuple[int, int, int]
    """
    clr: Any = ImageColor.getcolor(h, "RGB")
    return (clr[0], clr[1], clr[2])


T = TypeVar("T")


def array_chunks(arr: List[T], n: int):
    """Chunks array into n chunks

    :param arr: Array
    :type arr: List[T]
    :param n: Chunk count
    :type n: int
    :rtype: Chunked array
    """
    for i in range(0, len(arr), n):
        yield arr[i : i + n]
