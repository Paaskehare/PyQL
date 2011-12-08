#!/usr/bin/env python
# encoding: utf-8

from urllib2 import urlopen
from urllib import quote_plus
import re

weapons_re = re.compile('<div class="col_weapon">(?P<weapon>[\w\s]+)<\/div>\s+'
                        + '<div class="col_frags">(?P<frags>[\d\,]+)<\/div>\s+'

                        + '<div class="col_accuracy"( title="Hits: (?P<hits>[\d\,]+) Shots: (?P<shots>[\d\,]+)")?>'
                        + '<span class="text_tooltip">(?P<accuracy>\d+)%<\/span><\/div>\s+'
                        + '<div class="col_usage">\s*(?P<usage>\d+)%<\/div>'
                        , re.S)

stats_re = {
    'registered': re.compile('<b>Member Since:</b> ([a-zA-Z0-9 \.\,]+)<br />'),
    'playtime': re.compile('<b>Time Played:</b> <span class="text_tooltip" title="Actual Time: ([\d\.:]+)">(\d+) days</span><br />'),
    'lastgame': re.compile('<b>Last Game:</b>\s*<span class="text_tooltip" title="([\d+ /:]+)">(\d+) days ago</span>'),
    'wins': re.compile('<b>Wins:</b> ([\d\,]+)<br />'),
    'loses': re.compile('<b>Losses / Quits:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'frags': re.compile('<b>Frags / Deaths:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'hits': re.compile('<b>Hits / Shots:</b> ([\d\,]+) / ([\d\,]+)<br />'),
    'acc': re.compile('<b>Accuracy:</b> ([\d\.]+)%<br />'),
    'arena': re.compile('<b>Arena:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
    'gametype': re.compile('<b>Game Type:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
    'weapon': re.compile('<b>Weapon:</b> ([a-z A-Z0-9\-\_]+)\s*<div', re.S),
}

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
    registered = ""
    playtime = 0
    playtime_exact = ""
    lastgame = ""
    lastgame_days = 0
    kills = 0
    deaths = 0
    wins = 0
    loses = 0
    quits = 0
    frags = 0
    accuracy = 0.0
    arena = ""
    gametype = ""
    weapon = ""
    weapons = {}

    def __init__(self, username, stats=True, weapons=False):
        self.username = username
        self.contents = self._get_profile()
        if stats:
          self.scrape_stats()
        if weapons:
          self.scrape_weapons()

    def _tonumber(self, s):
        return int(s.replace(',', ''))

    def _get_profile(self):
        url = 'http://www.quakelive.com/profile/statistics/' + quote_plus(self.username)
        contents = ""
        try:
            page = urlopen(url)
            contents = page.read()
            page.close()
        except:
            pass
        return contents

    def scrape_stats(self):
        global stats_re
        r = stats_re
 
        if self.contents:
            content = self.contents

            self.registered = r['registered'].search(content).group(1)

            t = r['playtime'].search(content).groups()
            self.playtime, self.playtime_ago = t[0], int(t[1])

            t = r['lastgame'].search(content).groups()
            self.lastgame, self.lastgame_days = t[0], int(t[1])

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
            return 1
        return 0
      
    def scrape_weapons(self):
        global weapons_re, short_names
        s = short_names

        if self.contents:
            weapons = re.finditer(weapons_re, self.contents)
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
        return 0
