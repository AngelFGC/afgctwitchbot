# AnatoleBot

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT) 
[![Python 3](https://img.shields.io/badge/python-2-blue.svg)](https://www.python.org/)

A small Twitch bot using [TwitchObserver](https://github.com/joshuaskelly/twitch-observer)

## How to install

1. Install TwitchObserver
```
$ pip install twitchobserver
```
2. Run the bot
```
$ python anatole_bot.py <username> <oaut_token> <channel> <is_bot_mod>
```
Where:
* `<username>` and `<oauth_token>` are Twitch login credentials for the bot,
* `<channel>` is the channel the bot will be interacting with,
* `<is_bot_mod>` should be True if the bot has mod-level privileges in `<channel>`, False otherwise.

## How to use

These are the available commands when the bot is running on a channel.

### `!roll` : Dice Roller

Synthax: `!roll <n>d<k>[<op><x>]`, where:
* `<n>` number of dice
* `<k>` size of dice
* `<op>` operation carried out in the dice roll. Optional.
* `<x>` parameter for the operation. Required only when `<op>` is also given.

The valid operations for <op> are:
* `+` & `-` adds/substract `<x>` to the sum of all dice rolled
* `*` & `/` multiplies/divides the sum of all dice rolled by `<x>`
* `>` counts the number of dice rolled with a result of `<x>` or greater
* `<` counts the number of dice rolled with a result of `<x>` or less

Some example rolls:

> `!roll 1d20`

> `!roll 4d6+2`

> `!roll 3d8-1`

> `!roll 2d10*2`

> `!roll 4d10>6`

> `!roll 3d6<3`

### `!bop` : An Updated version of IRC's classic trout `/slap`

Synthax: `!bop <bopper> <bopped>`

Hitting is random, damage is random, even object used is random.

### `!vote` : Vote-capturing<sup>§</sup>

Synthax: `!vote <duration> <options>`, where:
* `<duration>` is how long the voting round will last, in seconds
* `<options>` is a list of one-word options, separated by a space that the chatters/viewers will vote on

Only one vote per user is allowed, the first vote they make is the vote that will be recorded.

After `<duration>` seconds, the vote ends and the bot announces the results.

### `!about` : Print information about the bot

### `!goodbye` : Shut down the bot<sup>§</sup>

*<sup>§</sup>: These ommands are available for mod-level users only*
