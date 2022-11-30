from typing import List, Union, Optional, Callable, Any
from enum import Enum
from itertools import count
from abc import abstractmethod
from numpy.random import exponential
import time

from simpy.rt import RealtimeEnvironment
import pygame
from pygame.surface import Surface

from .drawing.color import GStateColorMapper, GStateColorMapperMeta
from .drawing.drawable import GDrawable
from .drawing.shape import GShape


class GSimulationSpeed(Enum):
    """Simulation speed multiplier enum"""

    Real = 1
    Slow = 2
    Fast = 5
    Faster = 10
    Fastest = 100


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


class GSimulation(RealtimeEnvironment):
    """Extended ``simpy.rt.RealtimeEnvironment`` with graphical \
        capabilities of ``pygame`` to draw simulated objects.

    :param fps: Screen refresh rate in times per second, defaults to 30
    :type fps: int, optional
    :param resolution: Defines ``pygame`` window size, defaults to (800, 600)
    :type resolution: Tuple[int, int], optional
    :param background_color: Screen background color, \
        defaults to ``pygame.Color(0,0,0)``
    :type background_color: pygame.Color, optional,,
    :param simulation_speed: How fast should simulation proceed, defaults \
        to GSimulationSpeed.Real
    :type simulation_speed: Union[GSimulationSpeed, int, float], optional
    :param simulation_strict: If the simulation should be strict
    :type simulation_strict: bool, optional
    :param debug_show: Show debug stats, defaults to False
    :type debug_show: bool, optional
    :param debug_size: Debug stats size, defaults to 20
    :type debug_size: int, optional
    """

    def __init__(
        self,
        fps=30,
        resolution=(800, 600),
        background_color=pygame.Color(51, 51, 51),
        simulation_speed: Union[GSimulationSpeed, int, float] = GSimulationSpeed.Real,
        simulation_strict=False,
        debug_show=False,
        debug_size=20,
    ) -> None:
        # Pygame

        pygame.init()
        pygame.font.init()

        # Graphics

        self._fps = fps
        self._resolution = resolution
        self._background_color = background_color
        self._screen = pygame.display.set_mode(self._resolution)
        self._draw_calls: List[Callable[[Surface, float], None]] = []

        self._font = pygame.font.Font(None, debug_size)

        self._show_debug = debug_show

        # Simulation

        factor = get_factor_from_speed(simulation_speed)
        self._frame_ticks = 1 / (factor * self._fps)
        super().__init__(factor=factor, strict=simulation_strict)
        self._exit_event = self.event()

    @property
    def screen(self) -> Surface:
        return self._screen

    def _event_loop(self):
        if self._exit_event.triggered:
            self._exit_event = self.event()

        run = True

        last_tick = time.time()

        # Start the draw loop
        while run:
            # Get delta time
            current_tick = time.time()
            dt = current_tick - last_tick
            last_tick = current_tick

            # Pygame event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

            # Process draw calls
            self._process_draw_calls(dt)

            # sleep_time = self._frame_ticks - dt

            # Sleep for tick count to maintain fps
            # if sleep_time > 0:
            #     yield self.timeout(sleep_time)
            # else:
            #     yield self.timeout(self._frame_ticks)

            yield self.timeout(self._frame_ticks)

        # End the simulation
        self._exit_event.succeed()

    def _process_draw_calls(self, delta: float):
        # Repaint the screen
        self._screen.fill(self._background_color)
        # Repaint each draw call
        for draw_call in self._draw_calls:
            draw_call(self._screen, delta)
        # Draw debug
        self._draw_debug(self._screen, delta)
        # Refresh screen
        pygame.display.flip()

    def _draw_debug(self, screen: Surface, dt: float):
        if not self._show_debug:
            return

        if dt == 0.0:
            return

        text_fps_surface = self._font.render(
            f"FPS = {round(1/dt, 2)}", True, (255, 255, 255)
        )
        text_t_surface = self._font.render(
            f"t = {round(self.now, 2)}", True, (255, 255, 255)
        )
        text_t_rect = text_t_surface.get_rect()

        screen.blit(text_fps_surface, (5, 5))
        screen.blit(text_t_surface, (5, 10 + text_t_rect.height))

    def add_drawable(self, callable: GDrawable):
        """Adds drawable object to draw call pool

        :param callable: Callable GDrawable object
        :type callable: GDrawable
        """
        self._draw_calls.append(callable)

    def remove_drawable(self, callable: GDrawable):
        """Removes drawable object from draw call pool

        :param callable: Callable GDrawable object
        :type callable: GDrawable
        """
        targetId = -1
        for index, item in enumerate(self._draw_calls):
            if id(item) == id(callable):
                targetId = index
                break

        if targetId != -1:
            self._draw_calls.pop(targetId)

    def run(self):
        """Starts the simulation"""
        self.process(self._event_loop())
        return super().run(until=self._exit_event)


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
        env: GSimulation,
        states: Optional[GStateColorMapperMeta] = None,
        default_state: Optional[GStateColorMapper] = None,
        shape: Optional[GShape] = None,
    ) -> None:
        self._id = next(self._object_id_counter)
        self._env = env
        self._states = self._set_states(states)
        self._current_state = self._set_current_state(default_state)

        super().__init__(shape)

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
        c = self._set_current_state(s)
        if c == self._current_state:
            return
        self._shape.color = c._get_color
        self._current_state = c

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


class FactoryType(Enum):
    Infinite = 0
    Finite = 1


class GFactoryObject(GDrawable):
    """Factory class for specified objects

    :param env: Main simulation object
    :type env: GSimulation
    :param shape: Default shape, defaults to None
    :type shape: Optional[GShape], optional
    :param distribution: Default distribution function, defaults to \
        :func:`~numpy.random.exponential`
    :type distribution: Optional[Callable[[Any], float]], optional
    :param occurance: How often should build function be called, defaults to 1.0
    :type occurance: Optional[float], optional
    """

    _object_id_counter = count(0)

    def __init__(
        self,
        env: GSimulation,
        shape: Optional[GShape] = None,
        factory_type: FactoryType = FactoryType.Infinite,
        factory_max_build=5,
        distribution: Optional[Callable[[Any], float]] = None,
        occurance: Optional[float] = None,
    ) -> None:
        self._id = next(self._object_id_counter)
        self._env = env
        self._type = self._set_type(factory_type)
        self._max_build = self._set_build_count(factory_max_build)
        self._distribution = self._set_time(distribution)
        self._occurance = self._set_occurance(occurance)
        self._build_count = 0

        super().__init__(shape)

        self.run()

    # Properities

    @property
    def id(self) -> int:
        return self._id

    @property
    def build_count(self) -> int:
        return self._build_count

    # Overridable

    @property
    def Type(self) -> Optional[FactoryType]:
        """Factory type, either Infinite or Finite"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # States = TestState  # type: ignore
        pass

    @property
    def BuildCount(self) -> Optional[int]:
        """Finite factory type build count"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # States = TestState  # type: ignore
        pass

    @property
    def Distribution(self) -> Optional[Callable[[Any], float]]:
        """Target to spawn. **CAN to be overidden, will use exponential \
            distribution by default**
        """
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # States = TestState  # type: ignore
        pass

    @property
    def Occurance(self) -> Optional[float]:
        """How often does this object spawn. **CAN to be overidden!**"""
        # Pylint will not support correct typing so we have to use # type: ignore
        # at destination declaration, for instance.
        # States = TestState  # type: ignore
        pass

    def _life_cycle(self):
        if self._type == FactoryType.Infinite:
            while True:
                self.build()
                self._build_count += 1
                yield self._env.timeout(self._distribution(self._occurance))
        else:
            for i in range(self._max_build):
                self.build()
                self._build_count += 1
                yield self._env.timeout(0)

    # Simulation

    def run(self) -> None:
        """Starts objects simulation"""
        self._env.process(self._life_cycle())

    @abstractmethod
    def build(self):
        """Building function, has to be overriden

        This function is called every specified semi random interval
        """
        pass

    # Helpers

    def _set_build_count(self, c: Optional[int]) -> int:
        if self.BuildCount is None:
            if c is None:
                return 5
            return c
        return self.BuildCount

    def _set_type(self, t: Optional[FactoryType]) -> FactoryType:
        if self.Type is None:
            if t is None:
                return FactoryType.Infinite
            return t
        return self.Type

    def _set_time(self, c: Optional[Callable[[Any], float]]) -> Callable[[Any], float]:
        if self.Distribution is None:
            if c is None:
                return exponential
            return c
        return self.Distribution

    def _set_occurance(self, o: Optional[float]) -> float:
        if self.Occurance is None:
            if o is None:
                return 1.0
            return o
        return self.Occurance
