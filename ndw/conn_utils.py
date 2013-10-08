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
import json
import os
import tempfile
import time
import textwrap
import traceback
import urllib
import urlparse

import ndw
import ndw.constants as con

from ndw.constants import LOG


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
        # conn.set_debuglevel(1)
        return conn


def request(conn, rpath, method='GET', body=None, headers=None, only=False):
    """Open a Connection."""
    if headers is None:
        headers = {}

    if only is True:
        conn.request(method, rpath, body=body, headers=headers)
    else:
        try:
            # conn.set_debuglevel(1)
            conn.request(method, rpath, body=body, headers=headers)
        except Exception:
            raise SystemExit('Connection issues, %s ' % traceback.format_exc())
        else:
            resp = conn.getresponse()
            return resp, resp.read()
        finally:
            conn.close()


# Download Files
def downloader(sessionToken=None, args=None, obj=None, tempf=None):

    def obj_get(dw_url):
        conn = open_connection(dw_url)
        request(conn, dw_url.path, method='GET', only=True)
        resp = conn.getresponse()
        return conn, resp

    def file_write(local_path, resp):
        with open(local_path, 'wb') as f:
            while True:
                chunk = resp.read(2048)
                if chunk:
                    f.write(chunk)
                else:
                    break
        return True

    def download_exp(storage_path, json_read, retry):
        if json_read is not None:
            nd = json_read.get('Download')[0].get('DownloadHost').split('.')[0]
            exclude = '&excludedNode=%s' % nd
            storage_path = '%s%s' % (
                storage_path, exclude
            )
            return storage_path
        else:
            retry()

    def check_srv():
        services_check = urlparse.urlsplit(
            'http://services.nirvanix.com/ws/Version.ashx'
        )
        conn = open_connection(services_check)
        resp, read = request(conn, services_check.path, method='GET')
        if resp.status != 200:
            time.sleep(30)

    def error_msg(json_read, url_data, ec):
        msg = textwrap.fill(
            'ERROR: "%s" Nirvanix Reported an error with the content'
            ' you are attempting to Download. The system will retry.'
            'Error Count: %s '
            % (json_read['ErrorMessage'], ec),
            60
        )
        LOG.critical('\n%s\n' % msg)
        if int(json_read['ResponseCode']) == 70205:
            msg = textwrap.fill(
                'The response Code from Nirvanix about the URL,'
                ' "%s" indicates that the resource is not To be'
                ' found. While This is likey an issue with the'
                ' storage provider, The system will retry a few'
                ' more times, however success is not expected.'
                'Error Count: %s '
                % (url_data, ec),
                60
            )
            LOG.critical('\n%s\n' % msg)
            time.sleep(30)
        else:
            check_srv()

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
    error_count = 0
    for retry in ndw.retryloop(attempts=5, delay=5, backoff=1):
        conn = open_connection(storage_url)
        resp, read = request(conn, storage_path, method='GET')
        json_read = json.loads(read)
        if 'ErrorMessage' in json_read:
            error_count += 1
            error_msg(json_read, storage_path, error_count)
            retry()
        elif resp.status >= 300:
            error_count += 1
            LOG.error('Failed connecting to download Nirvanix Node. '
                      'ERROR: %s. System will retry. Error Message %s'
                      'Error Count: %s ', resp.status, resp.msg,
                      error_count)
            storage_path = download_exp(storage_path, json_read, retry)
            retry()
        else:
            try:
                dw_url = urlparse.urlsplit(
                    json_read.get('Download')[0].get('DownloadURL')
                )
                conn, resp = obj_get(dw_url)
                if resp.status >= 300:
                    conn.close()
                    error_count += 1
                    LOG.error('Nirvanix ERROR on Download Node API request. '
                              'ERROR: %s - %s. System will retry. '
                              'Error Count: %s ', resp.status, resp.msg,
                              error_count)
                    storage_path = download_exp(storage_path, json_read, retry)
                    retry()
            except Exception as exc:
                error_count += 1
                LOG.error('Absolute Failure in Nirvanix Request. %s the system'
                          ' will retry. ERROR: %s. Error Count: %s',
                          resp.status, exc, error_count)
                retry()
            else:
                file_w = file_write(local_path, resp)
                return file_w
            finally:
                conn.close()


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
                    LOG.error('ERROR in Processing. ERROR: %s\n%s\nSystem will'
                              ' retry', resp.status, resp.msg)
                    retry()
            elif resp.status >= 300:
                LOG.error('ERROR in Processing. ERROR: %s\n%s\nSystem will'
                          ' retry', resp.status, resp.msg)
                retry()
            else:
                return True
        except Exception as exp:
            LOG.error('ERROR in Processing RAX Container create.'
                      ' ERROR: %s. System will retry', exp)
            retry()


# Download Files
def gotorax(sessionToken, args, obj, payload):

    def _remove_file(temp_file):
        if os.path.exists(temp_file):
            os.remove(temp_file)

    def _check_object(rax_response, temp_file):
        if rax_response.status == 404:
            return True
        else:
            ndw.md5_checker(rax_response, temp_file)

    def _check_rax_error(rax_resp, sys_payload, sys_args, rax_retry,
                         other=False):
        if rax_resp.status == 401:
            sys_payload['headers']['X-Auth-Token'] = con.rax_reauthenticate(
                sys_args
            )
            LOG.error('ERROR: %s\n%s\nSystem will retry',
                      rax_resp.status, rax_resp.msg)
            rax_retry()
        elif rax_resp.status >= 300 and other is True:
            LOG.info(
                'ERROR in object request when RAX Processing.'
                ' ERROR: %s\n%s\nSystem will retry',
                rax_resp.status, rax_resp.msg
            )
            rax_retry()

    # make a temp download file.
    tempf = tempfile.mktemp()
    try:
        for retry in ndw.retryloop(attempts=10, delay=2, backoff=1):
            downloaded = downloader(sessionToken, args, obj, tempf)
            if downloaded is True and os.path.exists(tempf):
                # Upload file to RAX
                for _retry in ndw.retryloop(attempts=10, delay=2, backoff=1):
                    rpath = '%s/%s/%s' % (
                        payload['url'].path, payload['c_name'], obj
                    )
                    rpath = urllib.quote(rpath)
                    conn = open_connection(url=payload['url'])
                    resp, read = request(
                        conn,
                        rpath,
                        method='HEAD',
                        headers=payload['headers']
                    )
                    _check_rax_error(resp, payload, args, _retry)

                for _retry_ in ndw.retryloop(attempts=10, delay=2):
                    if _check_object(resp, tempf) is True:
                        conn = open_connection(url=payload['url'])
                        with open(tempf, 'rb') as open_file:
                            resp, read = request(
                                conn,
                                rpath,
                                method='PUT',
                                body=open_file,
                                headers=payload['headers']
                            )
                        _check_rax_error(
                            resp, payload, args, _retry_, other=True
                        )
                    else:
                        _remove_file(tempf)
            else:
                _remove_file(tempf)
                retry()
    except Exception as exp:
        LOG.error('Error Processing Rackspace Method ERROR: %s', exp)
        retry()
    finally:
        _remove_file(tempf)


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


def nirvanix_delete(sessionToken, args, queue):
    while True:
        try:
            obj = queue.get(timeout=5)
        except Exception:
            break
        else:
            delete_url = urlparse.urlsplit(
                '%s/ws/IMFS/DeleteFolders.ashx' % args['node_url']
            )
            delete_query = (
                '?sessionToken=%s&folderPath=%s&output=json'
                % (sessionToken, obj)
            )
            delete_path = '%s%s' % (delete_url.path, delete_query)
            conn = open_connection(delete_url)
            resp, read = request(conn, delete_path, method='GET')
            try:
                json_resp = json.loads(read)
                if json_resp.get('ResponseCode'):
                    if json_resp['ResponseCode'] == 0:
                        LOG.error('Folder DELETED:\t%s %s'
                                  % resp.status, resp.reason)
                    if json_resp['ResponseCode'] == 70005:
                        LOG.error('Folder %s no longer exists', obj)
                else:
                    LOG.error('Nothing was read in')
            except Exception as exp:
                LOG.error('Nothing to decode or understand.\nERROR : %s', exp)

