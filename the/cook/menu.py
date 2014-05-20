#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to manage available lunch menus"""

import os
import six
import getpass
import datetime
import logging
from .models import User, Lunch, Subscription, format_date, format_datetime

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

def next_subscribeable_lunch(session):
  """Get next possible lunch.

  Returns a lunch object or None, if no applicable lunch was found.
  """

  today = datetime.date.today()

  query = session.query(Lunch).filter(Lunch.date>=today).order_by(Lunch.date)

  if query.count() == 0: return None

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  now = datetime.datetime.now()
  today_at_18 = datetime.datetime(today.year, today.month, today.day, 18, 5)

  # special condition: there is a lunch tomorrow, but you cannot subscribe to
  # it any longer because it is more than 18h00 (the list has been sent to the
  # hotel already).
  retval = query.first()
  if retval.date == today or (retval.date == tomorrow and now > today_at_18):
    if query.count() > 1: return query[1] #returns the next possible lunch
    else: return None

  return retval

def lunch_at_date(session, date):
  """Gets the lunch on the given date or returns None"""

  if isinstance(date, six.string_types) and date == 'next':
    return next_subscribeable_lunch(session)

  retval = session.query(Lunch).filter(Lunch.date==date)

  if retval.count() == 0: return None
  return retval.first()

def lunches_in_range(session, start, end):
  """Returns all available lunches in the (start, end) range of dates"""

  return session.query(Lunch).filter(Lunch.date >= start, Lunch.date <= end).order_by(Lunch.date)

def subscriptions_in_range(session, username, start, end):
  """Returns all available subscriptions in the (start, end) range of dates"""

  return session.query(Subscription).join(Lunch).join((User, User.id == Subscription.user_id)).filter(Lunch.date >= start, Lunch.date <= end, User.name == username).distinct(Subscription.date).order_by(Subscription.date)

def unsubscribe(session, date):
  """Unsubscribes the person from the lunch"""

  user = get_current_user(session)
  lunch = lunch_at_date(session, date)

  if lunch is None:
    logging.error("Cannot find lunch with open unsubscription for the input date (%s)" % format_date(date))
    return None

  #special case, if the date:

  subscribed = session.query(Subscription).filter(
      Subscription.lunch_id == lunch.id,
      Subscription.user_id == user.id
      ).first()
  if subscribed is None:
    logging.error("User `%s' is not subscribed for lunch at `%s'" % (user.name, format_date(lunch.date)))
  else:
    session.delete(subscribed)
    logging.info("Deleted `%s'..." % subscribed)
    session.commit()

  return subscribed

def subscribe(session, date, persons):
  """Subscribes a new user into the database, for a given lunch"""

  user = get_current_user(session)
  lunch = lunch_at_date(session, date)

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

def lunch_list(session, start, end, long_desc):
  """List all existing entries in the system, matching a range"""

  lunches = lunches_in_range(session, start, end)

  if not lunches:
    logging.error("Cannot find lunches in range `%s' until `%s'",
        format_date(start), format_date(end))
    return

  retval = []
  for l in lunches:
    retval.append("[%s] %s, %d subscriber(s)" % \
        (format_date(l.date), l.menu_english, l.total_subscribers()))
    if long_desc:
      if len(l.subscriptions): retval[-1] += ":"
      for s in l.subscriptions:
        retval.append("  - %s: %d person(s), subscribed `%s'" % \
            (s.user.name_and_email(), s.persons, format_datetime(s.date)))

  return retval

def user_list(session, username, start, end, long_desc):
  """List all existing entries in the system for a given user, matching a range"""

  subscriptions = subscriptions_in_range(session, username, start, end)

  if not subscriptions:
    logging.error("Cannot find subscribed lunches for user `%s' in range `%s' until `%s'", username, format_date(start), format_date(end))
    return

  retval = ["User `%s' subscribed to the following lunches:" % username]
  for s in subscriptions:
    l = s.lunch
    if long_desc:
      retval.append("  - [%s] %s, %d total subscriber(s)" % \
          (format_date(l.date), l.menu_english, l.total_subscribers()))
    else:
      retval.append("  - %s, %d subscriber(s)" % (format_date(l.date), l.total_subscribers()))

  return retval
