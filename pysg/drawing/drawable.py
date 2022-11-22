from abc import ABC, abstractmethod

from pygame.surface import Surface


class GDrawable(ABC):
    """Base class providing drawable functions to simulation classes"""

    def __call__(self, screen: Surface) -> None:
        """Calls the drawing function when class called as function

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        self.draw(screen)

    @abstractmethod
    def draw(self, screen: Surface) -> None:
        """Drawing function, can be overidden.

        This draw call function is called `fps` times per second as \
            specified in :class:`~pysg.environment.GEnvironment` .

        :param screen: Screen to draw this object on
        :type screen: pygame.Surface
        """
        pass
