import pytest

import foobartory.config as cfg
from foobartory.models import Bar, Foo, Foobar


def test_str(robot):
    assert str(robot) == "Robot 1"


@pytest.mark.asyncio
async def test_stop(robot):
    assert robot.running is True
    await robot.stop()
    assert robot.running is False


@pytest.mark.asyncio
async def test_check_and_reserve_build_foobar(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.bar_queue.empty() is True
    await robot.foobartory.foo_queue.put(Foo())
    await robot.foobartory.bar_queue.put(Bar())
    res = await robot.check_and_reserve_build_foobar()
    assert res is True
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.bar_queue.empty() is True
    assert robot.foobartory.reserved_foo.empty() is False
    assert robot.foobartory.reserved_bar.empty() is False


@pytest.mark.asyncio
async def test_check_and_reserve_build_foobar_no_foo(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.bar_queue.empty() is True
    await robot.foobartory.bar_queue.put(Bar())
    res = await robot.check_and_reserve_build_foobar()
    assert res is False
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.bar_queue.empty() is False
    assert robot.foobartory.reserved_foo.empty() is True
    assert robot.foobartory.reserved_bar.empty() is True


@pytest.mark.asyncio
async def test_check_and_reserve_build_foobar_no_bar(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.bar_queue.empty() is True
    await robot.foobartory.foo_queue.put(Bar())
    res = await robot.check_and_reserve_build_foobar()
    assert res is False
    assert robot.foobartory.foo_queue.empty() is False
    assert robot.foobartory.bar_queue.empty() is True
    assert robot.foobartory.reserved_foo.empty() is True
    assert robot.foobartory.reserved_bar.empty() is True


@pytest.mark.asyncio
async def test_check_and_reserve_sell_foobar(robot):
    assert robot.foobartory.foobar_queue.empty() is True
    for _ in range(cfg.MAX_FOOBAR_TO_SELL):
        await robot.foobartory.foobar_queue.put(Foobar("Fake-UID"))
    assert robot.foobartory.foobar_queue.qsize() == cfg.MAX_FOOBAR_TO_SELL
    res = await robot.check_and_reserve_sell_foobar()
    assert res is True
    assert robot.foobartory.foobar_queue.empty() is True
    assert robot.foobartory.reserved_foobar.qsize() == cfg.MAX_FOOBAR_TO_SELL


@pytest.mark.asyncio
async def test_check_and_reserve_sell_foobar_not_enough_foobar(robot):
    assert robot.foobartory.foobar_queue.empty() is True
    for _ in range(cfg.MAX_FOOBAR_TO_SELL - 1):
        await robot.foobartory.foobar_queue.put(Foobar("Fake-UID"))
    assert robot.foobartory.foobar_queue.qsize() == cfg.MAX_FOOBAR_TO_SELL - 1
    res = await robot.check_and_reserve_sell_foobar()
    assert res is False
    assert robot.foobartory.foobar_queue.qsize() == cfg.MAX_FOOBAR_TO_SELL - 1
    assert robot.foobartory.reserved_foobar.empty() is True


@pytest.mark.asyncio
async def test_check_and_reserve_buy_robot(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.money == 0
    for _ in range(cfg.ROBOT_FOO_COST):
        await robot.foobartory.foo_queue.put(Foo())
    robot.foobartory.money += cfg.ROBOT_MONEY_COST
    assert robot.foobartory.foo_queue.qsize() == cfg.ROBOT_FOO_COST
    assert robot.foobartory.money == cfg.ROBOT_MONEY_COST
    res = await robot.check_and_reserve_buy_robot()
    assert res is True
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.money == 0
    assert robot.foobartory.reserved_money == cfg.ROBOT_MONEY_COST
    assert robot.foobartory.reserved_foo.qsize() == cfg.ROBOT_FOO_COST


@pytest.mark.asyncio
async def test_check_and_reserve_buy_robot_not_enough_money(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.money == 0
    for _ in range(cfg.ROBOT_FOO_COST):
        await robot.foobartory.foo_queue.put(Foo())
    robot.foobartory.money += cfg.ROBOT_MONEY_COST - 1
    assert robot.foobartory.foo_queue.qsize() == cfg.ROBOT_FOO_COST
    assert robot.foobartory.money == cfg.ROBOT_MONEY_COST - 1
    res = await robot.check_and_reserve_buy_robot()
    assert res is False
    assert robot.foobartory.foo_queue.qsize() == cfg.ROBOT_FOO_COST
    assert robot.foobartory.money == cfg.ROBOT_MONEY_COST - 1
    assert robot.foobartory.reserved_money == 0
    assert robot.foobartory.reserved_foo.empty() is True


@pytest.mark.asyncio
async def test_check_and_reserve_buy_robot_not_enough_foo(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.money == 0
    for _ in range(cfg.ROBOT_FOO_COST - 1):
        await robot.foobartory.foo_queue.put(Foo())
    robot.foobartory.money += cfg.ROBOT_MONEY_COST
    assert robot.foobartory.foo_queue.qsize() == cfg.ROBOT_FOO_COST - 1
    assert robot.foobartory.money == cfg.ROBOT_MONEY_COST
    res = await robot.check_and_reserve_buy_robot()
    assert res is False
    assert robot.foobartory.foo_queue.qsize() == cfg.ROBOT_FOO_COST - 1
    assert robot.foobartory.money == cfg.ROBOT_MONEY_COST
    assert robot.foobartory.reserved_money == 0
    assert robot.foobartory.reserved_foo.empty() is True


@pytest.mark.asyncio
async def test_mine_foo(robot):
    assert robot.foobartory.foo_queue.empty() is True
    await robot.mine_foo()
    assert robot.foobartory.foo_queue.empty() is False


@pytest.mark.asyncio
async def test_mine_bar(robot):
    assert robot.foobartory.bar_queue.empty() is True
    await robot.mine_bar()
    assert robot.foobartory.bar_queue.empty() is False


@pytest.mark.asyncio
async def test_build_foobar(robot):
    assert robot.foobartory.reserved_foo.empty() is True
    assert robot.foobartory.reserved_bar.empty() is True
    await test_check_and_reserve_build_foobar(robot)
    await robot.build_foobar()
    # Either we have a foobar, or we have a bar and more foo
    assert (
        robot.foobartory.foobar_queue.empty() is False
        or (
            robot.foobartory.bar_queue.empty() is False
            and robot.foobartory.foo_queue.empty() is True
        )
    ) is True


@pytest.mark.asyncio
async def test_sell_foobar(robot):
    assert robot.foobartory.reserved_foobar.empty() is True
    await test_check_and_reserve_sell_foobar(robot)
    await robot.sell_foobar()
    max_unsold = cfg.MAX_FOOBAR_TO_SELL - cfg.MIN_FOOBAR_TO_SELL
    assert (0 <= robot.foobartory.foobar_queue.qsize() <= max_unsold) is True


@pytest.mark.asyncio
async def test_buy_robot(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.money == 0
    await test_check_and_reserve_buy_robot(robot)
    await robot.buy_robot()
    assert robot.foobartory.reserved_money == 0
    assert robot.foobartory.reserved_foo.empty() is True


def test_reserve_money(robot):
    assert robot.foobartory.money == 0
    assert robot.foobartory.reserved_money == 0
    robot.foobartory.money += 3
    robot.reserve_money(3)
    assert robot.foobartory.money == 0
    assert robot.foobartory.reserved_money == 3


def test_remove_reserve_money(robot):
    assert robot.foobartory.reserved_money == 0
    robot.foobartory.reserved_money += 3
    robot.remove_reserved_money(3)
    assert robot.foobartory.reserved_money == 0


@pytest.mark.asyncio
async def test_reserve_foo(robot):
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.reserved_foo.empty() is True
    for _ in range(3):
        await robot.foobartory.foo_queue.put(Foo())
    await robot.reserve_foo(3)
    assert robot.foobartory.foo_queue.empty() is True
    assert robot.foobartory.reserved_foo.qsize() == 3


@pytest.mark.asyncio
async def test_reserve_bar(robot):
    assert robot.foobartory.bar_queue.empty() is True
    assert robot.foobartory.reserved_bar.empty() is True
    for _ in range(3):
        await robot.foobartory.bar_queue.put(Bar())
    await robot.reserve_bar(3)
    assert robot.foobartory.bar_queue.empty() is True
    assert robot.foobartory.reserved_bar.qsize() == 3


@pytest.mark.asyncio
async def test_reserve_foobar(robot):
    assert robot.foobartory.foobar_queue.empty() is True
    assert robot.foobartory.reserved_foobar.empty() is True
    for _ in range(3):
        await robot.foobartory.foobar_queue.put(Foobar("Fake-UID"))
    await robot.reserve_foobar(3)
    assert robot.foobartory.foobar_queue.empty() is True
    assert robot.foobartory.reserved_foobar.qsize() == 3


@pytest.mark.asyncio
async def test_return_reserved_foobar(robot):
    assert robot.foobartory.reserved_foobar.empty() is True
    for _ in range(3):
        await robot.foobartory.reserved_foobar.put(Foobar("Fake-UID"))
    await robot.return_reserved_foobar(3)
    assert robot.foobartory.reserved_foobar.qsize() == 0


@pytest.mark.asyncio
async def test_remove_reserved_foobar(robot):
    assert robot.foobartory.reserved_foobar.empty() is True
    for _ in range(3):
        await robot.foobartory.reserved_foobar.put(Foobar("Fake-UID"))
    robot.remove_reserved_foobar(3)
    assert robot.foobartory.reserved_foobar.qsize() == 0
