from pygsim.drawing import GStateColorMapper, GShape, GShapeType, DefaultColors
from pygsim.core import GSimulationObject, GSimulation, GSimulationSpeed
from pygsim.drawing.container import GAlign
from pygsim.drawing.text import GText


class TestState(GStateColorMapper):
    Online = "#fff"
    Offline = 1


class TestObject(GSimulationObject):
    States = TestState  # type: ignore
    Shape = GShape(
        GShapeType.Square, 30, -1, DefaultColors.Yellow._get_color  # type: ignore
    )

    def __init__(
        self, env, text_object: GText, states=None, default_state=None, shape=None
    ) -> None:
        self._text_object = text_object
        super().__init__(env, states, default_state, shape)

    def life_cycle(self):
        while True:
            for data in GAlign:
                self._text_object.align = data
                self._text_object.text = f"{data}"
                yield self._env.timeout(1)

    def draw(self, screen, dt) -> None:
        pass


if __name__ == "__main__":
    env = GSimulation(simulation_speed=GSimulationSpeed.Real, debug_show=True)

    t1 = GText(position=(0, 0), text="Align test", size=50, align=GAlign.BottomLeft)
    env.add_drawable(t1)

    s1 = TestObject(env, t1)

    env.run()
