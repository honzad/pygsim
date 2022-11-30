from typing import Optional, List, Tuple, Dict
from simpy.events import Event
import random

from pygsim.drawing import (
    GStateColorMapper,
    GShape,
    GShapeType,
    DefaultColors,
)
from pygsim.core import (
    GSimulationObject,
    GSimulation,
    GFactoryObject,
    GSimulationSpeed,
    FactoryType,
)
from pygsim.drawing.container import (
    GContainerRow,
    GcontainerGrid,
    GContainerBase,
    GFillDirection,
    GOverflow,
)

from pygsim.drawing.text import GText

import pygame


# Create states for checkout objects
class CheckoutState(GStateColorMapper):
    Closed = "#FF0000"
    Open = "#00FF00"
    Busy = "#FFA500"


# Create Checkout object
class CheckoutObject(GSimulationObject):
    # Assign States to this object
    States = CheckoutState  # type: ignore
    # Create default shape for this type of object
    Shape = GShape(
        GShapeType.Square, 75, 2, DefaultColors.Yellow._get_color  # type: ignore
    )

    def __init__(
        self,
        env: GSimulation,
        queue_container: GContainerBase,
        checkout_container: GContainerBase,
        checkout_rect: pygame.rect.Rect,
        *args,
        **kwargs,
    ) -> None:
        self._state_change = env.event()
        self._queued_customers: List[Tuple[CustomerObject, Event]] = []
        self._processed_customer: Optional[GSimulationObject] = None
        self._inactivity_counter = 0.0
        self._inactivity_close = 5.0

        self._queue_container = queue_container
        self._checkout_container = checkout_container

        self._checkout_rect = checkout_rect

        super().__init__(env, *args, **kwargs)

    @property
    def customer_count(self) -> int:
        return len(self._queued_customers)

    def life_cycle(self):
        while True:
            # Check if checkout is closed, if so then wait
            if self.current_state == CheckoutState.Closed:
                yield self._env.timeout(0.1)
                continue

            # Check if checkout is open and there arent any customers
            # if so then wait period of time before closing
            if (
                len(self._queued_customers) == 0
                and self.current_state == CheckoutState.Open
            ):
                if self._inactivity_counter <= self._inactivity_close:
                    self._inactivity_counter += 0.1
                    yield self._env.timeout(0.1)
                else:
                    self._inactivity_counter = 0.0
                    yield self._env.process(self.close_checkout())
                continue

            # Check if there are between 1 to 9 custoemrs and
            # if so set state to Open
            if len(self._queued_customers) > 0 and len(self._queued_customers) < 10:
                self.current_state = CheckoutState.Open
            # Check if there are more than 10 customers
            # is so set state to Busy
            elif len(self._queued_customers) > 10:
                self.current_state = CheckoutState.Busy

            # If there is at least 1 customer, process them
            yield self._env.process(self._process_customer())

    # Custom drawing function to draw checkout state
    def draw(self, screen, dt: float) -> None:
        pygame.draw.rect(
            screen,
            self.current_state._get_color,
            self._checkout_rect,
            2,
        )

    def _process_customer(self):
        # Take customer out of line
        customer, event = self._queued_customers.pop(0)

        # Remove customer from queue container
        self._queue_container.leave(customer)

        # Put customer in checkout container
        self._checkout_container.enter(customer)

        # Set customer state and wait for some time in checkout
        customer.current_state = CustomerState.Checkout
        time_to_process = sum(
            [random.uniform(0.02, 0.2) for _ in range(customer.items_bought)]
        )
        yield self._env.timeout(time_to_process)

        # Remove customer from queue container
        self._checkout_container.leave(customer)

        # Resolve event, which customer is waiting for
        event.succeed()

        # Wait a moment before accepting another customer
        yield self._env.timeout(1)

    def enqueue_customer(self, customer):
        yield self._env.timeout(0.05)
        # Create event for when customer is finished checkouting
        queue_event = self._env.event()
        # Add customer to queue
        self._queued_customers.append((customer, queue_event))
        # Put customer in queue container
        self._queue_container.enter(customer)
        # Return waiting event
        return queue_event

    def open_checkout(self):
        if self.current_state != CheckoutState.Closed:
            return

        yield self._env.timeout(0.01)

        self.queuedCustomers = []
        self.customerQueue = []
        self.current_state = CheckoutState.Open

    def close_checkout(self):
        if self.current_state == CheckoutState.Closed:
            return

        if self.current_state == CheckoutState.Busy:
            return

        if len(self.queuedCustomers) > 0:
            return

        self.current_state = CheckoutState.Closed

        yield self._env.timeout(0.01)


# Create gender enum
class GenderState(GStateColorMapper):
    Male = "#0000FF"
    Female = "#FFC0CB"


# Create customer states
class CustomerState(GStateColorMapper):
    WalkingToShopping = 0
    Shopping = 1
    WalkingToCheckout = 2
    Queued = 3
    Checkout = 4
    WalkingToExit = 5


# Create customer object
class CustomerObject(GSimulationObject):
    # Set customers states
    States = CustomerState  # type: ignore
    # Set default customer shape
    Shape = GShape(
        GShapeType.Circle, 50, -1, DefaultColors.Yellow._get_color  # type: ignore
    )

    def __init__(
        self,
        env: GSimulation,
        store: "StoreObject",
        container_dict: Dict[str, GContainerBase],
        *args,
        **kwargs,
    ) -> None:
        self._store = store
        self._container_dict = container_dict
        self._gender = (
            GenderState.Male if random.uniform(0, 1) < 0.5 else GenderState.Female
        )
        self._items_bought = 0
        self._arrive_time = env.now
        super().__init__(env, *args, **kwargs)

    @property
    def items_bought(self) -> int:
        return self._items_bought

    def life_cycle(self):
        # Put customer into walking to shopping container
        self._container_dict[f"{CustomerState.WalkingToShopping}"].enter(self)

        # Walk from store to shopping area
        yield self._env.timeout(random.randrange(1, 5))

        # Remove customer from walking to shopping container
        self._container_dict[f"{CustomerState.WalkingToShopping}"].leave(self)

        # Shop for items
        self.current_state = CustomerState.Shopping

        # Put customer into shopping container
        self._container_dict[f"{CustomerState.Shopping}"].enter(self)

        # Create random shopping time based on gender
        shoppping_time = (
            random.triangular(3, 10, 25)
            if self._gender == GenderState.Male
            else random.triangular(10, 20, 30)
        )

        # Create random items bought based on gender
        self._items_bought = int(
            random.triangular(1, 5, 15)
            if self._gender == GenderState.Male
            else random.triangular(10, 20, 30)
        )

        # Await customer to be done with shopping
        yield self._env.timeout(shoppping_time)

        # Remove customer from walking to shopping container
        self._container_dict[f"{CustomerState.Shopping}"].leave(self)

        # Walk from shopping to checkout
        self.current_state = CustomerState.WalkingToCheckout

        # Put customer into walking to checkout container
        self._container_dict[f"{CustomerState.WalkingToCheckout}"].enter(self)

        # Await customer to walk to checkout
        yield self._env.timeout(random.randrange(1, 5))

        # Remove customer from walking to checkout container
        self._container_dict[f"{CustomerState.WalkingToCheckout}"].leave(self)

        # Enqueue
        store: StoreObject = self._store
        # Get non busy checkout from store, if none open, open new one
        checkout: CheckoutObject = yield self._env.process(store.get_checkout())
        self.current_state = CustomerState.Queued
        # Await till customer is done with queue and processed checkout
        event = yield self._env.process(checkout.enqueue_customer(self))
        yield self._env.any_of([event])

        # Walk from checkout to exit
        self.current_state = CustomerState.WalkingToExit

        # Put customer into walking to exit container
        self._container_dict[f"{CustomerState.WalkingToExit}"].enter(self)

        # Await till customer walks out of store
        yield self._env.timeout(random.randrange(1, 5))

        # Remove customer from walking to exit container
        self._container_dict[f"{CustomerState.WalkingToExit}"].leave(self)

    def draw(self, screen, dt: float) -> None:
        pass


# Create customer factory
class CustomerFactory(GFactoryObject):
    # Set factory type to infinite
    Type = FactoryType.Infinite  # type: ignore

    # Set settings for distribution
    Occurance = 0.7  # type: ignore

    def __init__(
        self,
        env: GSimulation,
        store: "StoreObject",
        container_dict: Dict[str, GContainerBase],
        *args,
        **kwargs,
    ) -> None:
        self._store = store
        self._container_dict = container_dict
        super().__init__(env, *args, **kwargs)

    # Create customer objects
    def build(self):
        CustomerObject(self._env, self._store, self._container_dict)

    def draw(self, screen, dt: float) -> None:
        pass


# Create store object
class StoreObject(GFactoryObject):
    # Set factory type to finite, becouse we have finite checkouts
    Type = FactoryType.Finite  # type: ignore

    def __init__(self, env: GSimulation, checkout_count: int, *args, **kwargs) -> None:
        self._checkout_count = checkout_count
        self._checkouts: List[CheckoutObject] = []
        super().__init__(env, factory_max_build=checkout_count, *args, **kwargs)

    def draw(self, screen, dt) -> None:
        pass

    # Create checkouts and their containers
    def build(self):
        w, _ = self._env._resolution
        container_queue = GContainerRow(
            size=((int(w / 20) * 16) - 25, 75),
            position=(int(w / 20), 475 + (self._build_count * 75)),
            fill_direction=GFillDirection.Right,
            overflow=GOverflow.Hidden,
        )
        self._env.add_drawable(container_queue)

        checkout_rect = pygame.rect.Rect(
            (int(w / 20) * 17), 475 + (self._build_count * 75), int(w / 20) * 2, 75
        )

        container_checkout = GcontainerGrid(
            size=checkout_rect.size,
            position=(checkout_rect.x, checkout_rect.y),
            shape=GShape(GShapeType.Square, 75, -1, DefaultColors.White._get_color),
            fill_direction=GFillDirection.TopLeft,
            overflow=GOverflow.Visible,
        )

        self._env.add_drawable(container_checkout)

        checkout = CheckoutObject(
            self._env, container_queue, container_checkout, checkout_rect
        )

        container_checkout.shape.color = checkout.current_state._get_color

        self._env.add_drawable(checkout)
        self._checkouts.append(checkout)

    # Gets free checkout.
    # If no open checkouts, this will open random one.
    # If open and not busy, this will return non busy checkout
    # with least of customers waiting.
    # If busy and there are closed checkouts, this will open them.
    # Otherwise just choose the checkout with least of customers
    def get_checkout(self):
        checkouts = self._checkouts
        open_checkouts = list(
            filter(lambda c: c.current_state == CheckoutState.Open, checkouts)
        )

        if len(open_checkouts) == 0:
            return_checkout = yield self._env.process(self.open_closed_checkout())
            return return_checkout

        less_checkouts = list(
            filter(lambda c: len(c.queuedCustomers) < 10, open_checkouts)
        )

        if len(less_checkouts) == 0 and len(open_checkouts) != self._checkout_count:
            return_checkout = yield self._env.process(self.open_closed_checkout())
            return return_checkout

        if len(less_checkouts) == 0 and len(open_checkouts) == self._checkout_count:
            srt = sorted(open_checkouts, key=lambda c: len(c.queuedCustomers))
            yield self._env.timeout(0.001)
            return srt[0]

        if len(less_checkouts) > 0:
            srt = sorted(less_checkouts, key=lambda c: len(c.queuedCustomers))
            yield self._env.timeout(0.001)
            return srt[0]

        return None

    def open_closed_checkout(self):
        checkout = random.choice(
            list(
                filter(
                    lambda c: c.current_state == CheckoutState.Closed, self._checkouts
                )
            )
        )
        yield self._env.process(checkout.open_checkout())
        return checkout


if __name__ == "__main__":
    WINDOW_SIZE = (1000, 1000)

    env = GSimulation(
        simulation_speed=GSimulationSpeed.Faster,
        resolution=WINDOW_SIZE,
        debug_show=True,
    )

    # WalkingToShopping = 0
    container_wts = GContainerRow(
        size=((int(WINDOW_SIZE[0] / 20)) * 18, 75),
        position=(int(WINDOW_SIZE[0] / 20), 75),
        fill_direction=GFillDirection.Left,
        reverse=True,
    )
    env.add_drawable(container_wts)

    text_wts = GText(
        position=(int(WINDOW_SIZE[0] / 20), 60), text="Walking to shopping", size=20
    )
    env.add_drawable(text_wts)

    # Shopping = 1
    container_shp = GcontainerGrid(
        size=((int(WINDOW_SIZE[0] / 20)) * 10, 275),
        position=(int(WINDOW_SIZE[0] / 20), 175),
        fill_direction=GFillDirection.TopLeft,
        overflow=GOverflow.Hidden,
    )
    env.add_drawable(container_shp)

    text_shp = GText(position=(int(WINDOW_SIZE[0] / 20), 160), text="Shopping", size=20)
    env.add_drawable(text_shp)

    # WalkingToCheckout = 2
    container_wtc = GContainerRow(
        size=(((int(WINDOW_SIZE[0] / 20)) * 8) - 25, 75),
        position=((int(WINDOW_SIZE[0] / 20) * 11) + 25, 175),
        fill_direction=GFillDirection.Left,
        overflow=GOverflow.Hidden,
        reverse=True,
    )
    env.add_drawable(container_wtc)

    text_wtc = GText(
        position=((int(WINDOW_SIZE[0] / 20) * 11) + 25, 160),
        text="Walking to checkout",
        size=20,
    )
    env.add_drawable(text_wtc)

    # Queued = 3  => created in StoreObject

    text_q = GText(position=(int(WINDOW_SIZE[0] / 20), 460), text="Queued", size=20)
    env.add_drawable(text_q)

    # Checkout = 4 => Created in StoreObject

    text_c = GText(
        position=((int(WINDOW_SIZE[0] / 20) * 17), 460), text="Checkout", size=20
    )
    env.add_drawable(text_c)

    # WalkingToExit = 4
    container_wte = GContainerRow(
        size=((int(WINDOW_SIZE[0] / 20)) * 18, 75),
        position=(int(WINDOW_SIZE[0] / 20), 875),
        fill_direction=GFillDirection.Left,
    )
    env.add_drawable(container_wte)

    text_wte = GText(
        position=(int(WINDOW_SIZE[0] / 20), 860), text="Walking to exit", size=20
    )
    env.add_drawable(text_wte)

    container_map: Dict[str, GContainerBase] = {
        f"{CustomerState.WalkingToShopping}": container_wts,
        f"{CustomerState.Shopping}": container_shp,
        f"{CustomerState.WalkingToCheckout}": container_wtc,
        f"{CustomerState.WalkingToExit}": container_wte,
    }

    store = StoreObject(env, checkout_count=5)

    CustomerFactory(env, store, container_map)

    env.run()
