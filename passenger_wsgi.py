#!/usr/bin/env python

import os.path
import sys
import traceback

def application(environ, start_response):
    try:
        request = environ['REQUEST_URI']
        if request[0] == '/':
            request = request[1:]
        dir = os.path.join(os.path.dirname(__file__), request)
        sys.path.append(dir)
        import server
        ret = server.application(environ, start_response)
        sys.path.pop()
        return ret
    except:
        start_response('500', [('content-type', 'text/plain')])
        return traceback.format_exc()
