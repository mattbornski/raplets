#!/usr/bin/env python

import re
import urllib2

# Register a custom User-Agent string so that people don't slam the
# door on us.  Some people don't take kindly to unidentified robots.
opener = urllib2.build_opener()
opener.addheaders = [
  ('User-Agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.19) Gecko/20081202 Firefox (Debian-2.0.0.19-0etch1)'),
]
urllib2.install_opener(opener)

def scholar(names = None, emails = None):
    if names is not None and emails is not None:
        query = u'http://scholar.google.com/scholar?q='
        if len(emails) > 0:
            query += urllib2.quote(emails[0])
            for email in emails[1:]:
                query += '+'
                query += urllib2.quote(email)
        if len(names) > 0:
            if len(emails) > 0:
                query += '+'
            query += 'author:' + '+author:'.join(names)
        query += '&'
        query += 'hl=en&btnG=Search'#&as_sdt=2001'
        page = urllib2.urlopen(query).read()
        results = re.findall(
          r'<div[^>]*gs_rt[^<]*<h3[^>]*>[^<]*<a[^>]*>([^<]*).*href="([^">]+)',
          page)
        return results
    else:
        return []

def process(args):
    names = [] + args.get('name', '').split()
    emails = []
    if 'email' in args:
        emails += [args['email']]
    if len(names) + len(emails) > 0:
        results = scholar(names, emails)
        html = '<div class="citations">'
        if len(results) > 0:
            for result in results:
                html += '<div class="citation"><a href="' + result[1] + '">' \
                  + result[0] + '</a></div>'
        else:
            html += 'No citations info'
        return {'html':html + '</div>'}

if __name__ == '__main__':
    results = process(names = ['Luddy', 'Harrison'])
    print results
