#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 05:25:51 CEST

"""Validation routines"""

from datetime import date, datetime, timedelta
from .models import as_unicode

weekdays = [
    'monday',
    'tuesday',
    'wednesday',
    'thursday',
    'friday',
    'saturday',
    'sunday',
    ]

weekdays_short = [
    'mon',
    'tue',
    'wed',
    'thu',
    'fri',
    'sat',
    'sun',
    ]

def next_weekday(d, weekday):

  days_ahead = weekday - d.weekday()
  if days_ahead <= 0: # Target day already happened this week
    days_ahead += 7
  return d + timedelta(days_ahead)

def validate_date(o):
  """Validates the input string to be one of:

     * ``"next"`` - unchanged, means the next possible lunch
     * ``"today"`` - means the date of today
     * ``"tomorrow"`` - means the date of tomorrow
     * ``"mon"`` or ``"monday"`` - means the **next** monday
     * ``"dd"`` - means the day for the current month and year
     * ``"dd.mm"`` - means the day and month for the current year
     * ``"dd.mm.yy"`` - specifies day, month and year (with 2 digits)

  Returns the validated date.
  """
  today = date.today()

  if o is None: return 'next'

  dots = o.count('.')

  if dots == 0:
    if o.lower() == 'today': return today
    if o.lower() == 'tomorrow': return today + timedelta(days=1)
    if o.lower() == 'next': return o.lower()
    if o.lower() in weekdays:
      return next_weekday(today, weekdays.index(o.lower()))
    if o.lower() in weekdays_short:
      return next_weekday(today, weekdays_short.index(o.lower()))
    parsed = datetime.strptime(o, '%d')
    return date(today.year, today.month, parsed.day)
  elif dots == 1:
    parsed = datetime.strptime(o, '%d.%m')
    return date(today.year, parsed.month, parsed.day)
  elif dots == 2:
    parsed = datetime.strptime(o, '%d.%m.%y')
    return date(parsed.year, parsed.month, parsed.day)
  else:
    raise ValueError("Cannot parse date `%s' - use dd, dd.mm or dd.mm.yy")

def validate_range(o):
  """Validates the date range like this:
     * ``None`` -> the same as ``..``
     * ``start..`` -> from start-date
     * ``start..end`` -> precise start and end dates
     * ``..end`` -> until end-date
     * ``..`` -> all possible values
     * ``today..end`` -> from today
     * ``start..today`` -> up to today

  Returns a tuple with formal start and end dates
  """

  if o is None:
    return (date.min, date.max)

  valid = o.count('..')
  if not valid:
    raise ValueError('Date range should be in the format <start>..<end>')

  start, end = o.split('..', 1)
  if not start: start = date.min
  else: start = validate_date(start)
  if not end: end = date.max
  else: end = validate_date(end)

  return start, end

def validate_menu(o):
  """Validates the input menu:
     * menu en français
     * menu en français (english menu)

  Returns a tuple (french, english)
  """
  paren = o.count('(')

  if paren:
    french, english = o.split('(')
    french = french.strip()
    english = english.strip().strip(')').strip()

  else:
    french = o
    english = ''

  return as_unicode(french), as_unicode(english)
