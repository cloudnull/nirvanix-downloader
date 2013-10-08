# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================

import json
import os
import sys
import urlparse

import ndw

from ndw import actions
from ndw import arguments
from ndw import conn_utils
from ndw import rax_auth_utils
from ndw import spinner
from ndw.constants import LOG


def run():
    """Run the application."""

    def get_sesstoken(auth_url, auth_path):
        """Get session token."""

        conn = conn_utils.open_connection(auth_url)
        resp, read = conn_utils.request(conn, auth_path, method='GET')
        json_response = json.loads(read)

        # Get Session
        return json_response.get('SessionToken')

    if len(sys.argv) <= 1:
        raise SystemExit('Give me something to do and I will do it')

    # Load config, args
    args = arguments.args()
    base_url = args['node_url']

    # Authentication
    auth_url = urlparse.urlsplit('%s/ws/Authentication/Login.ashx' % base_url)
    auth_query = (
        '?appKey=%s&username=%s&password=%s&output=json'
        % (args['appkey'], args['username'], args['password'])
    )
    auth_path = '%s%s' % (auth_url.path, auth_query)

    # Get Session
    sessionToken = get_sesstoken(auth_url, auth_path)
    print('This is your Nirvanix Session Token:\t%s' % sessionToken)

    # Set folder path
    folder_url = urlparse.urlsplit('%s/ws/IMFS/ListFolder.ashx' % base_url)

    with spinner.spinner():
        # Get file list ready
        files = actions.file_finder(sessionToken, folder_url, args)
        # Get all of the unique Directories
        unique_dirs = []
        for obj in files:
            unique_dirs.append(
                obj.split(os.path.basename(obj))[0].rstrip(os.sep)
            )

    # notify on the number of files
    print 'Total Number of files found : %s' % len(files)

    # Make the local Directories
    payload = None
    action = None
    if args.get('download') is True:
        LOG.info('Starting Local Download job.')
        # Fetch the local Directories
        unique_dirs = list(
            set(unique_dirs)
        )
        for u_dir in unique_dirs:
            directory = '%s%s%s' % (
                args['work_dir'].rstrip(os.sep), os.sep, u_dir
            )
            actions.mkdir_p(directory)
        action = getattr(conn_utils, 'local_download')
    elif args.get('to_rax') is not None:
        LOG.info('Starting Rackspace Migration job.')
        payload = ndw.prep_payload(
            rax_auth_utils.authenticate(args), args
        )
        # Create Container
        conn_utils.container_create(payload)
        action = getattr(conn_utils, 'rax_stream')
    elif args.get('delete') is not None:
        LOG.info('Starting Nivanix Delete Job.')
        action = getattr(conn_utils, 'nirvanix_delete')
        files = unique_dirs
    elif args.get('list') is not None:
        unique_dirs = list(
            set(unique_dirs)
        )
        for u_dir in unique_dirs:
            print(u_dir)

    if action is not None:
        with spinner.spinner():
            ndw.threader(
                job_action=action,
                files=files,
                args=args,
                sessionToken=sessionToken,
                payload=payload
            )
    LOG.info('============== Job Complete ==============')
    print('Job is complete.')
