from typing import List, Union, Optional
from enum import Enum
from itertools import count
from abc import abstractmethod

from simpy.rt import RealtimeEnvironment
import pygame
from pygame.surface import Surface

from .drawing.color import GStateColorMapper, GStateColorMapperMeta
from .drawing.drawable import GDrawable
from .drawing.shape import GShape


class GSimulationSpeed(Enum):
    """Simulation speed enum, where each value is multiplier \
        of normal simulation speed"""

    Real = 1
    Slow = 2
    Fast = 5
    Faster = 10
    Fastest = 100


class GEnvironment(RealtimeEnvironment):
    """Extended ``simpy.rt.RealtimeEnvironment`` with graphical \
        capabilities of ``pygame`` to draw simulated objects.

    :param fps: Screen refresh rate in times per second, defaults to 30
    :type fps: int, optional
    :param simulation_speed: How fast should simulation proceed, defaults \
        to GSimulationSpeed.Real
    :type simulation_speed: Union[GSimulationSpeed, int, float], optional
    :param resolution: Defines ``pygame`` window size, defaults to (800, 600)
    :type resolution: Tuple[int, int], optional
    :param background_color: _description_, defaults to ``pygame.Color(0,0,0)``
    :type background_color: pygame.Color, optional,,
    :param auto_run: Specifies if the simulation will start on it self, or if it \
        needs to be started via ``.run()`` elsewhere, defaults to False
    :type auto_run: bool, optional
    """

    def __init__(
        self,
        fps=30,
        simulation_speed: Union[GSimulationSpeed, int, float] = GSimulationSpeed.Real,
        resolution=(800, 600),
        background_color=pygame.Color(0, 0, 0),
        auto_run=False,
        *args,
        **kwargs,
    ) -> None:
        factor = get_factor_from_speed(simulation_speed)
        super().__init__(factor=factor, *args, **kwargs)
        self._fps = fps
        self._ticks_per_frame = 1.0 / (self.factor * fps)
        self._resolution = resolution
        self._on_pygame_quit = self.event()
        self._background_color = background_color
        self._screen: Surface = pygame.display.set_mode(self._resolution)
        self._draw_callbacks: List[GDrawable] = []

        if auto_run:
            self.run()

    def _draw_loop(self):
        """Drawing loop using timeout calculated from desired \
            simulation speed and fps
        """
        while True:
            if self._is_quit_requested():
                self._on_pygame_quit.succeed()
            self._redraw()
            yield self.timeout(self._ticks_per_frame)

    def _redraw(self) -> None:
        """Redraws screen and tells every registered drawable to draw itself"""
        self._screen.fill(self._background_color)
        for draw_call in self._draw_callbacks:
            draw_call(screen=self._screen)
            pygame.display.flip()
            # Or use update in each draw calls to only specific parts

    def add_drawable(self, callable: GDrawable):
        self._draw_callbacks.append(callable)

    def remove_drawable(self, callable: GDrawable):
        targetId = -1
        for index, item in enumerate(self._draw_callbacks):
            if id(item) == id(callable):
                targetId = index
                break

        if targetId != -1:
            self._draw_callbacks.pop(targetId)

    def _is_quit_requested(self) -> bool:
        """Checks if there is pygame quit event happening

        :return: Returns true if pygame recieved quit event
        :rtype: bool
        """
        return any((e for e in pygame.event.get() if e.type == pygame.QUIT))

    def run(self) -> None:
        """Starts simulation and draw loop"""
        self.process(self._draw_loop())
        return super().run(until=self._on_pygame_quit)


def get_factor_from_speed(
    simulation_speed: Union[GSimulationSpeed, int, float]
) -> float:
    """Gets factor at which should simulation proceed, based on number how many times \
        the speed of the simulation should be

    :param simulation_speed: Desired speed of simulation, where speed is how big the \
        simulation speed multiplication is.
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


class GSimulationObject(GDrawable):
    """Base graphical simulation object.

    Has to be inherited and customized with custom \
        :func:`~pysg.core.GSimulationObject.life_cycle` method.

    :func:`~pysg.core.GSimulationObject.States` should be overriden in \
        inherited class as follows: 'States = SomeStateMapper', this \
        will set the default param states for all instances

    :func:`~pysg.core.GSimulationObject.Shape` can be overriden in \
        inherited class as follows: 'Shape = SomeShapeObject', this \
        will set the default param shape for all instances

    :param env: Graphical envirioment.
    :type env: :class:`~pysg.environment.GEnvironment`
    :param states: User defined state to color mapper created \
        with class inherited from :class:`~pysg.drawing.GStateColorMapper`.
    :type states: EnumMeta
    :param shape: What shape should the simulated object be drawn as.
    :type shape: :class:`~pysg.drawing.GShape`, defaults \
        to GShape(GShapeType.Circle, 10)
    :param default_state: Default state of user defined mapper, defaults \
        to None (select the first in Enum).
    :type default_state: GStateColorMapper, optional
    :param auto_run: Specifies if the simulation will start on it self, or if it \
        needs to be started via ``.run()`` elsewhere, defaults to False
    :type auto_run: bool, optional
    """

    _object_id_counter = count(0)

    def __init__(
        self,
        env: GEnvironment,
        states: Optional[GStateColorMapperMeta] = None,
        default_state: Optional[GStateColorMapper] = None,
        shape: Optional[GShape] = None,
        auto_run=False,
    ) -> None:
        self._id = next(self._object_id_counter)
        self._env = env
        self._states = self._set_states(states)
        self._current_state = self._set_current_state(default_state)

        super().__init__(shape)

        if auto_run:
            self.run()

    # Properities

    @property
    def id(self) -> int:
        return self._id

    @property
    def states(self) -> GStateColorMapperMeta:
        return self._states

    @property
    def current_state(self) -> GStateColorMapper:
        return self._current_state

    @current_state.setter
    def current_state(self, s: Optional[GStateColorMapper]) -> None:
        self._current_state = self._set_current_state(s)

    # Overridable

    @property
    def States(self) -> Optional[GStateColorMapperMeta]:
        """State to color mapper variable. **HAS to be overidden!**"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # States = TestState  # type: ignore
        return None

    @abstractmethod
    def life_cycle(self):
        """Simulation life cycle. **HAS to be overidden!**"""
        yield self._env.timeout(1)

    # Simulation

    def run(self) -> None:
        """Starts objects simulation"""
        self._env.process(self.life_cycle())

    # Helpers

    def _set_states(
        self, states: Optional[GStateColorMapperMeta]
    ) -> GStateColorMapperMeta:
        if (states is not None) and (self.States is not None):
            raise ValueError("Additional state mapper declared in constructor")

        if states is None:
            if self.States is None:
                raise ValueError(
                    "No state mapper declared in constructor or instance variable"
                )
            return self.States
        return states

    def _set_current_state(
        self, state: Optional[GStateColorMapper]
    ) -> GStateColorMapper:
        if state is None:
            return list(self._states._value2member_map_.values())[0]  # type: ignore
        elif isinstance(state, GStateColorMapper):
            vals = [v.name for v in self._states._value2member_map_.values()]
            if state.name not in vals:
                raise ValueError("Invalid state value supplied")
            return state
        else:
            raise ValueError("Invalid state type supplied")


# yield from
