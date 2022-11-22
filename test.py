from pysg.drawing import GStateColorMapper, GDrawable, GShape, GShapeType, DefaultColors
from pysg.core import GSimulationObject, GEnvironment


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject, GDrawable):
    States = TestState  # type: ignore
    Shape = GShape(GShapeType.Circle, 10, -1, DefaultColors.White._get_color)  # type: ignore

    def life_cycle(self):
        pass

    def draw(self, screen) -> None:
        pass


if __name__ == "__main__":
    # print(TestState.Online._get_color)
    # print(TestState.Offline._get_color)
    # print(type(TestState))
    # print(type(TestState.Online))
    env = GEnvironment()
    obj = TestObject(env)
    # env.add_drawable(obj)
    print(obj.shape.shape_type)
    print(obj.current_state)
    print(obj.states)
    pass
