"""
Python HelpSpot interface

A bare shell of a HelpSpot API.

John P. Speno
speno@macspeno.com
Copyright 2009

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
]

class HelpSpotHandler(urllib2.HTTPHandler):
    """
    urllib2 opener that treats HTTP status code 400
    as normal. HelpSpot uses code 400 for API errors.
    """
    def http_error_400(self, req, fp, code, msg, hdrs):
        return fp

class HelpSpotAPI:
    def __init__(self, method, user, password, uri):
        self.method = method.replace('_', '.')
        self.user = user
        self.password = password
        s = '%s:%s' % (self.user, self.password)
        self.authz = s.encode('base64').rstrip()
        self.uri = uri.rstrip('/') + '/api/index.php?method='
        if self.method in _POST_METHODS:
            self.action = 'POST'
        else:
            self.action = 'GET'
        
    def __call__(self, **kwargs):
        uri = '%s%s' % (self.uri, self.method)
        params = urlencode(kwargs)
        if 'GET' == self.action:
            if params:
                uri = '%s&%s' % (uri, params)
            data = None
        else:
            data = params
        uri = '%s&output=json' % uri
        req = urllib2.Request(uri)
        # Older Python versions may want to uncomment the following line
        # to prevent the server from keeping the connection open.
        #req.add_header('Connection', 'close')
        if self.method.startswith('private.'):
            req.add_header('Authorization', 'Basic %s' % self.authz) 
        r = urllib2.urlopen(req, data)
        # XXX Detect errors when API not enabled
        # XXX Detect other errors
        return json.loads(r.read())

class HelpSpot:
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

    err1 = hs.move_along()
    print "unknown method move.along returned", err1

    err2 = hs.private_request_update(xRequest='466', Custom28='Foobar')
    print "bad request ID update returned", err2

    good = hs.private_request_update(xRequest='20466', Custom28='Python')

    print good['xRequest'], "was updated just fine"
if __name__ == '__main__':
    import sys
    sys.exit(main())
