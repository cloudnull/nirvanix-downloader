# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import multiprocessing
import time
import random


def prep_payload(auth, args):
    """Create payload dictionary.

    :param auth:
    :param container:
    :return (dict, dict): payload and headers
    """

    # Unpack the values from Authentication
    token, tenant, user, inet, enet = auth

    # Get the headers ready
    headers = {'X-Auth-Token': token}

    if args.get('internal'):
        url = inet
    else:
        url = enet

    # Set the upload Payload
    return {'c_name': args['container'],
            'tenant': tenant,
            'headers': headers,
            'user': user,
            'url': url}


def retryloop(attempts, timeout=None, delay=None, backoff=1):
    """Enter the amount of retries you want to perform.

    The timeout allows the application to quit on "X".
    delay allows the loop to wait on fail. Useful for making REST calls.

    Example:
        Function for retring an action.
        for retry in retryloop(attempts=10, timeout=30, delay=1, backoff=1):
            something
            if somecondition:
                retry()

    :param attempts:
    :param timeout:
    :param delay:
    :param backoff:
    """

    starttime = time.time()
    success = set()
    for _ in range(attempts):
        success.add(True)
        yield success.clear
        if success:
            return
        duration = time.time() - starttime
        if timeout is not None and duration > timeout:
            break
        if delay:
            time.sleep(delay)
            delay = delay * backoff
    print('RetryError: FAILED TO PROCESS after "%s" Attempts' % attempts)


def threader(job_action, files, args, sessionToken, payload=None, threads=25):
    queue = multiprocessing.Queue()
    for file in files:
        queue.put(file)

    concurrency = threads
    if len(files) < concurrency:
        concurrency = len(files)

    if all([args is None, sessionToken is None, payload is None]):
        jobs = [multiprocessing.Process(
            target=job_action, args=(queue,)
        ) for _ in xrange(concurrency)]
    elif payload is None:
        jobs = [multiprocessing.Process(
            target=job_action, args=(sessionToken, args, queue,)
        ) for _ in xrange(concurrency)]
    else:
        jobs = [multiprocessing.Process(
            target=job_action, args=(sessionToken, args, queue, payload)
        ) for _ in xrange(concurrency)]

    join_jobs = []
    for _job in jobs:
        join_jobs.append(_job)
        _job.Daemon = True
        _job.start()

    for job in join_jobs:
        job.join()


def stupid_hack(most=5, wait=None):
    """Return a random time between 1 - 10 Seconds."""

    # Stupid Hack For Public Cloud so it is not overwhelmed with API requests.
    if wait is not None:
        time.sleep(wait)
    else:
        time.sleep(random.randrange(1, most))
