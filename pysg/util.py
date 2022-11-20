from PIL import ImageColor
from typing import Tuple
import re

def clamp(num, min_value, max_value):
	return max(min(num, max_value), min_value)

# https://www.geeksforgeeks.org/how-to-validate-hexadecimal-color-code-using-regular-expression/
def is_valid_hex(string: str) -> bool:
	regex = "^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$"
	p = re.compile(regex)

	if(string == None):
		return False

	if(re.search(p, string)):
		return True
	else:
		return False

def hex_to_rgb(h: str) -> Tuple[int, int, int]:
	return ImageColor.getcolor(h, "RGB")
