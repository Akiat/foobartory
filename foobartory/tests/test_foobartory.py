import pytest

import foobartory.config as cfg


@pytest.mark.asyncio
async def test_foobartory(foobartory, capsys):
    assert len(foobartory.robots) == 0
    # Add the first robots
    for _ in range(cfg.STARTING_ROBOT_NUMBER):
        await foobartory.add_robot()
    assert len(foobartory.robots) == cfg.STARTING_ROBOT_NUMBER
    await foobartory.start()
    res = capsys.readouterr()
    assert "Your Foobartory has now" in res.out
