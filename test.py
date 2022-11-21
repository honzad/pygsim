from pysg.drawing import GStateColorMapper
from pysg.core import GSimulationObject, GEnvironment


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject):
    Test = 1

    def life_cycle(self):
        pass


if __name__ == "__main__":
    print(TestState.Online._get_color)
    print(TestState.Offline._get_color)
    print(type(TestState))
    print(type(TestState.Online))
    env = GEnvironment()
    obj = TestObject(env, states=TestState)
    pass
