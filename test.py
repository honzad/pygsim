from pysg.drawing import GStateColorMapper

class TestState(GStateColorMapper):
	Online = "#fff"
	Offline = "#000"

class FooState(GStateColorMapper):
	Online = 0
	Offline = 1

if __name__ == "__main__":
	print(TestState.Online._get_color)
	print(TestState.Offline._get_color)
	print(FooState.Online._get_color)
	print(FooState.Offline._get_color)

	pass
