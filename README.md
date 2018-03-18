# toggl-helper

`toggl-helper` helps prefill your day with recurring time entries on this day in last 3 months.

Currently it calculates recurring entries very simply: if there are two or more entries with the same description with same start hour:minute and same duration on same weekday on two different dates, they are considered recurring. This algorithm will be further expanded to account for more complex cases like same entries with slightly drifting start times and durations, or entries with descriptions that start with the same prefix (e.g. "Meeting with Bob - about login" and "Meeting with Bob - about user page").

:boom: Caveat: tags and projects are not used in comparison, but new time entries are created with tags and projects from the first entry discovered.

## Installation

```
$ git clone https://github.com/andreyst/toggl-helper
$ cd toggl-helper
$ pipenv --three install
```

## Usage

```
$ python toggl-helper.py
# Will analyze last 3 months and offer to fill tomorrow with recurring items found on the weekday of tomorrow's date

$ python toggl-helper.py --date 2018-03-19
# Will do the same for the date 2018-03-19 and, since this date was Monday, for recurring items on Mondays
```
