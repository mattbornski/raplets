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

def scholar(names):
    query = u'http://scholar.google.com/scholar?q='
    if len(names) > 0:
        query += 'author:' + '+author:'.join(names)
        query += '&'
    query += 'hl=en&btnG=Search'#&as_sdt=2001'
    page = urllib2.urlopen(query).read()
    results = re.findall(r'<div[^>]*gs_rt[^<]*<h3[^>]*>[^<]*<a[^>]*href="([^">]+)"[^>]*>([^<]*)', page)
    return results

def process(args):
    if 'name' in args:
        results = scholar(args['name'].split())
        html = '<div class="citations">'
        for result in results:
            html += '<div class="citation"><a href="' + result[0] + '">' \
              + result[1] + '</a></div>'
        return {'html':html + '</div>'}

if __name__ == '__main__':
    results = process({'name':'Luddy Harrison'})
    print results
