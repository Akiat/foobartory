import asyncio
from functools import wraps

from foobartory import config as cfg
from foobartory import constants


def wait_if_moving(job):
    """Wait if robot needs to move, and register the current job"""

    @wraps(job)
    async def wrapper(self, *args, **kwargs):
        if self.current_job != job.__name__:
            self.current_job = constants.MOVING
            await asyncio.sleep(cfg.CHANGE_JOB_TIME / cfg.SPEED_MULTIPLIER)

        self.current_job = job.__name__ if self.running else constants.SLEEPING
        return await job(self, *args, **kwargs)

    return wrapper
