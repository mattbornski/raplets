#!/usr/bin/env python

import cookielib
import couchdb
import getpass
import htmllib
import re
import simplejson
import sys
import traceback
import urllib2
import urlparse
#import xmllib

import ClientForm

login_urls = ['https://www.kickball.com/user/login']

# Register a custom User-Agent string so that people don't slam the
# door on us.  Some people don't take kindly to unidentified robots.
#opener = urllib2.build_opener()
#opener.addheaders = [
#  ('User-Agent', 'mattborn dev-mode Raplet'),
#]
#urllib2.install_opener(opener)

def unescape(s):
    p = htmllib.HTMLParser(None)
    p.save_bgn()
    p.feed(s)
    return p.save_end()

# Essentially a tuple of the player id, player's role, and the team.
# The team is unique to each season, which is unique to a division.
#class sop:
#    def __init__(self, player, role, team):
#        self.player = player
#        self.role = role
#        self.team = team

# Essentially a tuple of the season id and the team name.
class team:
    def __init__(self, sop, name, database = None):
        self.database = database
        self._sop = sop
        self._name = name
        self.id = self._sop + self._name
        self._colors = None
    def colors(self):
        if self._colors is None:
            try:
                # Check in the database first.
                self._colors = self.database['teamcolors' + self.id]['colors']
                return self._colors
            except:
                pass
            try:
                # Retrieve the color scheme associated with this team.
                # The teams can be viewed and scraped from
                #   "https://www.kickball.com/node/<sop id>"
                url = 'https://www.kickball.com/node/' + self._sop
                names = [self._name, unescape(self._name)]
                page = urllib2.urlopen(url).read()
                colors = None
                for name in names:
                    try:
                        colors = re.findall(
                          'background-color:\W*#?([0-9a-fA-F]{6}).*'
                          + '[ ;"]color:\W*#?([0-9a-fA-F]{6}).*' + name,
                          page)
                        if len(colors) > 0:
                            self._colors \
                              = {'color':colors[0][0], 'contrast':colors[0][1]}
                            try:
                                self.database['teamcolors' + self.id] \
                                  = {'colors':self._colors}
                            except:
                                print traceback.format_exc()
                            break
                    except:
                        # Try the next one.
                        continue
            except:
                print 'Could not parse colors.'
                print 'Season "' + self._sop + '"'
                print 'Team "' + '" / "'.join(names) + '"'
                print 'URL "' + url + '"'
                print traceback.format_exc()
        if self._colors is not None:
            return self._colors
        else:
            # Sane fallback.
            return {'color':'FFFFFF', 'contrast':'000000'}

class player:
    def __init__(self, email = None, id = None, database = None):
        self.database = database
        self._sops = None
        self.id = id
        if email is not None:
            self.identify(email)
    def identify(self, email):
        email = urllib2.quote(email)
        try:
            # Check in the database first.
            self.id = self.database['playeremails' + email]['id']
        except:
            # Retrieve the id number associated with this email.
            # The users can be searched and scraped from
            #   "https://www.kickball.com/user/"
            url = 'https://www.kickball.com/search/user/' + email
            matches = re.findall(
              r'kickball.com/user/([0-9]+)',
              urllib2.urlopen(url).read())
            for id in matches:
                self.id = id
                break
            try:
                self.database['playeremails' + email] = {'id':self.id}
            except:
                print traceback.format_exc()
    def sops(self):
        if self._sops is None:
            if self.id is not None:
                try:
                    # Check in the database first.
                    self._sops \
                      = self.database['playerseasons' + self.id]['sops']
                except:
                    # Retrieve the seasons which this player occurs in.
                    # The season listing can be scraped from
                    #   "https://www.kickball.com/user/<id>/playercard"
                    url = 'https://www.kickball.com/user/' \
                      + self.id + '/playercard'
                    matches = re.findall(
                      r'href="/user/' + self.id \
                        + '/playercard/([0-9]+)">([^<]*)',
                      urllib2.urlopen(url).read())
                    self._sops = []
                    for (season_id, text) in matches:
                        sop = {}
                        (d, s, t) = re.split('\W*[:-]\W*', text)
                        sop['id'] = season_id
                        sop['division'] = d
                        sop['season'] = s
                        sop['team'] = t
                        self._sops.append(sop)
                    # If that all worked, then let's try to save this info.
                    try:
                        self.database['playerseasons' + self.id] \
                          = {'sops':self._sops}
                    except:
                        print traceback.format_exc()
        if self._sops is not None:
            return self._sops
        else:
            return []
    def html(self):
        try:
            # Check in the database first.
            raise NotImplemented
        except:
            # Regenerate the HTML.
            html = '<div class="waka">'
            # Depends upon the current behavior where the WAKA website gives
            # us seasons in reverse-chronological order.
            sops = self.sops()
            if len(sops) > 0:
                for sop in reversed(sops):
                    t = team(sop['id'], sop['team'], self.database)
                    colors = t.colors()
                    html += '<div class="sop">' + sop['division'] + ' (' + sop['season'] + ') <div class="team" style="background-color: #' + colors['color'] + '; color: #' + colors['contrast'] + ';">' + sop['team'] + '</div></div>'
#                try:
#                    self.database[''] = html
#                except:
#                    pass
            else:
                html = '<div>No kickball info.'
            return html + '</div>'
    def json(self):
        try:
            # Check in the database first.
            pass
        except:
            # Regenerate.
            pass

class season:
    def __init__(self, id):
        self.id = id
    def players(self):
        # Retrieve the season roster.
        # The roster can be scraped from
        #   "http://www.kickball.com/og_waka_roster/users/<id>"
        pass

class database:
    domain = 'mattborn.cloudant.com'
    def __init__(self, creds):
        self.server = couchdb.Server('https://' \
          + creds['username'] + ':' + creds['password'] + '@' + self.domain)
        try:
            self.table = self.server['raplet_waka']
        except:
            self.table = self.server.create('raplet_waka')
        auth(creds)
    def __getitem__(self, key):
        return self.table[key]
    def __setitem__(self, key, value):
        self.table[key] = value
    # Pass through functions.
    def player(self, *args, **kwargs):
        kwargs['database'] = self
        return player(*args, **kwargs)

#class scraper:
def auth(creds):
    cookiejar = cookielib.LWPCookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookiejar))
    urllib2.install_opener(opener)
    for url in login_urls:
        try:
            forms = ClientForm.ParseResponse(
              urllib2.urlopen(url), backwards_compat = False)
            for form in forms:
                button = None
                for control in form.controls:
                    if control.name == 'name':
                        control.value = creds['username']
                    elif control.name == 'pass':
                        control.value = creds['password']
                    elif control.name == 'op':
                        button = control
                if button is not None:
                    request = form.click(button.name)
                    response = urllib2.urlopen(request)
                    break
        except:
            print 'Could not parse "' + url + '".'
            print traceback.format_exc()

if __name__ == '__main__':
    creds = {'username':'mattborn', 'password':getpass.getpass()}
    auth(creds)
    db = database(creds)
    for email in sys.argv[1:]:
        p = player(email = email, database = db)
        print p.sops()
