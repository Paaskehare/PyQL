#!/usr/bin/env python
# encoding: utf-8

from urllib2 import urlopen
from urllib import quote_plus
import re
from datetime import timedelta, date
import json

re_weapons = re.compile('<div class="col_weapon">(?P<weapon>[\w\s]+)<\/div>\s+'
                        + '<div class="col_frags">(?P<frags>[\d\,]+)<\/div>\s+'

                        + '<div class="col_accuracy"( title="Hits: (?P<hits>[\d\,]+) Shots: (?P<shots>[\d\,]+)")?>'
                        + '<span class="text_tooltip">(?P<accuracy>\d+)%<\/span><\/div>\s+'
                        + '<div class="col_usage">\s*(?P<usage>\d+)%<\/div>'
                        , re.S)

re_stats = {
    'registered': re.compile('<b>Member Since:</b> ([a-zA-Z0-9 \.\,]+)<br />'),
    'playtime': re.compile('<b>Time Played:</b> <span class="text_tooltip" title="Ranked Time: ([\d\.:]+) Unranked Time: ([\d\.:]+)">(.+?)</span><br />'),
    'lastgame': re.compile('<b>Last Game:</b>\s*<span class="text_tooltip" title="([\d+ /:]+)">(\d+) days ago</span>'),
    'wins': re.compile('<b>Wins:</b> ([\d\,]+)<br />'),
    'loses': re.compile('<b>Losses / Quits:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'frags': re.compile('<b>Frags / Deaths:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'hits': re.compile('<b>Hits / Shots:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'acc': re.compile('<b>Accuracy:</b> ([\d\.]+)%<br />'),
    'arena': re.compile('<b>Arena:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
    'gametype': re.compile('<b>Game Type:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
    'weapon': re.compile('<b>Weapon:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
    'recentmatches': re.compile('<div class="recent_match[^"]*" id="[a-z]{2,4}_([a-z0-9-]{36})_1"'),
}

re_match = re.compile('<div class="areaMapC" id="[a-z]{2,4}_([a-z0-9-]{36})_1">')

short_names = {
    'Gauntlet': 'g',
    'Machinegun': 'mg',
    'Shotgun': 'sg',
    'Grenade Launcher': 'gl',
    'Rocket Launcher': 'rl',
    'Lightning Gun': 'lg',
    'Railgun': 'rg',
    'Plasma Gun': 'pg',
    'BFG': 'bfg',
    'Chaingun': 'cg',
    'Nailgun': 'ng',
    'Proximity Mine': 'pm'
}

class Player:
    exists = False
    registered = ''
    playtime = ''
    playtime_ranked = ''
    playtime_unranked = ''
    lastgame = ''
    lastgame_days = 0
    kills = 0
    deaths = 0
    wins = 0
    loses = 0
    quits = 0
    frags = 0
    accuracy = 0.0
    arena = ''
    gametype = ''
    weapon = ''
    weapons = {}
    recent_matches = []
    elo = {'ca': 0, 'duel': 0, 'tdm': 0}

    matches = []

    def __init__(self, username, stats=True, weapons=False, elo=True):
        self.username = username
        self.contents = ""
        if stats or weapons or elo:
            self.contents = self._get_profile()
            if stats:
                self.scrape_stats()
            if weapons:
                self.scrape_weapons()
            if elo:
                self._get_elo()

    def _tonumber(self, s):
        return int(s.replace(',', ''))

    def _get_page(self, url):
        contents = ''
        try:
            page = urlopen(url)
            contents = page.read()
            page.close()
        except:
            pass
        return contents

    def _get_elo(self):
        url = 'http://qlranks.com/api/getElo.aspx?nick=' + quote_plus(self.username)
        contents = self._get_page(url)
        if contents:
            lines = contents.split('\n')
            for line in lines:
              l = line.split(':')
              t, v = l
              t, v = t.strip().lower(), v.strip()
              self.elo[t] = int(v) if not v == 'Not found.' else 0

    def _get_profile(self):
        url = 'http://www.quakelive.com/profile/statistics/' + quote_plus(self.username)
        return self._get_page(url)

    def _get_week(self, week_date):
        global re_match
        url = 'http://www.quakelive.com/profile/matches_by_week/%s/%s' % (quote_plus(self.username), week_date)
        contents = self._get_page(url)
        week = []
        if contents:
            matches = re.finditer(re_match, contents)
            
            week = [match.group(1) for match in matches]
        return week

    def scrape_stats(self):
        global re_stats
        r = re_stats
 
        if self.contents and 'Player not found: %s</span>' % self.username not in self.contents:
            self.exists = True
            content = self.contents

            self.registered = r['registered'].search(content).group(1)

            t = r['playtime'].search(content).groups()
            self.playtime_ranked, self.playtime_unranked, self.playtime = t[0], t[1], t[2]

            try:
              t = r['lastgame'].search(content).groups()
              self.lastgame, self.lastgame_days = t[0], int(t[1])
            except:
              pass

            self.wins = self._tonumber(r['wins'].search(content).group(1))

            t = r['loses'].search(content).groups()
            self.loses, self.quits = self._tonumber(t[0]), self._tonumber(t[1])

            t = r['frags'].search(content).groups()
            self.frags, self.deaths = self._tonumber(t[0]), self._tonumber(t[1])

            t = r['hits'].search(content).groups()
            self.hits, self.shots = self._tonumber(t[0]), self._tonumber(t[1])

            self.accuracy = float(r['acc'].search(content).group(1))

            self.arena = r['arena'].search(content).group(1)

            self.gametype = r['gametype'].search(content).group(1)

            self.weapon = r['weapon'].search(content).group(1)

            rm = re.finditer(r['recentmatches'], content)
            for match in rm:
                self.recent_matches.append(Match(match.group(1)))
            return 1
        return 0
      
    def scrape_weapons(self):
        global re_weapons, short_names
        s = short_names

        if self.contents:
            weapons = re.finditer(re_weapons, self.contents)
            for w in weapons:
                weapon = {'hits': 0, 'shots': 0, 'accuracy': 0}
                weapon['name'] = w.group('weapon')
                weapon['frags'] = self._tonumber(w.group('frags'))
                weapon['usage'] = w.group('usage')

                if weapon['name'] != 'Gauntlet':
                    weapon['hits'] = self._tonumber(w.group('hits'))
                    weapon['shots'] = self._tonumber(w.group('shots'))
                    weapon['accuracy'] = int(w.group('accuracy'))

                self.weapons[s[w.group('weapon')]] = weapon
            return 1
        return 0

    def scrape_matches(self, num_weeks=1):
        global match_re
        today = date.today()

        weeks = [(today - timedelta(7 * i)).strftime('%Y-%m-%d') for i in range(num_weeks)]

        for week in weeks:
            matches = self._get_week(week)
            for match in matches:
                self.matches.append(Match(match))
        self.matches.reverse()

class Match:
    id = ''
    def __init__(self, match_id):
       self.id = match_id
       self.data = None

    def _get_page(self, url):
        contents = ''
        try:
            page = urlopen(url)
            contents = page.read()
            page.close()
        except:
            pass
        return contents 

    def get_json(self):
        if not self.data:
            contents = self._get_page("http://www.quakelive.com/stats/matchdetails/%s" % self.id)
            if contents:
                self.data = json.loads(contents)
        return self.data
