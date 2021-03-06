#!/usr/bin/env python

import cgi
import simplejson
import traceback
import urlparse
import wsgiref

import citations

metadata = {
  'name':           'Citations',
  'description':    'Attempt to match academics with their articles.',
  'welcome_text':   'Adding Citations will let you preview the articles written by people you correspond with quickly and easily.',
  'icon_url':       'http://raplets.mattborn.net/citations/icon.jpg',
  'preview_url':    'http://raplets.mattborn.net/citations/preview.jpg',
  'provider_name':  'Matt Born',
  'provider_url':   'http://raplets.mattborn.net/citations/',
}
endpoint = {
  'process':        citations.process,
  'bind_interface': '',
  'bind_port':      2483,
}

# Regardless of the operating mode, this code's job is to execute the
# specified function and package the return value.
def common(qs):
    try:
        try:
            args = dict(urlparse.parse_qsl(qs))
        except AttributeError:
            args = dict(cgi.parse_qsl(qs))
        if 'callback' in args:
            if args.get('show', None) == 'metadata':
                result = metadata
            else:
                result = endpoint['process'](args)
                if not isinstance(result, dict):
                    result = {'html':str(result)}
                else:
                    result = {'html':''}
            result['status'] = 200
            text = args['callback'] + '(' + simplejson.dumps(result) + ')'
            return (200, text)
        else:
            return (400, None)
    except:
        return (500, traceback.format_exc())

class Database:
    pass


# WSGI endpoint.  If we happen to be within a WSGI directory, and someone
# points a browser at us, this will provide the Raplet response.
def application(environ, start_response):
    qs = environ.get('QUERY_STRING', '')
    (status, body) = common(qs)
    start_response(str(status), [('Content-Type', 'text/javascript')])
    if body is not None:
        return body
    else:
        return ''

# WSGI server.  If we don't happen to be within a WSGI directory, we'll
# make it one.
class Raplet(BaseHTTPServer.BaseHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        self.db = Database()
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    def do_GET(self):
        qs = (self.path + '?').split('?')[1]
        (status, body) = common(qs)
        self.send_response(status)
        if body is not None:
            self.send_header('Content-type', 'text/javascript')
            self.end_headers()
            self.wfile.write(body)

# Run a web server providing the Raplet endpoint.  It would be nice if
# there were some sort of command line argument support and/or config
# file support, but the inline metadata and endpoint dictionaries are
# the best we're doing at the moment.
def main():
    try:
        server = BaseHTTPServer.HTTPServer(
          (endpoint['bind_interface'], endpoint['bind_port']), Raplet)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

# If you invoke us as the script, we'll just start running a web server.
# It'll be great.
if __name__ == '__main__':
    main()
