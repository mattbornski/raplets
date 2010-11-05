#!/usr/bin/env python

import os
import os.path
import sys
import traceback

try:
    import simplejson
except:
    sys.path.append('/home/mtborn/local/lib/python2.5/site-packages/simplejson-2.1.1-py2.5-linux-x86_64.egg')
    import simplejson

def application(environ, start_response):
    try:
        request = environ['REQUEST_URI'][1:].split('/')[0]
        dir = os.path.join(os.getcwd(), request)
        if os.path.isfile(os.path.join(dir, 'server.py')):
            sys.path.append(dir)
            import server
            ret = server.application(environ, start_response)
            sys.path.pop()
            return ret
        else:
            start_response('404', [('content-type', 'text/plain')])
            return '404'
    except:
        start_response('500', [('content-type', 'text/plain')])
        return traceback.format_exc()
