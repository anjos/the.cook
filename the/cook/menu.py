#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to manage available lunch menus"""

import os
import getpass
from .models import User, Lunch, Subscription, connect

def get_current_user(session, args):

  retval = session.query(User).filter(User.id==os.getuid()).first()
  if retval: return retval

  #otherwise, create it
  user = User(os.getuid(), getpass.getuser())
  session.add(user)
  session.commit()
  print("Added `%s'" % user)
  return user

def add(args):
  """Adds a new lunch menu into the system"""

  session = connect(args['--dbfile'])
  user = get_current_user(session, args)
  lunch = Lunch(args['<date>'], args['<menu>'], user)
  session.add(lunch)
  print("Added `%s'" % lunch)
  session.commit()
  session.close()

def remove(args):
  """Removes the lunch menu from the system"""

  session = connect(args['--dbfile'])

  lunch = session.query(Lunch).filter(Lunch.date == args['<date>']).first()
  for s in lunch.subscriptions:
    print("Deleting `%s" % s)
    session.delete(s)

  print("Deleting `%s'" % lunch)
  session.delete(lunch)
  session.commit()

def subscribe(args):
  """Subscribes a new user into the database, for a given lunch"""

  session = connect(args['--dbfile'])
  user = get_current_user(session, args)
  lunch = session.query(Lunch).filter(Lunch.date == args['<date>']).first()
  subscribed = session.query(Subscription).filter(
      Subscription.lunch_id == lunch.id,
      Subscription.user_id == user.id
      ).first()
  if subscribed is None:
    subscription = Subscription(lunch, user, args['--persons'])
    session.add(subscription)
    print("Added `%s'" % subscription)
    session.commit()
    session.close()
  else:
    print("User `%s' is already subscribed for lunch at %s" %
        (user.name_and_email(), lunch.date))

def list_entries(args):
  """List all existing entries in the system, matching a range"""

  session = connect(args['--dbfile'])

  date_range = args['<range>']

  lunches = session.query(Lunch).filter(
      Lunch.date >= date_range[0],
      Lunch.date <= date_range[1]
      )
  for l in lunches:
    print("%s, %d subscriber(s)" % (l, len(l.subscriptions)))
    if args['--long']:
      for s in l.subscriptions:
        print(s)
