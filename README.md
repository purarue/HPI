Note: This is currently going through a restructure as I'm syncing
back to master and using this repo as a namespace subpackage

**TLDR**: I'm using `HPI`(Human Programming Interface) package as a means of unifying, accessing and
interacting with all of my personal data.

It's a Python library (named `my`), a collection of modules for:

- social networks: posts, comments, favorites, searches
- shell/program histories (zsh, python, mpv, firefox)
- reading: e-books and pdfs
- programming (github/commits)
- todos and notes
- instant messaging
- bank account history/transactions
- some video game achievements/history

[_Why?_](https://github.com/karlicoss/HPI#why)

This is built on top of and uses lots of the machinery from [`karlicoss/HPI`](https://github.com/karlicoss/HPI)

### My Modules

- `my.browsing`, using my [`ffexport`](https://github.com/seanbreckenridge/ffexport) tool to backup/parse firefox history
- `my.zsh`, access to my shell history w/ timestamps
- `my.google`, parses lots of (~250,000) events (youtube, searches, phone usage, comments, location history) from [google takeouts](https://takeout.google.com/)
- `my.food`, tracks calorie/water intake; imports from [`calories`](https://github.com/zupzup/calories). I use [this](https://github.com/seanbreckenridge/calories-scripts/) interface most of the time to add food I eat.
- `my.body_log` to track body functionality (e.g. weight) (with a TUI using [`autotui`](https://github.com/seanbreckenridge/autotui))
- `my.mpv`, accesses movies/music w/ activity/metdata that have played on my machine, facilitated by a [mpv history daemon](https://github.com/seanbreckenridge/mpv-history-daemon)
- `my.discord`, parses ~1,000,000 messages/events from the discord GDPR export, parser [here](https://github.com/seanbreckenridge/discord_data)
- `my.money`, bank account transactions/balance history from [my budget tool](https://github.com/seanbreckenridge/mint)
- `my.todotxt`, to track my to-do list history (using backups of my [`todotxt`](http://todotxt.org/) files)
- `my.rss`, keeps track of when I added/removed RSS feeds (for [`newsboat`](https://newsboat.org/))
- `my.ipython`, for timestamped python REPL history
- `my.ttt`, to parse shell/system history tracked by [`ttt`](https://github.com/seanbreckenridge/ttt)
- `my.battery`, to parse basic battery percentage over time on my laptop
- `my.window_watcher`, to parse active window events (what application I'm using/what the window title is) using [`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)
- `my.location`, merges data from [`gpslogger`](https://github.com/mendhak/gpslogger), `apple`, `google`, `discord`, `games.blizzard`, and `facebook` to provide location data (goes back ~10 years)
- `my.games.chess`, to track my [chess.com](https://www.chess.com) games, using [`chessdotcom_export`](https://github.com/seanbreckenridge/chessdotcom_export)

### 'Historical' Modules

These are modules to parse GDPR exports/data from services I used to use, but don't anymore. They're here to provide more context into the past.

- `my.apple`, parses game center and location data from the apple GDPR export
- `my.facebook`, to parse the GDPR export I downloaded from facebook before deleting my account
- `my.games.league`, gives league of legends game history using [`lolexport`](https://github.com/seanbreckenridge/lolexport)
- `my.games.steam`, for steam achievement data and game playtime using [`steamscraper`](https://github.com/seanbreckenridge/steamscraper)
- `my.games.blizzard`, for general battle.net event data [parsed from a gdpr export](https://github.com/seanbreckenridge/blizzard_gdpr_parser)
- `my.old_forums`, random posts from forums I used to use in the past, see [`forum_parser`](https://github.com/seanbreckenridge/forum_parser)
- `my.skype` to parse a couple datetimes from the skype GDPR export
- `my.spotify`, to parse the GDPR export from spotify, mostly for songs from my playlists from years ago

See [here](https://github.com/seanbreckenridge/dotfiles/blob/master/.config/my/my/config/__init__.py) for config.

### In-use from [karlicoss/HPI](https://github.com/karlicoss/HPI)

- `my.coding` to track git commits across the system
- `my.github` to track github events/commits and parse the GDPR export, using [`ghexport`](https://github.com/karlicoss/ghexport)
- `my.reddit`, get saved posts, comments. Uses [`rexport`](https://github.com/karlicoss/rexport) to create backups of recent activity periodically, and [`pushshift`](https://github.com/seanbreckenridge/pushshift_comment_export) to get old comments.
- `my.smscalls`, exports call/sms history using [SMS Backup & Restore](https://play.google.com/store/apps/details?id=com.riteshsahu.SMSBackupRestore&hl=en_US)

### Companion Libraries

Disregarding tools which actively collect data (like [`ttt`](https://github.com/seanbreckenridge/ttt)/[`window_watcher`](https://github.com/seanbreckenridge/aw-watcher-window)), I have some other libraries I've created for this project, to provide more context to some of the data.

- [`ipgeocache`](https://github.com/seanbreckenridge/ipgeocache) - for any IPs gathered from data exports, provides geolocation info, so I have partial location info going back to 2013
- [`url_metadata`](https://github.com/seanbreckenridge/url_metadata) - caches youtube subtitles, url metadata (title, description, image links), and a html/plaintext summary for any URL
- [`HPI_API`](https://github.com/seanbreckenridge/HPI_API) - automatically creates a JSON API for HPI modules

### Ad-hoc and interactive

Some basic examples.

When was I most using reddit?

```python
>>> import collections, my.reddit, pprint
>>> pprint.pprint(collections.Counter([c.created.year for c in my.reddit.comments()]))
Counter({2016: 3288,
         2017: 801,
         2015: 523,
         2018: 209,
         2019: 65,
         2014: 4,
         2020: 3})
```

Most common shell commands?

```python
>>> import collections, pprint, my.zsh
# lots of these are git-related aliases
>>> pprint.pprint(collections.Counter([c.command for c in my.zsh.history()]).most_common(10))
[('ls', 51059),
 ('gst', 11361),
 ('ranger', 6530),
 ('yst', 4630),
 ('gds', 3919),
 ('ec', 3808),
 ('clear', 3651),
 ('cd', 2111),
 ('yds', 1647),
 ('ga -A', 1333)]
```

What websites do I visit most?

```python
>>> import collections, pprint, my.browsing, urllib
>>> pprint.pprint(collections.Counter([urllib.parse.urlparse(h.url).netloc for h in my.browsing.history()]).most_common(5))
[('github.com', 20953),
 ('duckduckgo.com', 10146),
 ('www.youtube.com', 10126),
 ('discord.com', 8425),
 ('stackoverflow.com', 2906)]
```

Song I've listened to most?

```python
>>> import collections, my.mpv
>>> collections.Counter([m.path for m in my.mpv.history()]).most_common(1)[0][0]
'/home/sean/Music/Toby Fox/Toby Fox - UNDERTALE Soundtrack (2015) [V0]/085 - Fallen Down (Reprise).mp3'
```

---

### Other Changes

- [`setup/install`](setup/install) first installs the upstream repo ([`karlicoss/HPI`](https://github.com/karlicoss/HPI)) as a editable namespace package, then sets up this repository as a bunch of sub-modules. (TODO: add minimal hpi namespace example)
- [`jobs`](./jobs) contains anacron-like jobs that are run periodically, using [`bgproc`](https://github.com/seanbreckenridge/bgproc) and [`evry`](https://github.com/seanbreckenridge/evry). So, this repo has both the [DAL](https://beepb00p.xyz/exports.html#dal) and the scripts to backup the data. I run the jobs in the background using supervisor, see the `run_jobs` script [`here`](https://github.com/seanbreckenridge/dotfiles/tree/master/.local/scripts/supervisor)
- Added a little query interface to `my.utils`: to do some type introspection to query/order functions/events based on datetime, and to dump any of the computed events to JSON. It includes some helpers to serialize NamedTuple/dataclass and date-like objects:

```python
>>> from my.utils.serialize import dumps
>>> from my.utils.query import most_recent, find_hpi_function
>>> print(dumps(list(most_recent(find_hpi_function("my.zsh", "history")(), events=2)), indent=2))
[
  {
    "dt": 1609195654,
    "duration": 0,
    "command": "ls"
  },
  {
    "dt": 1609195491,
    "duration": 0,
    "command": "ls"
  }
]
```

That info is also available as a CLI interface, which I use to grab recent events so I can populate that info into my dashboard/menu bar. For example, to quickly grab how much water I've drank in the last day:

```
$ ./scripts/hpi_query my.food water --days 1 | jq '.[] | .glasses' | datamash sum 1
4.5
```

### TODO:

- [ ] create HPI example namespace package
- [ ] configure `my.stackexchange` API tokens: https://github.com/karlicoss/stexport

create 'export modules' which keep these up to date:

- [ ] backup trakt? (have API access)
- [ ] backup MAL (ugh)

Need to do more research/figure out

- [ ] polar? some other reading system? formalize documents/configure `my.pdfs`
- [ ] email?
