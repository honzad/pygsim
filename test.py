from pysg.drawing import GStateColorMapper, GShape, GShapeType, DefaultColors
from pysg.core import GSimulationObject, GEnvironment, GFactoryObject
from pysg.drawing.container import (
    GContainerRow,
    GContainerColumn,
    GcontainerGrid,
    GOverflow,
    GFillDirection,
)

import pygame


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject):
    States = TestState  # type: ignore
    Shape = GShape(
        GShapeType.Square, 30, -1, DefaultColors.Yellow._get_color  # type: ignore
    )

    def life_cycle(self):
        pass

    def draw(self, screen) -> None:
        pass


class TestFactory(GFactoryObject):
    def draw(self, screen) -> None:
        pass

    def build(self):
        obj = TestObject(self._env)
        c3.enter(obj)


if __name__ == "__main__":
    pygame.init()
    pygame.font.init()

    env = GEnvironment()
    c = GContainerColumn(
        size=(50, 200),
        position=(30, 30),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.Left,
        reverse=True,
    )
    env.add_drawable(c)

    c2 = GContainerRow(
        size=(200, 50),
        position=(150, 30),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.Right,
    )
    env.add_drawable(c2)

    c3 = GcontainerGrid(
        size=(300, 150),
        position=(150, 150),
        overflow=GOverflow.Hidden,
        fill_direction=GFillDirection.TopLeft,
    )
    env.add_drawable(c3)

    fy = TestFactory(env, auto_run=True)

    env.run()
