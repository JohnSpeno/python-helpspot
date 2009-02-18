"""
Python HelpSpot interface

A bare shell of a HelpSpot API.

John P. Speno
speno@macspeno.com
Copyright 2009

Inspired by Python Twitter Tools
http://mike.verdone.ca/twitter/
"""

import urllib2
from urllib import urlencode
import json

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
                raise HelpSpotError(self.method)
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

    print hs.private_version()
    try:
        print hs.nomethod()
    except HelpSpotError, e:
        print e

if __name__ == '__main__':
    import sys
    sys.exit(main())
