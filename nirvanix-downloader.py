#!/usr/bin/env python
# Copyright [2013] [Kevin Carter]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import urlparse
import urllib
import httplib
import json
import errno
import os
try:
    import argparse
except ImportError:
    raise SystemExit('Python module "argparse" not Found for import.')


par = argparse.ArgumentParser(
    usage='%(prog)s',
    formatter_class=lambda prog: argparse.HelpFormatter(
        prog,
        max_help_position=28
    ),
    description=(
        '%(prog)s will Download Files from Nirvanix Folders. This application'
        ' will search all folders that it can find at increments of 500 per'
        ' page. then it will download the found "files" and store them in your'
        ' working directory while maintaining your Nirvanix directory'
        ' structure.'
    ),
    epilog='Apache2 Licensed Nirvanix Downloader.'
)

par.add_argument('-u',
                 '--username',
                 metavar='',
                 help='Your Nirvanix Username',
                 required=True,
                 default=None)
par.add_argument('-p',
                 '--password',
                 metavar='',
                 help='Your Nirvanix Password',
                 required=True,
                 default=None)
par.add_argument('-a',
                 '--appkey',
                 metavar='',
                 help='Your Nirvanix AppKey',
                 required=True,
                 default=None)
par.add_argument('-w',
                 '--work-dir',
                 metavar='',
                 help='Your Nirvanix Working Directory',
                 required=True,
                 default=None)
par.add_argument('-r',
                 '--remote-path',
                 metavar='',
                 help='Remote Path to Base folder, Default: "%(default)s"',
                 default='/')
# Parse the Arguments.
ARGS = vars(par.parse_args())



def connection(url, rpath, method='GET'):
    """Open a Connection."""
    try:
        conn = httplib.HTTPSConnection(url.netloc)
        # conn.set_debuglevel(1)
        conn.request(method, rpath)
        resp = conn.getresponse()
    except Exception:
        raise SystemExit('Connection issues')
    else:
        return resp, resp.read()
    finally:
        conn.close()


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

base_url = 'https://services.nirvanix.com'


# Authentication
auth_url = urlparse.urlsplit('%s/ws/Authentication/Login.ashx' % base_url)
auth_query = (
    '?appKey=%s&username=%s&password=%s&output=json'
    % (ARGS['appkey'], ARGS['username'], ARGS['password'])
)
auth_path = '%s%s' % (auth_url.path, auth_query)

# Connection
resp, read = connection(auth_url, auth_path, method='GET')
json_response = json.loads(read)

# Get Session
sessionToken = json_response.get('SessionToken')

# Set folder path
folder_url = urlparse.urlsplit('%s/ws/IMFS/ListFolder.ashx' % base_url)

# Get file list ready
files = []


def get_folder_list(folder='/'):
    folder_query = folder_query_quote(sessionToken, folder)
    folder_path = '%s%s' % (folder_url.path, folder_query)
    resp, read = connection(folder_url, folder_path, method='GET')
    json_response = json.loads(read)
    list_folders = json_response.get('ListFolder')
    _files = list_folders.get('File')
    file_lister(_files)
    return list_folders


def folder_query_quote(sessionToken, path):
    folder_query = (
        '?sessionToken=%s&folderPath=%s&pageNumber=1&pageSize=500&'
        'output=json' % (sessionToken, path)
    )
    return folder_query


def file_lister(files_list):
    if files_list:
        for file in files_list:
            if file.get('Path'):
                files.append(file.get('Path'))


def file_getter(folder_list):
    for folder in folder_list:
        list_folders = get_folder_list(folder=folder)
        file_getter(
            [path['Path'] for path in list_folders.get('Folder')
             if path.get('Path') is not None]
        )

list_folders = get_folder_list(folder=ARGS['remote_path'])
file_getter(
    [path['Path'] for path in list_folders.get('Folder')
     if path.get('Path') is not None]
)

# Fetch the local Directories
unique_dirs = []
for obj in files:
    full_path = os.path.join(ARGS['work_dir'], obj)
    dir_path = full_path.split(os.path.basename(full_path))[0].rstrip(os.sep)
    unique_dirs.append(dir_path)

# Make the local Directories
for u_dir in unique_dirs:
    mkdir_p(u_dir)

# Download Files
for obj in files:
    download_path = '%s/%s/%s' % (sessionToken,
                                  ARGS['username'],
                                  urllib.quote(obj))
    dw_url = urlparse.urlsplit(urlparse.urljoin(base_url, download_path))
    resp, read = connection(dw_url, dw_url.path, method='GET')
    local_path = '/tmp/%s' % obj
    with open(local_path, 'wb') as f:
        f.write(read)
