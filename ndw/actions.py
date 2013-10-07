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
import errno
import json
import multiprocessing
import math
import os

import ndw
from ndw import conn_utils


# Globals
SessToken = None
FolderUrl = None
FileList = None
FolderList = None


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


def get_folder_list(folder='/', page_number=1, total_folders=0):

    def _recurse_list(remaining, page):
        page += 1
        get_folder_list(
            folder=folder, page_number=page, total_folders=remaining
        )

    folder_query = folder_query_quote(SessToken, folder, page_number)
    folder_path = '%s%s' % (FolderUrl.path, folder_query)
    conn = conn_utils.open_connection(FolderUrl)
    resp, read = conn_utils.request(conn, folder_path, method='GET')
    json_response = json.loads(read)
    list_folders = json_response.get('ListFolder')
    folders = list_folders.get('Folder')
    num_folders = len(folders)

    for _folder in folders:
        FolderList.append(_folder)

    if total_folders == 0:
        total_folders = list_folders.get('TotalFolderCount')
        if total_folders is not None:
            total_folders = int(total_folders)
        else:
            total_folders = 0

    remaining_folders = total_folders - num_folders
    if remaining_folders > 0:
        _recurse_list(remaining_folders, page_number)


def folder_query_quote(SessToken, path, page):
    folder_query = (
        '?sessionToken=%s&folderPath=%s&pageNumber=%s&pageSize=500&output=json'
        % (SessToken, path, page)
    )
    return folder_query


def get_file_list(folder_path, page_number=1, total_files=0):

    def _recurse_list(queue):
        while True:
            try:
                page = queue.get(timeout=2)
                print page
            except Exception:
                break
            else:
                page += 1
                _folder_query = folder_query_quote(
                    SessToken, folder_path, page
                )
                _folder_path = '%s%s' % (FolderUrl.path, _folder_query)
                _conn = conn_utils.open_connection(FolderUrl)
                _resp, _read = conn_utils.request(
                    _conn, _folder_path, method='GET'
                )
                _json_response = json.loads(_read)
                _list_folders = _json_response.get('ListFolder')
                _files = _list_folders.get('File')
                file_lister(_files, FileList)

    folder_query = folder_query_quote(SessToken, folder_path, page_number)
    _folder_path = '%s%s' % (FolderUrl.path, folder_query)
    conn = conn_utils.open_connection(FolderUrl)
    resp, read = conn_utils.request(conn, _folder_path, method='GET')
    json_response = json.loads(read)
    list_folders = json_response.get('ListFolder')

    if total_files == 0:
        total_files = list_folders.get('TotalFileCount')
        if total_files is not None:
            total_files = int(total_files)
        else:
            total_files = 0

    pages = int(math.ceil(float(total_files) / float(500)))
    if pages <= 1:
        files = list_folders.get('File')
        file_lister(files, FileList)
    else:
        ndw.threader(
            job_action=_recurse_list,
            files=range(pages),
            args=None,
            sessionToken=None,
            payload=None,
            threads=20
        )


def file_lister(_files, files_list):

    def _lister(queue):
        while True:
            try:
                file = queue.get(timeout=2)
            except Exception:
                break
            else:
                if file.get('Path'):
                    files_list.append(file.get('Path'))

    if _files:
        ndw.threader(
            job_action=_lister,
            files=_files,
            args=None,
            sessionToken=None,
            payload=None,
            threads=2
        )


def file_actions(queue=None, folder=None):
    try:
        if folder is None:
            folder = queue.get(timeout=5)
    except Exception:
        pass
    else:
        get_folder_list(folder=folder)


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
    global SessToken, FolderUrl, FileList, FolderList
    SessToken = sessionToken
    FolderUrl = folder_url
    manager = multiprocessing.Manager()
    FileList = manager.list()
    FolderList = manager.list()

    get_folder_list(
        folder=args['remote_path']
    )

    get_file_list(
        folder_path=args['remote_path'],
    )
    for folder in FolderList:
        get_file_list(
            folder_path=folder.get('Path'),
            total_files=folder.get('FileCount')
        )

    return set(FileList)
