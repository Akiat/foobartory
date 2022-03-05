# Foobartory

The foobartory is a robot factory where foo, bar, and foobar are made.

## Installation

This project has only been tested with python >= 3.10.
`````shell
# Clone the git repository
$ git clone https://github.com/Akiat/foobartory.git

# Install requirements
$ cd foobartory && pip install -r requirements.txt

# (OPTIONAL) - Only if you want to launch the tests
$ pytest foobartory

# (OPTIONAL) Install foobartory
$ pip install .

# Use it
## If you installed it
$ foobartory --help
## Otherwise
$ python -m foobartory --help
`````

## Usage
````shell
$ foobartory --help
usage: foobartory [-h] [--quick [SPEED MULTIPLIER]]

Foobartory, a great foobar factory!

options:
  -h, --help            show this help message and exit
  --quick [SPEED MULTIPLIER]
                        Activate quick mode with the given speed multiplier value (default 10).
````

### Example
````shell
$ foobartory
# Quick mode, 10 times faster by default
$ foobartory --quick
# Quick mode, 100 times faster
$ foobartory --quick 100
````

## Configuration
You can tweak some parameters in foobartory/config.py

| **Name**                | **Default value** | **Explanation**                                                 |
| ----------------------- | ----------------- | --------------------------------------------------------------- |
| SPEED_MULTIPLIER        | 1                 | The execution speed is multiplied by this value                 |
| STARTING_ROBOT_NUMBER   | 2                 | The number of robots we have at the beginning                   |
| MAX_ROBOT_NUMBER        | 30                | The maximum number of robots                                    |
| ROBOT_MONEY_COST        | 3                 | How many euros a robot costs                                    |
| ROBOT_FOO_COST          | 6                 | How many foos a robot costs                                     |
| FOOBAR_SELLING_PRICE    | 1                 | How many euros we get if we sell a robot                        |
| MIN_FOOBAR_TO_SELL      | 1                 | The minimum amount of foobar that can be sold at once           |
| MAX_FOOBAR_TO_SELL      | 5                 | The maximum amount of foobar that can be sold at once           |
| BUILD_FOOBAR_CHANCE     | 0.6               | The chance for a robot to succeed in making a foobar (1 = 100%) |
| CHANGE_JOB_TIME         | 5                 | The time a robot spends during a move                           |
| MINE_FOO_TIME           | 1                 | The time a robot spends to craft a foo                          |
| MINE_BAR_MIN_TIME       | 0.5               | The minimum time a robot spends to craft a bar                  |
| MINE_BAR_MAX_TIME       | 2                 | The maximum time a robot spends to craft a bar                  |
| BUILD_FOOBAR_TIME       | 2                 | The time a robot spends to craft a foobar                       |
| SELL_FOOBAR_TIME        | 10                | The time a robot spends to sell foobars                         |


