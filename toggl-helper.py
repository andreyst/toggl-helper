from datetime import date, time, datetime, timedelta, timezone
from toggl import Toggl
import argparse
import copy
import dateutil.parser
import json
import settings
import sys

def query_yes_no(question, default="yes"):
    """Ask a yes/no question via input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {"yes": True, "y": True, "ye": True,
             "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        eprint(question + prompt, end="")
        choice = input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


def parse_args():
  argparser = argparse.ArgumentParser()
  argparser.add_argument("--date", "-d", help="Day to fill, YYYY-MM-DD")
  args = argparser.parse_args()

  if args.date:
    try:
      args.date = dateutil.parser.parse(args.date).date()
    except Exception as e:
      eprint("Caught exception while trying to convert --date parameter: %s" % str(e))
      raise e

  if not args.date:
    args.date = date.today() + timedelta(days=1)

  return args


def main():
  args = parse_args()
  toggl = Toggl(settings.TOGGL_TOKEN)

  startDate = (datetime.now(timezone.utc) - timedelta(days=90)).isoformat()
  endDate = datetime.now(timezone.utc).isoformat()
  timeEntries = toggl.getTimeEntries(startDate, endDate)

  entriesByWeekday = { str(k): {} for k in range(6) }

  for te in timeEntries:
    startDate = dateutil.parser.parse(te['start'])
    te['startDate'] = startDate
    weekDay = str(startDate.weekday())
    key = ("%s!%s!%s!%s" % (te['description'], startDate.hour, startDate.minute, te['duration']))
    if weekDay not in entriesByWeekday:
      entriesByWeekday[weekDay] = {}
    if key not in entriesByWeekday[weekDay]:
      entriesByWeekday[weekDay][key] = {
        'wid': te['wid'],
        'pid': te.get('pid', None),
        'description': te['description'],
        'start': time(te['startDate'].hour, te['startDate'].minute, tzinfo=timezone.utc),
        'duration': te['duration'],
        'tags': te.get('tags', []),
        'count': 0
      }
    entriesByWeekday[weekDay][key]['count'] += 1

  for day, entries in entriesByWeekday.items():
    entriesByWeekday[day] = { k: entries[k] for k in entries if entries[k]['count'] > 1 }

  weekday = str(args.date.weekday())
  entries = sorted(entriesByWeekday[weekday].values(), key=lambda entry: entry['start'])
  for te in entries:
    startDate = datetime.combine(args.date, te['start'])
    endDate = startDate + timedelta(seconds=te['duration'])
    prompt = "Add {} from {} to {} (duration {} sec)?".format(te['description'], startDate, endDate, te['duration'])
    newTe = copy.deepcopy(te)
    newTe['start'] = startDate
    if query_yes_no(prompt, "no"):
      res = toggl.createTimeEntry(newTe)
      if 'data' in res and 'id' in res['data'] and res['data']['id'] > 0:
        eprint("OK!")
      else:
        eprint("WARNING: Check output - " + str(res))

  # print(json.dumps(entriesByWeekday, ensure_ascii=False, default=json_serial))

if __name__ == "__main__":
    main()
