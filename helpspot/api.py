"""
Python HelpSpot interface

A semi-bare shell of a HelpSpot API.

John P. Speno
speno@macspeno.com
Copyright 2010

Inspired by Python Twitter Tools
http://mike.verdone.ca/twitter/

Usage:

Create a HelpSpot object then call methods on it. Any method you call on
the object will be translated into the corresponding HelpSpot Web Services
API call. For methods with a literal dot ('.') in them, replace the dot
with an underscore in Python. Pass arguments to the remote side as keyword
style arguments from Python.

import helpspot

user = 'you@example.com'
pazz = 'idontknow'
path = 'http://helpdesk.example.com/help'

hs = helpspot.HelpSpot(path, user, pazz)

print hs.version()
print hs.private_version()

hs.private_request_update(xRequest='12345', Custom28='90210')
"""

import urllib2
import base64
from urllib import urlencode
try:
    import json
except ImportError:
    import simplejson as json

_POST_METHODS = [
    'request.create',
    'request.update',
    'forums.createTopic',
    'forums.createPost',
    'private.request.create',
    'private.request.update',
    'private.request.addTimeEvent',
    'private.request.deleteTimeEvent',
    'private.request.merge',
    'private.request.unsubscribe',
]

class HelpSpotError(Exception):
    """
    Exception raised when HelpSpot returns HTTP status code 400.
    The instance varibles are as follows:

        err_mesg - Description of the Error from HelpSpot.
        err_id - Error ID of the Error from HelpSpot. 

    This does not handle the error case if either public or private API
    are not enabled.

    """
    def __init__(self, err_mesg='', err_id=0):
        self.err_mesg = err_mesg
        self.err_id = err_id

    def __str__(self):
        return '%s (%s)' % (self.err_mesg, self.err_id)
    
class HelpSpotHandler(urllib2.HTTPHandler):
    """
    urllib2 opener class that handles (most) HelpSpot API errors.
    HelpSpot returns HTTP status code 400 for (most) errors.
    """
    def http_error_400(self, req, fp, code, msg, hdrs):
    	response = fp.read()
        try:
            errs = json.loads(response)
            details = errs['error'][0]
            err_mesg = details['description']
            err_id = details['id']
        except ValueError:
            err_id = 0
            err_mesg = "%s %s" % (msg, response)
        except IndexError:
            err_mesg = 'Unknown HelpSpot API error'
            err_id = 0
        raise HelpSpotError(err_mesg=err_mesg, err_id=err_id)

class HelpSpotAPI:
    """
    A HelpSpot API call. Will implicitly raise HelpSpotError
    on API errors otherwise it will return the unmarshalled
    json ouput from HelpSpot.
    """
    def __init__(self, method, user, password, uri):
        """
        Creates a HelpSpotAPI for a given method.
        """
        self.method = method.replace('_', '.')
        self.user = user
        self.password = password
        s = '%s:%s' % (self.user, self.password)
        self.authz = base64.b64encode(s)
        self.uri = uri.rstrip('/') + '/api/index.php?method='
        if self.method in _POST_METHODS:
            self.action = 'POST'
        else:
            self.action = 'GET'
        
    def __call__(self, **kwargs):
        """
        Calls the remote HelpSpot method on the HelpSpot server.
        """
        uri = '%s%s' % (self.uri, self.method)
        params = urlencode(kwargs)
        if 'GET' == self.action:
            if params:
                uri = '%s&%s' % (uri, params)
            message_body = None
        else:
            message_body = params
        uri = '%s&output=json' % uri
        req = urllib2.Request(uri)
        # Older Python versions may want to uncomment the following line
        # to prevent the server from keeping the connection open.
        #req.add_header('Connection', 'close')
        if self.method.startswith('private.'):
            req.add_header('Authorization', 'Basic %s' % self.authz) 
        # urllib2.urlopen could raise URLError, or HelpSpotError
        r = urllib2.urlopen(req, message_body)
        # XXX Detect errors when API not enabled
        return json.loads(r.read())

class HelpSpot:
    """
    A wrapper object around the HelpSpotAPI. Any method call on this
    object will create and invoke a HelpSpotAPI object.
    """
    def __init__(self, uri, user, password, debuglevel=0):
        self.uri = uri
        self.user = user
        self.password = password
        opener = urllib2.build_opener(HelpSpotHandler(debuglevel=debuglevel))
        urllib2.install_opener(opener)

    def __getattr__(self, key):
        try:
            return object.__getattr__(self, key)
        except AttributeError:
            return HelpSpotAPI(key, self.user, self.password, self.uri)

def main():
    user = sys.argv[1]
    password = sys.argv[2]
    uri = sys.argv[3]
    hs = HelpSpot(user=user, password=password, uri=uri)

    ver1 = hs.version()
    print "version returned", ver1
    ver2 = hs.private_version()
    print "private.version returned", ver2
    assert ver1 == ver2

if __name__ == '__main__':
    import sys
    sys.exit(main())
