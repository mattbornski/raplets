#!/usr/bin/python

import getpass
import simplejson
import urlparse
import BaseHTTPServer
import traceback

import kickball

class Raplet(BaseHTTPServer.BaseHTTPRequestHandler):
    creds = None
    def __init__(self, *args, **kwargs):
        self.database = kickball.database(self.creds)
        BaseHTTPServer.BaseHTTPRequestHandler.__init__(self, *args, **kwargs)
    def do_GET(self):
        try:
            qs = (self.path + '?').split('?')[1]
            args = dict(urlparse.parse_qsl(qs))
            if 'callback' in args:
                if args.get('show', None) == 'metadata':
                    result = {'name':'WAKA', 'description':'WAKA', 'welcome_text':'waka waka waka', 'icon_url':'http://raplets.mattborn.net/waka/icon.jpg', 'preview_url':'http://raplets.mattborn.net/waka/preview.jpg', 'provider_name':'Matt Born', 'provider_url':'http://raplets.mattborn.net/waka/'}
                else:
                    p = self.database.player(email = args['email'])
                    result = {'status':200, 'html':p.html()}
                self.send_response(200)
                self.send_header('Content-type', 'text/javascript')
                self.end_headers()
                text = args['callback'] + '(' + simplejson.dumps(result) + ')'
                self.wfile.write(text)
            else:
                self.send_response(400)
        except:
            self.send_response(500)
            print self.path
            print traceback.format_exc()

def main():
    creds = {'username':'mattborn', 'password':getpass.getpass()}
    try:
        Raplet.creds = creds
        server = BaseHTTPServer.HTTPServer(('', 5425), Raplet)
        server.serve_forever()
    except KeyboardInterrupt:
        server.socket.close()

if __name__ == '__main__':
    main()
