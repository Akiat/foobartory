import asyncio
from asyncio import Queue
from time import gmtime, strftime
from timeit import default_timer as timer

from rich.console import Console
from rich.live import Live
from rich.table import Table

from foobartory import config as cfg
from foobartory import constants
from foobartory.models import Bar, Foo, Foobar, Robot


class Foobartory:
    """
    The class that manage the Foobartory and its robots
    """

    def __init__(self):
        self.running: bool = True
        self.robots: list[Robot] = []

        self.money: int = 0
        self.reserved_money: int = 0

        # queues for producer/consumer flow
        self.foo_queue: Queue[Foo] = Queue()
        self.bar_queue: Queue[Bar] = Queue()
        self.foobar_queue: Queue[Foobar] = Queue()

        # queues for reserved materials flow
        self.reserved_foo: Queue[Foo] = Queue()
        self.reserved_bar: Queue[Bar] = Queue()
        self.reserved_foobar: Queue[Foobar] = Queue()

    async def generate_table(self) -> Table:
        """
        Generates the displayed table
        """
        table = Table()
        table.expand = True
        table.title_style = "bold green"
        table.title = f"""\
Foo: [bright_cyan]{self.foo_queue.qsize()}[/]\
([magenta]{self.reserved_foo.qsize()}[/]) | \
Bar: [bright_cyan]{self.bar_queue.qsize()}[/]\
([magenta]{self.reserved_bar.qsize()}[/]) | \
Foobar: [bright_cyan]{self.foobar_queue.qsize()}[/]\
([magenta]{self.reserved_foobar.qsize()}[/]) | \
Money: [bright_cyan]{self.money}[/]\
([magenta]{self.reserved_money}[/])"""

        table.add_column("Robot No.", style="bright_magenta", ratio=2)
        table.add_column("Current Job", style="yellow3", ratio=8)

        for i, _ in enumerate(self.robots):
            table.add_row(
                f"{self.robots[i].uid}",
                f"{constants.jobs[self.robots[i].current_job]}",
            )
        return table

    async def start(self) -> None:
        """
        Displays and updates the table and information
        as long as the factory is running
        """
        start = timer()

        with Live(refresh_per_second=4) as live:
            while self.running:
                live.update(await self.generate_table())
                await asyncio.sleep(0.1)

            # Just updating a last time the info table to have the final state
            live.update(await self.generate_table())

        Console().print(
            f"Your Foobartory has now {len(self.robots)} robots congrats!",
            justify="center",
            style="bold green",
        )

        elapsed_time = int((timer() - start) * cfg.SPEED_MULTIPLIER)
        str_time = strftime("[cyan]%M[/]m [cyan]%S[/]s", gmtime(elapsed_time))
        Console().print(
            f"Real elapsed time: {str_time}.", justify="center", style="bold green"
        )

    async def add_robot(self) -> None:
        """
        Add one robot to the Foobartory and start it.
        Also stop the Foobartory and robots if MAX_ROBOT_NUMBER is reached.
        """
        self.robots.append(robot := Robot(uid=len(self.robots) + 1, foobartory=self))

        if len(self.robots) >= cfg.MAX_ROBOT_NUMBER:
            await self.stop()
        else:
            asyncio.create_task(robot.start())

    async def stop(self) -> None:
        """
        Stop the foobartory and the robots.
        """
        for i, _ in enumerate(self.robots):
            await self.robots[i].stop()
        self.running = False
