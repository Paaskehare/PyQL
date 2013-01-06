#!/usr/bin/env python
# encoding: utf-8

from quakelive import Player

# Only get the stats:
p = Player("fragtion")
print(p.gametype)
print(p.accuracy)

# Get the stats and weapons:
p = Player("fragtion", weapons=True)

# Check if player exists:
if p.exists:
    print('Player exists')

print(p.weapon)
# stats for e.g. Railgun:
print(p.weapons['rg']['name'])
print(p.weapons['rg'])

# Dont get stats, we just need the weapons:
p = Player("fragtion", stats=False, weapons=True)
for weapon in p.weapons:
  print('%(name)s - Accuracy: %(accuracy)s%% - Usage: %(usage)s%%' % p.weapons[weapon])

# Get matches for the last four week, no stats, and no weapons:
p = Player("fragtion", stats=False)

p.scrape_matches(4) # defaults to last week, but we want the four last weeks

print(len(p.matches)) # number of matches

for match in p.matches:
    # This doesn't actually scrape the match data
    # It just shows the id
    print(match.id)

# get the json data for the latest match:
print(p.matches[0].get_json())
