import asyncio
import random
import uuid
from dataclasses import dataclass

from foobartory import config as cfg
from foobartory import constants
from foobartory.decorators import wait_if_moving


@dataclass
class Foo:
    def __init__(self):
        self.uid: str = str(uuid.uuid4())


@dataclass
class Bar:
    def __init__(self):
        self.uid: str = str(uuid.uuid4())


@dataclass
class Foobar:
    uid: str


class Robot:
    def __init__(self, uid: int, foobartory):
        self.uid: int = uid
        self.running: bool = True
        self.foobartory = foobartory
        self.current_job: str = constants.SLEEPING

    def __str__(self):
        return f"Robot {self.uid}"

    async def stop(self) -> None:
        self.current_job = constants.SLEEPING
        self.running = False

    async def start(self) -> None:
        while self.running:
            if await self.check_and_reserve_buy_robot():
                await self.buy_robot()

            elif self.foobartory.foo_queue.qsize() < cfg.ROBOT_FOO_COST:
                await self.mine_foo()

            elif await self.check_and_reserve_sell_foobar():
                await self.sell_foobar()

            elif await self.check_and_reserve_build_foobar():
                await self.build_foobar()

            else:
                await self.mine_bar()

    async def check_and_reserve_build_foobar(self) -> bool:
        """
        Checks if the robot must build a foobar.
        If it's the case, reserves the needed resources.
        :return: True if the robot must build a foobar, False otherwise.
        """
        async with self.foobartory.foo_lock:
            async with self.foobartory.bar_lock:
                if (
                    not self.foobartory.foo_queue.empty()
                    and not self.foobartory.bar_queue.empty()
                ):
                    # Let's reserve 1 foo and 1 bar before moving
                    await self.reserve_foo()
                    await self.reserve_bar()
                    return True
        return False

    async def check_and_reserve_sell_foobar(self) -> bool:
        """
        Checks if the robot must sell a foobar.
        If it's the case, reserves the needed resources.
        :return: True if the robot must sell a foobar, False otherwise.
        """
        async with self.foobartory.foobar_lock:
            if self.foobartory.foobar_queue.qsize() >= cfg.MAX_FOOBAR_TO_SELL:
                # We reserve MAX_FOOBAR_TO_SELL foobars because
                # we can't know yet how many we will sell
                await self.reserve_foobar(cfg.MAX_FOOBAR_TO_SELL)
                return True
        return False

    async def check_and_reserve_buy_robot(self) -> bool:
        """
        Checks if the robot must buy a robot.
        If it's the case, reserves the needed resources.
        :return: True if the robot must buy a robot, False otherwise.
        """
        async with self.foobartory.foo_lock:
            async with self.foobartory.money_lock:
                if (
                    self.foobartory.foo_queue.qsize() >= cfg.ROBOT_FOO_COST
                    and self.foobartory.money >= cfg.ROBOT_MONEY_COST
                ):
                    # Let's reserve foos and money before moving
                    await self.reserve_foo(cfg.ROBOT_FOO_COST)
                    async with self.foobartory.reserved_money_lock:
                        self.reserve_money(cfg.ROBOT_MONEY_COST)
                    return True
        return False

    @wait_if_moving
    async def mine_foo(self) -> None:
        await asyncio.sleep(cfg.MINE_FOO_TIME / cfg.SPEED_MULTIPLIER)
        await self.foobartory.foo_queue.put(Foo())

    @wait_if_moving
    async def mine_bar(self) -> None:
        duration = random.uniform(cfg.MINE_BAR_MIN_TIME, cfg.MINE_BAR_MAX_TIME)
        await asyncio.sleep(duration / cfg.SPEED_MULTIPLIER)
        await self.foobartory.bar_queue.put(Bar())

    @wait_if_moving
    async def build_foobar(self) -> None:
        success = True if random.random() < cfg.BUILD_FOOBAR_CHANCE else False

        # Gets foo and bar from the reserved parts
        bar = await self.foobartory.reserved_bar.get()
        foo = await self.foobartory.reserved_foo.get()
        await asyncio.sleep(cfg.BUILD_FOOBAR_TIME / cfg.SPEED_MULTIPLIER)
        if success:
            await self.foobartory.foobar_queue.put(Foobar(f"{foo.uid}.{bar.uid}"))
        else:
            await self.foobartory.bar_queue.put(bar)

    @wait_if_moving
    async def sell_foobar(self) -> None:
        nb_to_sell = random.randint(cfg.MIN_FOOBAR_TO_SELL, cfg.MAX_FOOBAR_TO_SELL)
        await asyncio.sleep(cfg.SELL_FOOBAR_TIME / cfg.SPEED_MULTIPLIER)

        async with self.foobartory.money_lock:
            self.foobartory.money += nb_to_sell * cfg.FOOBAR_SELLING_PRICE

        # Removes the sold foobars from the reserved queue
        self.remove_reserved_foobar(nb_to_sell)
        # Return bars that have not been sold
        nb_foobar_not_sold = cfg.MAX_FOOBAR_TO_SELL - nb_to_sell
        await self.return_reserved_foobar(nb_foobar_not_sold)

    @wait_if_moving
    async def buy_robot(self) -> None:
        # Remove the reserved money
        async with self.foobartory.reserved_money_lock:
            self.remove_reserved_money(cfg.ROBOT_MONEY_COST)
        # Remove the reserved foos
        self.remove_reserved_foo(cfg.ROBOT_FOO_COST)

        await self.foobartory.add_robot()

    # All reserve/remove/return methods presume that resources are present and locked
    def reserve_money(self, count: int = 1) -> None:
        self.foobartory.money -= count
        self.foobartory.reserved_money += count

    def remove_reserved_money(self, count: int = 1) -> None:
        self.foobartory.reserved_money -= count

    async def reserve_foo(self, count: int = 1):
        for _ in range(count):
            await self.foobartory.reserved_foo.put(
                self.foobartory.foo_queue.get_nowait()
            )

    def remove_reserved_foo(self, count: int = 1) -> None:
        for _ in range(count):
            self.foobartory.reserved_foo.get_nowait()

    async def reserve_bar(self, count: int = 1) -> None:
        for _ in range(count):
            await self.foobartory.reserved_bar.put(
                self.foobartory.bar_queue.get_nowait()
            )

    async def reserve_foobar(self, count: int = 1) -> None:
        for _ in range(count):
            await self.foobartory.reserved_foobar.put(
                self.foobartory.foobar_queue.get_nowait()
            )

    async def return_reserved_foobar(self, count: int = 1) -> None:
        for _ in range(count):
            await self.foobartory.foobar_queue.put(
                self.foobartory.reserved_foobar.get_nowait()
            )

    def remove_reserved_foobar(self, count: int = 1) -> None:
        for _ in range(count):
            self.foobartory.reserved_foobar.get_nowait()
