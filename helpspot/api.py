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

hs = helpspot.HelpSpot(user, pazz, path)

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

class HelpSpotError(Exception):
    """Exception raised for HelpSpot API Exceptions"""
    def __init__(self, method):
        self.method = method
    def __str__(self):
        return str(self.method)

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
        if self.method.startswith('private.'):
            req.add_header("Authorization", "Basic %s" % self.authz) 
        try:
            r = urllib2.urlopen(req, data)
        except urllib2.HTTPError, e:
            # No such method
            if 400 == e.code:
                s = "No such method: %s" % self.method
                raise HelpSpotError(s)
        # XXX Detect errors when API not enabled
        # XXX Detect other errors
        return json.loads(r.read())
        

class HelpSpot:
    def __init__(self, uri, user, password):
        self.uri = uri
        self.user = user
        self.password = password

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
    ver2 = hs.private_version()
    assert ver1 == ver2

    try:
        print hs.move_along()
    except HelpSpotError, e:
        print e

    print hs.private_request_update(xRequest='20466', Custom28='Foobar')

if __name__ == '__main__':
    import sys
    sys.exit(main())
