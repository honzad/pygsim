from pygsim.drawing import GStateColorMapper, GShape, GShapeType, DefaultColors
from pygsim.core import GSimulationObject, GSimulation, GFactoryObject, GSimulationSpeed
from pygsim.drawing.container import (
    GContainerRow,
    GContainerColumn,
    GcontainerGrid,
    GOverflow,
    GFillDirection,
)
from pygsim.drawing.text import GText

from numpy import random


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject):
    States = TestState  # type: ignore
    Shape = GShape(
        GShapeType.Square, 30, -1, DefaultColors.Yellow._get_color  # type: ignore
    )

    def life_cycle(self):
        yield self._env.timeout(1)

    def draw(self, screen, dt) -> None:
        pass


class TestObjectVariant(GSimulationObject):
    States = TestState  # type: ignore
    Shape = GShape(
        GShapeType.Circle, 30, -1, DefaultColors.Orange._get_color  # type: ignore
    )

    def life_cycle(self):
        yield self._env.timeout(1)

    def draw(self, screen, dt) -> None:
        pass


class TestFactory(GFactoryObject):
    Occurance = 0.7  # type: ignore

    def draw(self, screen, dt) -> None:
        pass

    def build(self):
        obj = (
            TestObject(self._env)
            if random.uniform() > 0.5
            else TestObjectVariant(self._env)
        )
        c.enter(obj)
        c2.enter(obj)
        c3.enter(obj)


if __name__ == "__main__":
    env = GSimulation(simulation_speed=GSimulationSpeed.Faster, debug_show=True)

    c = GContainerColumn(
        size=(50, 300),
        position=(100, 100),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.Left,
        reverse=True,
    )
    env.add_drawable(c)

    t = GText(position=(100, 80), text="Column container", size=20)
    env.add_drawable(t)

    c2 = GContainerRow(
        size=(300, 50),
        position=(250, 100),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.Right,
        reverse=True,
    )
    env.add_drawable(c2)

    t1 = GText(position=(250, 80), text="Row container", size=20)
    env.add_drawable(t1)

    c3 = GcontainerGrid(
        size=(300, 200),
        position=(250, 200),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.TopLeft,
        reverse=True,
    )
    env.add_drawable(c3)

    t2 = GText(position=(250, 180), text="Grid container", size=20)
    env.add_drawable(t2)

    fy = TestFactory(env)

    env.run()
