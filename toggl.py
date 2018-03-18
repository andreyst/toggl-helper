import requests
import sys
import json
from datetime import date, time, datetime

def eprint(*args, **kwargs):
  print(*args, file=sys.stderr, **kwargs)


def json_serial(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date, time)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))


class Toggl:

  urlPrefix = "https://www.toggl.com/api/v8"

  def __init__(self, token):
    self.token = token

  def _request(self, urlSuffix, params=None, data=None, method='get'):
    auth = (self.token, 'api_token')
    headers = {
      'Content-Type': 'application/json',
      'User-Agent': 'curl/7.54.0',
    }

    url = self.urlPrefix + urlSuffix
    kwargs = {}
    if params is not None:
      kwargs['params'] = params
    if data is not None:
      kwargs['data'] = json.dumps(data, default=json_serial)

    r = getattr(requests, method)(url, auth=auth, headers=headers, **kwargs)
    # eprint(r.url)
    # eprint(r.url, params, data, auth, headers, r.history, r.request.body)
    try:
      buf = r.json()
    except json.decoder.JSONDecodeError as e:
      eprint("ERROR: Unable to decode json response")
      eprint("ERROR: Response code was: %s" % r.status_code)
      eprint("Raw response was: '%s'" % r.text)
      raise e

    return buf

  def getTimeEntries(self, startDate=None, endDate=None):
    urlSuffix = '/time_entries'
    params = {}
    if startDate:
      params['start_date'] = startDate
    if endDate:
      params['end_date'] = endDate

    return self._request('/time_entries', params=params)

  def createTimeEntry(self, timeEntry):
    timeEntry['created_with'] = 'https://github.com/andreyst/toggl-helper'
    data = { 'time_entry': timeEntry }

    return self._request('/time_entries', data=data, method='post')
