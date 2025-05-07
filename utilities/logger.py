#!bin/env/python

"""Usage - from main code file add 'from loggers import LoggingHandler' then on execution pass the argument noted below"""

import logging
import argparse
import requests

# the following line is responsible for suppressing the warning.

requests.packages.urllib3.disable_warnings()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-log",
    "--log",
    default="warning",
    help=("Provide logging level. " "Example --log debug', default='warning'"),
    )
options = parser.parse_args()
levels = {

    "critical": logging.CRITICAL,
    "error": logging.ERROR,
    "warn": logging.WARNING,
    "warning": logging.WARNING,
    "info": logging.INFO,
    "debug": logging.DEBUG,
    }
level = levels.get(options.log.lower())

if level is None:
    raise ValueError(
        f"log level given: {options.log}"
        f" -- must be one of: {' | '.join(levels.keys())}"
    )

logging.basicConfig(level=level)

# Create a base class
class LoggingHandler:
    def __init__(self, name):
        logID = str(name)
        self.log = logging.getLogger(str(name))
        # self.log = logging.getLogger(self.__class__.__name__)
