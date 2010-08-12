#!/usr/bin/env python

import os.path
import sys

def application(environ, start_response):
    start_response('200 OK', [('content-type', 'text/plain')])
    return os.path.join(os.path.dirname(__file__), environ['REQUEST_URI'])
