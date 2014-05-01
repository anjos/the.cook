#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to manage available lunch menus"""

import os
import getpass
import datetime
import logging
from .models import User, Lunch, Subscription, format_date

def get_current_user(session):

  retval = session.query(User).filter(User.id==os.getuid()).first()
  if retval: return retval

  #otherwise, create it
  user = User(os.getuid(), getpass.getuser())
  session.add(user)
  session.commit()
  logging.info("Added `%s'" % user)
  return user

def add(session, date, menu_french, menu_english):
  """Adds a new lunch menu into the system"""

  user = get_current_user(session)
  existing = lunch_at_date(session, date)

  if existing:
    logging.error("Trying to add another lunch to `%s' is not possible since we already have one setup `%s'" % (format_date(date), existing))
    return None

  lunch = Lunch(date, menu_french, menu_english, user)
  session.add(lunch)
  logging.info("Added `%s'" % lunch)
  session.commit()
  return lunch

def remove(session, date, force=False):
  """Removes the lunch menu from the system"""

  lunch = session.query(Lunch).filter(Lunch.date == date).first()

  if not lunch:
    logging.error("Could not find lunch on `%s'" % format_date(date))
    return None

  if lunch.subscriptions and not force:
    logging.error("Found %d subscriptions associated with lunch to be deleted, but no `--force' - aborting deletion of `%s'" % (len(lunch.subscriptions), lunch))
    return None

  for s in lunch.subscriptions:
    session.delete(s)
    logging.info("Also deleted `%s'" % s)

  session.delete(lunch)
  logging.info("Deleted `%s'..." % lunch)
  session.commit()

  return lunch

def next_lunch(session):
  """Get next possible lunch.

  Returns a lunch object or None, if no applicable lunch was found.
  """

  today = datetime.date.today()
  query = session.query(Lunch).filter(Lunch.date>=today).order_by(Lunch.date)
  now = datetime.datetime.now()
  cutoff = datetime.datetime(today.year, today.month, today.day, 14)

  if query.count() == 0: return None

  retval = query.first()
  if retval.date == today and now > cutoff:
    if query.count() > 1: retval = query[1]
    else: return None

  return retval

def next_subscribeable_lunch(session, date=None):
  """Get next possible lunch to subscribe after a certain date

  If the date is ``None`` or represents today, then the cut-off time (18h00) is
  taken into consideration.

  Returns a lunch object or None, if no applicable lunch was found.
  """

  today = datetime.date.today()
  if date <= today:
    date = datetime.datetime(today.year, today.month, today.day, 18)

  retval = session.query(Lunch).filter(Lunch.date>=date).order_by(Lunch.date)

  return retval.first()

def lunch_at_date(session, date):
  """Gets the lunch on the given date or returns None"""

  retval = session.query(Lunch).filter(Lunch.date==date)

  if retval.count() == 0: return None
  return retval.first()

def lunches_in_range(session, start, end):
  """Returns all available lunches in the (start, end) range of dates"""

  return session.query(Lunch).filter(Lunch.date >= start, Lunch.date <= end).order_by(Lunch.date)

def subscribe(session, date, persons):
  """Subscribes a new user into the database, for a given lunch"""

  user = get_current_user(session)
  lunch = next_subscribeable_lunch(session, date)

  if lunch is None:
    logging.error("Cannot find lunch with open subscription for the input date (%s)" % format_date(date))
    return None

  subscribed = session.query(Subscription).filter(
      Subscription.lunch_id == lunch.id,
      Subscription.user_id == user.id
      ).first()
  if subscribed is None:
    subscription = Subscription(lunch, user, persons)
    session.add(subscription)
    logging.info("Added `%s'" % subscription)
    session.commit()
    return subscription
  else:
    logging.warn("User `%s' is already subscribed for lunch at %s" %
        (user.name, format_date(lunch.date)))
    return subscribed

def list_entries(session, start, end, long_desc):
  """List all existing entries in the system, matching a range"""

  lunches = lunches_in_range(session, start, end)

  if not lunches:
    logging.error("Cannot find lunches in range `%s' until `%s'",
        format_date(start), format_date(end))
    return

  retval = []
  for l in lunches:
    retval.append("%s, %d subscriber(s)" % (l, l.total_subscribers()))
    if long_desc:
      retval[-1] += ":"
      for s in l.subscriptions: retval.append("  " + str(s))

  return retval
