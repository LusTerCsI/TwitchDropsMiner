from __future__ import annotations

import ctypes
import logging
import argparse
from typing import Optional

from twitch import Twitch
from version import __version__
from constants import FORMATTER, LOG_PATH, WINDOW_TITLE


class ParsedArgs(argparse.Namespace):
    _verbose: int
    _debug_ws: bool
    _debug_gql: bool
    log: bool
    tray: bool
    game: Optional[str]

    @property
    def logging_level(self) -> int:
        return {
            0: logging.ERROR,
            1: logging.WARNING,
            2: logging.INFO,
            3: logging.DEBUG,
        }.get(self._verbose, logging.DEBUG)

    @property
    def debug_ws(self) -> int:
        """
        If the debug flag is True, return DEBUG.
        If the main logging level is DEBUG, return INFO to avoid seeing raw messages.
        Otherwise, return NOTSET to inherit the global logging level.
        """
        if self._debug_ws:
            return logging.DEBUG
        elif self._verbose >= 3:
            return logging.INFO
        return logging.NOTSET

    @property
    def debug_gql(self) -> int:
        if self._debug_gql:
            return logging.DEBUG
        elif self._verbose >= 3:
            return logging.INFO
        return logging.NOTSET


# check if we're not already running
try:
    exists = ctypes.windll.user32.FindWindowW(None, WINDOW_TITLE)
except AttributeError:
    # we're not on Windows - continue
    exists = False
if exists:
    # already running - exit
    quit()
# handle input parameters
parser = argparse.ArgumentParser(
    "Twitch Drops Miner (by DevilXD).exe",
    description="A program that allows you to mine timed drops on Twitch.",
)
parser.add_argument("-V", "--version", action="version", version=f"v{__version__}")
parser.add_argument("-v", dest="_verbose", action="count", default=0)
parser.add_argument("--debug-ws", dest="_debug_ws", action="store_true")
parser.add_argument("--debug-gql", dest="_debug_gql", action="store_true")
parser.add_argument("-g", "--game", default=None)
parser.add_argument("--tray", action="store_true")
parser.add_argument("-l", "--log", action="store_true")
options: ParsedArgs = parser.parse_args(namespace=ParsedArgs())
# handle logging stuff
if options.logging_level > logging.DEBUG:
    # redirect the root logger into a NullHandler, effectively ignoring all logging calls
    # that aren't ours. This always runs, unless the main logging level is DEBUG or lower.
    logging.getLogger().addHandler(logging.NullHandler())
logger = logging.getLogger("TwitchDrops")
logger.setLevel(options.logging_level)
if options.log:
    handler = logging.FileHandler(LOG_PATH)
    handler.setFormatter(FORMATTER)
    logger.addHandler(handler)
logging.getLogger("TwitchDrops.gql").setLevel(options.debug_gql)
logging.getLogger("TwitchDrops.websocket").setLevel(options.debug_ws)
# client run
client = Twitch(options)
client.start()
