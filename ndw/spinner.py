# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import contextlib
import sys
import time
import multiprocessing


class IndicatorThread(object):
    """Creates a visual indicator while normally performing actions."""

    def __init__(self, system=True):
        """System Operations Available on Load.

        :param system:
        """

        self.system = system

    def indicator(self):
        """Produce the spinner."""

        while self.system:
            busy_chars = ['|', '/', '-', '\\']
            for _cr in busy_chars:
                # Fixes Errors with OS X due to no sem_getvalue support
                _qz = 'Please Wait... '
                sys.stdout.write('\rProcessing - [ %(spin)s ] - %(qsize)s'
                                 % {"qsize": _qz, "spin": _cr})
                sys.stdout.flush()
                time.sleep(.1)
                self.system = self.system

    def indicator_thread(self):
        """indicate that we are performing work in a thread."""

        job = multiprocessing.Process(target=self.indicator)
        job.start()
        return job


@contextlib.contextmanager
def spinner():
    """Show a fancy spinner while we have work running.

    :yeild:
    """

    set_itd = IndicatorThread()
    itd = None
    try:
        itd = set_itd.indicator_thread()
        yield
    finally:
        set_itd.system = False
        if itd is not None:
            itd.terminate()










