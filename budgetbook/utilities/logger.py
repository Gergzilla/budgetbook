#!bin/env/python

"""Usage - from main code file add 'from loggers import LoggingHandler' then on execution pass the
argument noted below"""

import logging
import os
import sys
import argparse
import requests
import urllib3


# the following line is responsible for suppressing the warning.
# print(os.path.abspath(__file__).split())
logfilename = os.path.abspath(
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs/runninglog.txt")
)
# print(os.path.join(os.path.dirname(__file__), "..", "logs/runninglog.txt"))
# if os.path.exists(logfilename):
#     print("yay")
# else:
#     print("cant find it")
urllib3.disable_warnings()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-log",
    "--log",
    default="warning",
    nargs="?",
    help="Provide logging level. " "Example --log debug', default='warning'",
)
parser.add_argument(
    "-c",
    "--console",
    default="false",
    nargs="?",
    help="Enables output of log messages to the console, default is logfile in /logs folder",
)
try:
    options, passthrough_args = parser.parse_known_args()
    # options = parser.parse_args()
except ValueError as e:
    print(f"Logger module exiting with exception: {e}")
    sys.exit(1)

levels = {
    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
}
# parse the input arguments and assign relevant values
level = levels.get(options.log.lower())
showconsole = options.console.lower()
if level is None:
    raise ValueError(
        f"log level given: {options.log}"
        f" -- must be one of: {' | '.join(levels.keys())}"
    )

logging.basicConfig(
    level=level,
    format="%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
    datefmt="%m-%d %H:%M",
    filename=logfilename,
    filemode="a",
)
formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
console = logging.StreamHandler()
console.setLevel(level)
console.setFormatter(formatter)


class LoggingHandler:
    """my doc is my string, verify me"""

    def __init__(self, name, level=level):
        # fixed this, it should have been name not __name__ so it picks up the source name
        self.name = name
        # print(f"where the hell is my name from? {self.name}")
        self.log = logging.getLogger(str(self.name))
        self.level = level
        if showconsole:
            self.log.addHandler(console)
        # logging.getLogger(self.log)

    def __str__(self):
        return self.name

    def get_logging_level(self):
        return self.level

    def show_logging_level(self):
        """my doc is my string, verify me"""
        return f"current logging Level: {self.level}:{logging.getLevelName(self.level)}"
