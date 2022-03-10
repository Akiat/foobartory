import argparse
import asyncio

from foobartory import config as cfg
from foobartory.factory import Foobartory


async def start_factory() -> None:
    """
    Instantiate the factory, add firsts robots and start the Factory
    """
    foobartory = Foobartory()

    # Add the first robots
    for _ in range(cfg.STARTING_ROBOT_NUMBER):
        await foobartory.add_robot()

    await foobartory.start()


def parse_args():
    """
    Define the args parser and parse arguments
    :return: the arguments
    """
    parser = argparse.ArgumentParser(description="Foobartory, a great foobar factory!")
    parser.add_argument(
        "--quick",
        dest="quick",
        nargs="?",
        type=int,
        const=10,
        help="Activate quick mode with the given speed multiplier value (default 10).",
        metavar="SPEED MULTIPLIER",
    )
    return parser.parse_args()


def start(args=None):
    """
    The entry point, start the event loop
    :param args: Only used to send params from pytest
    """
    if not args:
        args = parse_args()

    if args.quick:
        cfg.SPEED_MULTIPLIER = args.quick

    try:
        # Start the factory
        asyncio.run(start_factory())
    except KeyboardInterrupt:
        if not args.quick:
            print("Too slow? Have you tried the --quick option?")
        else:
            print("See you!")
