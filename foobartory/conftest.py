import pytest

from foobartory import config
from foobartory.factory import Foobartory
from foobartory.models import Robot

config.SPEED_MULTIPLIER = 5000


@pytest.fixture
def foobartory():
    return Foobartory()


@pytest.fixture
def robot(foobartory):
    robot = Robot(1, foobartory)
    foobartory.robots.append(robot)
    return robot
