# =============================================================================
# Copyright [2013] [Kevin Carter]
# License Information :
# This software has no warranty, it is provided 'as is'. It is your
# responsibility to validate the behavior of the routines and its accuracy
# using the code provided. Consult the GNU General Public license for further
# details (see GNU General Public License).
# http://www.gnu.org/licenses/gpl.html
# =============================================================================

try:
    import argparse
except ImportError:
    raise SystemExit('Python module "argparse" not Found for import.')
import os


def args():
    par = argparse.ArgumentParser(
        usage='%(prog)s',
        description=(
            '%(prog)s will Download Files from Nirvanix Folders. This'
            ' application will search all folders that it can find at'
            ' increments of 500 per page. then it will download the found'
            ' "files" and store them in your working directory while'
            ' maintaining your Nirvanix directory structure.'
        ),
        epilog='GPLv3 Licensed Nirvanix Downloader Tool.'
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
                     default=os.getcwd())
    par.add_argument('-r',
                     '--remote-path',
                     metavar='',
                     help='Remote Path to Base folder, Default: "%(default)s"',
                     required=True,
                     default=None)
    par.add_argument('--node-url',
                     metavar='',
                     help='The base Nirvanix URL, Default: "%(default)s"',
                     default='https://services.nirvanix.com')

    # Setup for the positional Arguments
    subparser = par.add_subparsers(title='Available Actions',
                                   metavar='<Commands>\n')
    # Download Action
    download = subparser.add_parser('download',
                                    help='Download Files Locally')
    download.set_defaults(download=True)
    delete = subparser.add_parser('delete',
                                    help=('Delete all of your remote files in'
                                          ' a Nirvanix Folder.'))
    delete.set_defaults(delete=True)

    lister = subparser.add_parser('list',
                                  help='List all of your folders')
    lister.set_defaults(list=True)

    turbgroup = subparser.add_parser(
        'to-rax',
        help='Stream Nirvanix files to Rackspace CloudFiles'
    )
    turbgroup.set_defaults(to_rax=True)

    turbgroup.add_argument('-U',
                           '--os-user',
                           metavar='[STR]',
                           help='Your Openstack Username',
                           required=True,
                           default=None)

    key = turbgroup.add_mutually_exclusive_group()
    key.add_argument('-P',
                     '--os-password',
                     metavar='[STR]',
                     help='Your Openstack Password',
                     default=None)
    key.add_argument('-A',
                     '--os-apikey',
                     metavar='[STR]',
                     help='Your Openstack API Key',
                     default=None)
    key.add_argument('-T',
                     '--os-token',
                     metavar='[STR]',
                     help='Your Openstack Token',
                     default=None)

    reg = turbgroup.add_mutually_exclusive_group()
    reg.add_argument('--os-region',
                     metavar='[STR]',
                     help='Your Openstack Region',
                     default=None)
    reg.add_argument('--os-rax-auth',
                     choices=['dfw', 'ord', 'iad', 'lon', 'syd'],
                     help='Your Rackspace Region')

    turbgroup.add_argument('--os-auth-url',
                           metavar='[STR]',
                           help='Your Authentication URL',
                           default=None)
    turbgroup.add_argument('--os-version',
                           metavar='[STR]',
                           help='Your Openstack Authentication Version',
                           default='v2.0')
    turbgroup.add_argument('-C',
                           '--container',
                           metavar='[STR]',
                           help=('Container you will upload to,'
                                 ' Default: "%(default)s"'),
                           default='nirvanix')
    turbgroup.add_argument('--internal',
                           help='Use the service URL for Cloud Files',
                           action='store_true',
                           default=False)
    # Parse the Arguments.
    return vars(par.parse_args())
