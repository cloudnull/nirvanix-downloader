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
import traceback
import urlparse

from ndw import conn_utils

__rax_regions__ = ['dfw', 'ord', 'iad', 'lon', 'syd']
__srv_types__ = ['cloudFiles', 'objectServer']


def authenticate(args):
    """Authentication For Openstack API.

    Pulls the full Openstack Service Catalog Credentials are the Users API
    Username and Key/Password "osauth" has a Built in Rackspace Method for
    Authentication

    Set a DC Endpoint and Authentication URL for the OpenStack environment

    :param auth_dict: required parameters are auth_url
    """

    # Setup the request variables
    url, rax = parse_region(args)
    a_url = parse_url(url=url, auth=True)
    auth_json = parse_reqtype(args)

    # remove the prefix for the Authentication URL if Found
    auth_json_req = json.dumps(auth_json)
    headers = {'Content-Type': 'application/json'}

    # Send Request
    request = ('POST', a_url.path, auth_json_req, headers)
    resp_read = request_process(aurl=a_url, req=request)
    try:
        auth_resp = json.loads(resp_read)
    except ValueError as exp:
        raise SystemExit('JSON Decode Failure. ERROR: %s - RESP %s'
                         % (exp, resp_read))
    else:
        auth_info = parse_auth_response(auth_resp, args)
        token, tenant, user, inet, enet = auth_info
        return token, tenant, user, inet, enet


def parse_url(url, auth=False):
    """Return a clean URL. Remove the prefix for the Auth URL if Found.

    :param url:
    :return aurl:
    """

    def is_https(iurl):
        """Check URL to determine the Connection type.

        :param iurl:
        :return 'complete url string.':
        """

        if 'rackspace' in iurl:
            return 'https://%s' % iurl
        else:
            return 'http://%s' % iurl

    if auth is True:
        if 'tokens' not in url:
            url = urlparse.urljoin(url, 'tokens')

    if url.startswith(('http', 'https', '//')):
        if url.startswith('//'):
            return urlparse.urlparse(url, scheme='http')
        else:
            return urlparse.urlparse(url)
    else:
        return urlparse.urlparse(is_https(iurl=url))


def parse_reqtype(ARGS):
    """Setup our Authentication POST.

    username and setup are only used in APIKEY/PASSWORD Authentication
    """

    setup = {'username': ARGS.get('os_user')}
    if ARGS.get('os_token') is not None:
        auth_body = {'auth': {'token': {'id': ARGS.get('os_token')},
                              'tenantName': ARGS.get('os_tenant')}}
    elif ARGS.get('os_apikey') is not None:
        prefix = 'RAX-KSKEY:apiKeyCredentials'
        setup['apiKey'] = ARGS.get('os_apikey')
        auth_body = {'auth': {prefix: setup}}
    elif ARGS.get('os_password') is not None:
        prefix = 'passwordCredentials'
        setup['password'] = ARGS.get('os_password')
        auth_body = {'auth': {prefix: setup}}
    else:
        raise AttributeError('No Password, APIKey, or Token Specified')
    return auth_body


def get_surl(region, cf_list, lookup):
    """Lookup a service URL.

    :param region:
    :param cf_list:
    :param lookup:
    :return net:
    """

    for srv in cf_list:
        if region in srv.get('region'):
            net = parse_url(url=srv.get(lookup))
            return net
    else:
        raise SystemExit(
            'Region "%s" was not found in your Service Catalog.' % region
        )


def parse_auth_response(auth_response, ARGS):
    """Parse the auth response and return the tenant, token, and username.

    :param auth_response: the full object returned from an auth call
    :returns: tuple (token, tenant, username, internalurl, externalurl, cdnurl)
    """

    access = auth_response.get('access')
    token = access.get('token').get('id')

    if 'tenant' in access.get('token'):
        tenant = access.get('token').get('tenant').get('name')
        user = access.get('user').get('name')
    elif 'user' in access:
        tenant = None
        user = access.get('user').get('name')
    else:
        raise SystemExit('No Token Found to Parse.\nHere is the DATA: %s\n%s'
                         % (auth_response, traceback.format_exc()))

    scat = access.pop('serviceCatalog')
    for srv in scat:
        if srv.get('name') in __srv_types__:
            cfl = srv.get('endpoints')

    if ARGS.get('os_region') is not None:
        region = ARGS.get('os_region')
    elif ARGS.get('os_rax_auth') is not None:
        region = ARGS.get('os_rax_auth')
    else:
        raise SystemExit('No Region Set')

    region = region.upper()
    if cfl is not None:
        inet = get_surl(region=region, cf_list=cfl, lookup='internalURL')
        enet = get_surl(region=region, cf_list=cfl, lookup='publicURL')

    return token, tenant, user, inet, enet


def parse_region(ARGS):
    """Pull region/auth url information from context."""

    base_auth_url = 'identity.api.rackspacecloud.com/v2.0/tokens'

    if ARGS.get('os_region'):
        region = ARGS.get('os_region')
    elif ARGS.get('os_rax_auth'):
        region = ARGS.get('os_rax_auth')
    else:
        raise SystemExit('You Are required to specify a REGION')

    if region.lower() is 'lon':
        return 'lon.%s' % base_auth_url, True
    elif region.lower() in __rax_regions__:
        return '%s' % base_auth_url, True
    else:
        if ARGS.get('os_auth_url'):
            if 'racksapce' in ARGS.get('os_auth_url'):
                return ARGS.get('os_auth_url', '%s' % base_auth_url), True
            else:
                return ARGS.get('os_auth_url'), False
        else:
            raise SystemExit('You Are required to specify a'
                             ' REGION and an AUTHURL')


def request_process(aurl, req):
    """Perform HTTP(s) request based on Provided Params.

    :param aurl:
    :param req:
    :param https:
    :return read_resp:
    """

    conn = conn_utils.open_connection(url=aurl)

    # Make the request for authentication
    try:
        _method, _url, _body, _headers = req
        conn.request(method=_method, url=_url, body=_body, headers=_headers)
        resp = conn.getresponse()
    except Exception as exc:
        raise AttributeError("Failure to perform Authentication %s ERROR:\n%s"
                             % (exc, traceback.format_exc()))
    else:
        resp_read = resp.read()
        status_code = resp.status
        if status_code >= 300:
            raise httplib.HTTPException('Failed to authenticate %s'
                                        % status_code)
        return resp_read
