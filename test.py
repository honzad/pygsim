from pysg.drawing import GStateColorMapper, GDrawable
from pysg.core import GSimulationObject, GEnvironment


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject, GDrawable):
    def life_cycle(self):
        pass

    def draw(self, screen) -> None:
        pass


if __name__ == "__main__":
    print(TestState.Online._get_color)
    print(TestState.Offline._get_color)
    print(type(TestState))
    print(type(TestState.Online))
    env = GEnvironment()
    obj = TestObject(env, states=TestState)
    env.add_drawable(obj)
    pass
