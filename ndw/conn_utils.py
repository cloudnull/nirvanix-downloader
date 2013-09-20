# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================
import httplib
import tempfile
import os
import json
import traceback
import urllib
import urlparse

import ndw


def open_connection(url):
    """Open an Http Connection and return the connection object.

    :param url:
    :return conn:
    """

    try:
        if url.scheme == 'https':
            conn = httplib.HTTPSConnection(url.netloc)
        else:
            conn = httplib.HTTPConnection(url.netloc)
    except httplib.InvalidURL as exc:
        msg = 'ERROR: Making connection to %s\nREASON:\t %s' % (url, exc)
        raise httplib.CannotSendRequest(msg)
    else:
        return conn


def request(conn, rpath, method='GET', body=None, headers=None):
    """Open a Connection."""
    try:
        if headers is None:
            headers = {}
        # conn.set_debuglevel(1)
        if body is not None:
            conn.request(method, rpath, body=body, headers=headers)
        else:
            conn.request(method, rpath, headers=headers)
    except Exception:
        raise SystemExit('Connection issues, %s ' % traceback.format_exc())
    else:
        resp = conn.getresponse()
        return resp, resp.read()
    finally:
        conn.close()


# Download Files
def downloader(sessionToken=None, args=None, obj=None, tempf=None):
    if tempf is None:
        tempf = obj
        local_path = '%s%s%s' % (
            args['work_dir'].rstrip(os.sep), os.sep, tempf.lstrip(os.sep)
        )
    else:
        local_path = '%s' % tempf

    file_path = urllib.quote(obj)
    storage_url = urlparse.urlsplit(
        '%s/ws/IMFS/GetOptimalUrls.ashx' % args['node_url']
    )
    storage_query = (
        '?sessionToken=%s&filePath=%s&expiration=500&output=json'
        % (sessionToken, file_path)
    )
    storage_path = '%s%s' % (storage_url.path, storage_query)
    for retry in ndw.retryloop(attempts=10, delay=2, backoff=1):
        conn = open_connection(storage_url)
        try:
            resp, read = request(conn, storage_path, method='GET')
            dw_url = urlparse.urlsplit(
                json.loads(read).get('Download')[0].get('DownloadURL')
            )
            if resp.status >= 300:
                print(
                    'ERROR in Download Node API request. ERROR: %s\n%s'
                    '\nSystem will retry' % (resp.status, resp.msg)
                )
                retry()
        except Exception as exp:
            print(
                'FAILURE Accessing the Nirvanix API\nERROR: %s,\n'
                'System will retry' % exp
            )
            retry()
    for retry in ndw.retryloop(attempts=10, delay=2, backoff=1):
        conn = open_connection(dw_url)
        try:
            resp, read = request(conn, dw_url.path, method='GET')
            if resp.status >= 300:
                print(
                    'ERROR in Processing Download. ERROR: %s\n%s'
                    '\nSystem will retry' % (resp.status, resp.msg)
                )
                retry()
            else:
                with open(local_path, 'wb') as f:
                    f.write(read)
        except Exception as exp:
            print(
                'FAILURE in Downloading from Nirvanix\nERROR: %s,\n'
                'System will retry' % exp
            )
            retry()


# RAX Container Create
def container_create(payload):
    rpath = '%s/%s' % (payload['url'].path, payload['c_name'])
    rpath = urllib.quote(rpath)
    for retry in ndw.retryloop(attempts=5, delay=2, backoff=2):
        conn = open_connection(url=payload['url'])
        try:
            resp, read = request(
                conn, rpath, method='HEAD', headers=payload['headers']
            )
            if resp.status == 404:
                resp, read = request(
                    conn, rpath, method='PUT', headers=payload['headers']
                )
                if resp.status >= 300:
                    print(
                        'ERROR in Processing. ERROR: %s\n%s\nSystem will'
                        ' retry' % (resp.status, resp.msg)
                    )
                    retry()
            elif resp.status >= 300:
                print(
                    'ERROR in Processing. ERROR: %s\n%s\nSystem will'
                    ' retry' % (resp.status, resp.msg)
                )
                retry()
            else:
                return True
        except Exception as exp:
            print('ERROR in Processing RAX Container create.'
                  ' ERROR: %s\nSystem will retry' % exp)
            retry()


# Download Files
def gotorax(sessionToken, args, obj, payload):
    tempf = tempfile.mktemp()
    try:
        # make a temp download file.
        downloader(
            sessionToken=sessionToken, args=args, obj=obj, tempf=tempf
        )
        for retry in ndw.retryloop(attempts=10, delay=2, backoff=1):
            conn = open_connection(url=payload['url'])
            rpath = '%s/%s/%s' % (
                payload['url'].path, payload['c_name'], obj
            )
            rpath = urllib.quote(rpath)
            with open(tempf, 'rb') as fopen:
                resp, read = request(
                    conn,
                    rpath,
                    method='PUT',
                    body=fopen,
                    headers=payload['headers']
                )
            if resp.status >= 300:
                retry()
                print(
                    'ERROR in PUT\'ing object onto RAXProcessing.'
                    ' ERROR: %s\n%s\nSystem will retry'
                    % (resp.status, resp.msg)
                )
    finally:
        if os.path.exists(tempf):
            os.remove(tempf)


def local_download(sessionToken, args, queue):
    while True:
        try:
            obj = queue.get(timeout=5)
        except Exception:
            break
        else:
            downloader(sessionToken, args, obj)


def rax_stream(sessionToken, args, queue, payload):
    while True:
        try:
            obj = queue.get(timeout=5)
        except Exception:
            break
        else:
            gotorax(sessionToken, args, obj, payload)