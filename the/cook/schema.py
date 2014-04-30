#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 05:25:51 CEST

"""Validation routines"""

from datetime import date, datetime

def validate_email(o):
  """Validates the input string to be one of:
     * user@example.com
     * User <user@example.com>

  Returns a tuple (fullname, email)
  """
  from email.utils import parseaddr

  return parseaddr(o)

def validate_date(o):
  """Validates the input string to be one of:
     * dd
     * dd.mm
     * dd.mm.yy

  Returns the validated date.
  """
  today = date.today()

  dots = o.count('.')

  if dots == 0:
    if o.lower() == 'today': return today
    parsed = datetime.strptime(o, '%d')
    return date(today.year, today.month, parsed.day)
  elif dots == 1:
    parsed = datetime.strptime(o, '%d.%m')
    return date(today.year, parsed.month, parsed.day)
  elif dots == 2:
    return datetime.strptime(o, '%d.%m.%y')
  else:
    raise ValueError("Cannot parse date `%s' - use dd, dd.mm or dd.mm.yy")

def validate_range(o):
  """Validates the date range like this:
     * start.. -> start-date until end of times
     * start..end -> precise start and end dates
     * ..end -> start of times until end-date
     * .. -> start of times until end of times
     * today..end -> from today
     * start..today -> up to today

  Returns a tuple with formal start and end dates
  """

  valid = o.count('..')
  if not valid:
    raise ValueError('Date range should be in the format <start>..<end>')

  start, end = o.split('..', 1)
  if not start: start = datetime.min
  else: start = validate_date(start)
  if not end: end = datetime.max
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

  return french, english
