from pysg.drawing import GStateColorMapper, GShape, GShapeType, DefaultColors
from pysg.core import GSimulationObject, GEnvironment
from pysg.drawing.container import GContainerRow, GOverflow


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject):
    States = TestState  # type: ignore
    Shape = GShape(GShapeType.Square, 30, -1, DefaultColors.Yellow._get_color)  # type: ignore

    def life_cycle(self):
        pass

    def draw(self, screen) -> None:
        pass


if __name__ == "__main__":
    env = GEnvironment()
    c = GContainerRow((200, 50), (30, 30), overflow=GOverflow.Visible)
    env.add_drawable(c)

    n = 5

    for i in range(n):
        obj = TestObject(env)
        c.enter(obj)
    env.run()
    pass
