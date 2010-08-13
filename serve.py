#!/usr/bin/env python

import BaseHTTPServer
import cgi
import simplejson
import sys
import traceback
import urlparse
import wsgiref
import wsgiref.simple_server

endpoint = {
  'bind_interface': '',
  'bind_port':      6379,
}

# WSGI endpoint.  If we happen to be within a WSGI directory, and someone
# points a browser at us, this will provide the Raplet response.
def application(environ, start_response):
    # First, determine which Raplet this is intended for.
    sys.path.append('citations')
    import citations
    sys.path.pop()
    raplet = citations.process
    # Second, determine which arguments should be passed to the raplet.
    qs = environ.get('QUERY_STRING', '')
    try:
        args = dict(urlparse.parse_qsl(qs))
    except AttributeError:
        args = dict(cgi.parse_qsl(qs))
    # Third, invoke the Raplet with the arguments.
    status = 200
    body = None
    if 'callback' in args:
        if args.get('show', None) == 'metadata':
            result = module.metadata
            result['status'] = 200
        else:
            result = raplet(args)
            if not isinstance(result, dict):
                result = {'html':str(result)}
            result['status'] = 200
        body = args['callback'] + '(' + simplejson.dumps(result) + ')'
    else:
        status = 400
    # Fourth, compose the response to send to the remote host.
    message = str(status) + ' ' \
      + BaseHTTPServer.BaseHTTPRequestHandler.responses[status][0]
    start_response(message, [('Content-Type', 'text/javascript')])
    if body is not None:
        return body
    else:
        return ''

# If we're not in a WSGI directory, make it so.
def main():
    try:
        server = wsgiref.simple_server.make_server(
          endpoint['bind_interface'], endpoint['bind_port'], application)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

# If you invoke us as the script, we'll just start running a web server.
# It'll be great.
if __name__ == '__main__':
    main()
