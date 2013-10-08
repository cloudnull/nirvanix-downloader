#!/usr/bin/env python
# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import os

from ndw import constants
from ndw import logger


def executable():
    """Run the application."""

    constants.load_constants(logger, os.getenv('HOME'))
    from ndw import run
    run.run()

if __name__ == "__main__":
    executable()
