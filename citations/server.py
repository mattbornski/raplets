#!/usr/bin/python

import simplejson
import urlparse
import BaseHTTPServer
import traceback

import citation

metadata = {
  'name':           'Citations',
  'description':    'Attempt to match academics with their articles.',
  'welcome_text':   'Citations',
  'icon_url':       'http://raplets.mattborn.net/citations/icon.jpg',
  'preview_url':    'http://raplets.mattborn.net/citations/icon.jpg',
  'provider_name':  'Google Scholar',
  'provider_url':   'http://scholar.google.com/',
}
endpoint = {
  'process':        citation.process,
  'bind_interface': '',
  'bind_port':      2483,
}

# Regardless of the operating mode, this code's job is to execute the
# specified function and package the return value.
def common(qs):
    try:
        args = dict(urlparse.parse_qsl(qs))
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
            print text
            return (200, text)
        else:
            return (400, None)
    except:
        print traceback.format_exc()
        return (500, None)

class Database:
    pass


########
# Mode 1: WSGI application
########

# WSGI endpoint.  If we happen to be within a WSGI directory, and someone
# points a browser at us, this will provide the Raplet response.
def application(environ, start_response):
    qs = environ.get('QUERY_STRING', '')
    (status, body) = common(qs)
    start_response(str(status), [('Content-Type', 'text/javascript')])
    if body is not None:
        return body

########
# Mode 2: stand alone web server
########

# A class to provide the Raplet response when we're operating as a
# stand alone web server.
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
