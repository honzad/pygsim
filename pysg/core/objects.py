from typing import List, Any, Tuple, Union
from enum import Enum, EnumMeta
from itertools import count
from abc import ABC, abstractmethod

import pygame

from pysg.core.environment import GEnvironment
from pysg.drawing import GShape, GShapeType

class GSimulationObject(ABC):
	"""Base graphical simulation object.

		Has to be inherited and customized with custom :func:`~pysg.core.GSimulationObject.life_cycle` method, and :func:`~pysg.core.GSimulationObject.draw` if needed.

		:param env: Graphical envirioment.
		:type env: :class:`~pysg.environment.GEnvironment`
		:param states: User defined state to color mapper created with :func:`~pysg.drawing.generate_state_color_enum`.
		:type states: EnumMeta
		:param shape: What shape should the simulated object be drawn as.
		:type shape: :class:`~pysg.drawing.GShape`, defaults to GShape(GShapeType.Circle, 10)
		:param default_state: Default state of user defined mapper, defaults to None (select the first in Enum).
		:type default_state: Enum, optional
		:param auto_run: Specifies if the simulation will start on it self, or if it needs to be started via ``.run()`` elsewhere, defaults to False
		:type auto_run: bool, optional
		"""
	_object_id_counter = count(0)

	def __init__(self, env: GEnvironment, states: EnumMeta, shape: GShape = GShape(GShapeType.Circle, 10), default_state: Enum = None, auto_run = False) -> None:
		self._id = next(self._object_id_counter)
		self._env = env
		self._states = states
		self.current_state = default_state
		self.shape = shape

		if auto_run:
			self.run()

	def __call__(self, screen: pygame.Surface) -> None:
		"""Calls the drawing function when class called as function

		:param screen: Screen to draw this object on
		:type screen: pygame.Surface
		"""
		self._draw(screen)

	def draw(self, screen: pygame.Surface) -> None:
		"""Drawing function, can be overidden.

		This draw call function is called `fps` times per second as specified in :class:`~pysg.environment.GEnvironment` .

		:param screen: Screen to draw this object on
		:type screen: pygame.Surface
		"""
		pass

	@abstractmethod
	def life_cycle(self):
		"""Simulation life cycle. **Has to be overidden**
		"""
		pass

	def run(self) -> None:
		"""Starts objects simulation
		"""
		self._env.process(self.life_cycle())

	@property
	def id(self) -> int:
		return self._id

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
	def states(self) -> EnumMeta:
		return self._states

	@property
	def current_state(self) -> Enum:
		return self._current_state

	@current_state.setter
	def current_state(self, s: Union[Enum, None]) -> None:
		if s is None:
			self._current_state = list(self._states._value2member_map_.values())[0]
		elif isinstance(s, Enum):
			vals = [v.name for v in self._states._value2member_map_.values()]
			if s.name not in vals:
				raise ValueError("Invalid state value supplied")
			self._current_state = s
		else:
			raise ValueError("Invalid state type supplied")
# yield from
