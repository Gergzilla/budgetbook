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
    options = parser.parse_args()
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
    def __init__(self, name):
        self.name = __name__
        self.log = logging.getLogger(str(name))
        if showconsole:
            self.log.addHandler(console)
        # logging.getLogger(self.log)

    def __str__(self):
        return self.name

    def show_level(self):
        return f"current Debug Level: {level})"
