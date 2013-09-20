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
import multiprocessing
import json
import errno
import os

from ndw import conn_utils
import ndw


def mkdir_p(path):
    """'mkdir -p' in Python

    :param path:
    """

    try:
        if not os.path.isdir(path):
            os.makedirs(path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise SystemExit(
                'The path provided, "%s", is either occupied and can\'t be'
                ' used as a directory or the permissions will not allow you to'
                ' write to this location.' % path
            )


def get_folder_list(folder='/'):
    folder_query = folder_query_quote(SessToken, folder)
    folder_path = '%s%s' % (FolderUrl.path, folder_query)
    conn = conn_utils.open_connection(FolderUrl)
    resp, read = conn_utils.request(conn, folder_path, method='GET')
    json_response = json.loads(read)
    list_folders = json_response.get('ListFolder')
    _files = list_folders.get('File')
    file_lister(_files, FileList)
    return list_folders


def folder_query_quote(SessToken, path):
    folder_query = (
        '?sessionToken=%s&folderPath=%s&pageNumber=1&pageSize=500&'
        'output=json' % (SessToken, path)
    )
    return folder_query


def file_lister(_files, files_list):
    if _files:
        for file in _files:
            if file.get('Path') and file.get('Path') not in files_list:
                files_list.append(file.get('Path'))


def file_actions(queue=None, folder=None):
    try:
        if folder is None:
            folder = queue.get(timeout=5)
    except Exception:
        pass
    else:
        list_folders = get_folder_list(
            folder=folder
        )
        file_getter(
            [path['Path'] for path in list_folders.get('Folder')
             if path.get('Path') is not None]
        )


def file_getter(folder_list):
    if len(folder_list) <= 1:
        for folder in folder_list:
            file_actions(folder=folder)
    else:
        ndw.threader(
            job_action=file_actions,
            files=folder_list,
            args=None,
            sessionToken=None,
            payload=None,
            threads=5
        )


def file_finder(sessionToken, folder_url, args):
    global SessToken, FolderUrl, FileList
    SessToken = sessionToken
    FolderUrl = folder_url
    manager = multiprocessing.Manager()
    FileList = manager.list()

    list_folders = get_folder_list(
        folder=args['remote_path']
    )
    file_getter(
        [path['Path'] for path in list_folders.get('Folder')
         if path.get('Path') is not None]
    )
    return FileList

