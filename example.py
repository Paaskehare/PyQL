#!/usr/bin/env python
# encoding: utf-8

from quakelive import Player

# Only get the stats:
p = Player("paaskehare")
print(p.gametype)
print(p.accuracy)

# Get the stats and weapons:
p = Player("paaskehare", weapons=True)
print(p.weapon)
# stats for e.g. Railgun:
print(p.weapons['rg']['name'])
print(p.weapons['rg'])

# Dont get stats, we just need the weapons:
p = Player("paaskehare", stats=False, weapons=True)
for weapon in p.weapons:
  print('%(name)s - Accuracy: %(accuracy)s%% - Usage: %(usage)s%%' % p.weapons[weapon])
