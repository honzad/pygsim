from typing import List, Any, Tuple, Union
from enum import Enum

from simpy.rt import RealtimeEnvironment
from simpy.events import Event
import pygame

from pysg.core import GSimulationObject

class GSimulationSpeed(Enum):
	Real = 1
	Slow = 2
	Fast = 5
	Faster = 10
	Fastest = 100

class GEnvironment(RealtimeEnvironment):
	"""Extended ``simpy.rt.RealtimeEnvironment`` with graphical capabilities of ``pygame`` to draw simulated objects.

		:param fps: Screen refresh rate in times per second, defaults to 30
		:type fps: int, optional
		:param simulation_speed: How fast should simulation proceed, defaults to GSimulationSpeed.Real
		:type simulation_speed: Union[GSimulationSpeed, int, float], optional
		:param resolution: Defines ``pygame`` window size, defaults to (800, 600)
		:type resolution: Tuple[int, int], optional
		:param background_color: _description_, defaults to ``pygame.Color(0,0,0)``
		:type background_color: pygame.Color, optional
		:param auto_run: Specifies if the simulation will start on it self, or if it needs to be started via ``.run()`` elsewhere, defaults to False
		:type auto_run: bool, optional
	"""

	def __init__(self, fps=30, simulation_speed: Union[GSimulationSpeed, int, float] = GSimulationSpeed.Real, resolution = (800, 600), background_color = pygame.Color(0,0,0), auto_run = False, *args, **kwargs) -> None:
		factor = get_factor_from_speed(simulation_speed)
		super().__init__(factor=factor, *args, **kwargs)
		self._fps = fps
		self._ticks_per_frame = 1.0 / (self.factor * fps)
		self._resolution = resolution
		self._on_pygame_quit = self.event()
		self._background_color = background_color
		self._screen = pygame.display.set_mode(self._resolution)
		self._draw_callbacks: List[GSimulationObject] = []

		if auto_run:
			self.run()

	def _draw_loop(self):
		"""Drawing loop using timeout calculated from desired simulation speed and fps
		"""
		while True:
			if self._is_quit_requested():
				self._on_pygame_quit.succeed()
			self._redraw()
			yield self.timeout(self._ticks_per_frame)

	def _redraw(self) -> None:
		"""Redraws screen and tells every registered drawable to draw itself
		"""
		self._screen.fill(self._fill_color)
		for draw_call in self._draw_callbacks:
			draw_call(screen=self._screen)
			pygame.display.flip() # Or use update in each draw calls to only specific parts

	def add_drawable(self, callable: GSimulationObject):
		pass

	def remove_drawable(self, callable: GSimulationObject):
		pass

	def _is_quit_requested(self) -> bool:
		"""Checks if there is pygame quit event happening

		:return: Returns true if pygame recieved quit event
		:rtype: bool
		"""
		return any((e for e in pygame.event.get() if e.type == pygame.QUIT))

	def run(self) -> None:
		"""Starts simulation and draw loop
		"""
		self.process(self._draw_loop())
		return super().run(until=self._on_pygame_quit)

def get_factor_from_speed(simulation_speed: Union[GSimulationSpeed, int, float]) -> float:
	"""Gets factor at which should simulation proceed, based on number how many times the speed of the simulation should be

	:param simulation_speed: Desired speed of simulation, where speed is how big the simulation speed multiplication is.
	:type simulation_speed: Union[GSimulationSpeed, int, float]
	:raises ValueError: When invalid GSimulationSpeed is supplied.
	:raises ValueError: When supplied speed is either zero or negative.
	:raises ValueError: When other type than GSimulationSpeed, int or float supplied.
	:return: Speed factor
	:rtype: float
	"""
	factor = 1.0
	if isinstance(simulation_speed, GSimulationSpeed):
		values = [m.value for m in GSimulationSpeed]
		if simulation_speed.value not in values:
			raise ValueError("Invalid GSimulationSpeed simulation speed")
		factor = 1 / simulation_speed.value
	elif any([isinstance(simulation_speed, int), isinstance(simulation_speed, float)]):
		if simulation_speed <= 0:
			raise ValueError("Simulation speed cannot be negative or zero")
		factor = 1 / simulation_speed
	else:
		raise ValueError("Invalid simulation speed ")
	return factor
