#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 06:22:14 CEST

import datetime
import nose.tools
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import six

from .menu import add, remove, lunches_in_range, subscribe, unsubscribe, \
    get_current_user, lunch_at_date
from .models import connect, Base, User, Lunch, Subscription

today = datetime.date.today()
fivedaysago = datetime.date.today() - datetime.timedelta(days=5)
twodaysago = datetime.date.today() - datetime.timedelta(days=2)
yesterday = datetime.date.today() - datetime.timedelta(days=1)
tomorrow = datetime.date.today() + datetime.timedelta(days=1)
in3days = datetime.date.today() + datetime.timedelta(days=3)
in7days = datetime.date.today() + datetime.timedelta(days=7)
in10days = datetime.date.today() + datetime.timedelta(days=10)

# some fake menus
menu_french0 = six.u("Gigot d'agneau aux petits légumes")
menu_english0 = six.u('Lamb with vegetables')
menu_french1 = six.u('Magret de Canard et pâtes')
menu_english1 = six.u('Duck breast with pasta')
menu_french2 = six.u('Trio de pâtes au poivrons')
menu_english2 = six.u('Pasta with capsicum')
menu_french3 = six.u('Risotto aux champignons')
menu_english3 = six.u('Risotto with mushrooms')

# session fixture for tests
session = None

def test_init():

  import os
  import tempfile

  tmpfile = tempfile.NamedTemporaryFile()
  dbfile = tmpfile.name
  assert os.path.exists(dbfile)
  nose.tools.eq_(os.stat(dbfile).st_size, 0)
  session = connect(dbfile)
  nose.tools.assert_not_equal(os.stat(dbfile).st_size, 0)
  assert os.path.exists(dbfile)
  nose.tools.assert_not_equal(os.stat(dbfile).st_size, 0)

def setup_database():

  global session
  session = connect(None)

def teardown_database():
  global session
  session.close()
  session = None
  global engine
  engine = None

@nose.tools.with_setup(setup_database, teardown_database)
def test_add():

  lunch1 = add(session, tomorrow, menu_french1, menu_english1)
  assert lunch1 is not None
  assert lunch1.date == tomorrow
  assert lunch1.menu_french == menu_french1
  assert lunch1.menu_english == menu_english1
  assert repr(lunch1)

  lunch2 = add(session, in3days, menu_french2, menu_english2)
  assert lunch2.date == in3days
  assert lunch2 is not None
  assert lunch2.menu_french == menu_french2
  assert lunch2.menu_english == menu_english2
  assert repr(lunch2)

  lunch3 = add(session, in7days, menu_french3, menu_english3)
  assert lunch3 is not None
  assert lunch3.date == in7days
  assert lunch3.menu_french == menu_french3
  assert lunch3.menu_english == menu_english3
  assert repr(lunch3)

def setup_lunches():

  setup_database()

  lunch0 = add(session, yesterday, menu_french0, menu_english0)

  lunch1 = add(session, tomorrow, menu_french1, menu_english1)

  lunch2 = add(session, in3days, menu_french2, menu_english2)

  lunch3 = add(session, in7days, menu_french3, menu_english3)

@nose.tools.with_setup(setup_lunches)
def test_subscribe():

  sub = subscribe(session, 'next', 1) #notice: the lunch is actually tomorrow
  assert isinstance(sub, Subscription)

  lunch1 = lunch_at_date(session, tomorrow)
  assert lunch1 is not None
  nose.tools.eq_(sub.lunch, lunch1)
  nose.tools.eq_(sub.user, get_current_user(session))
  nose.tools.eq_(sub.persons, 1)

  # subscribing again does not introduce a new entry
  sub2 = subscribe(session, tomorrow, 1) #notice: should work the same
  assert isinstance(sub, Subscription)
  nose.tools.eq_(sub, sub2)

  # can subscribe in the far future
  sub = subscribe(session, in7days, 1)
  assert isinstance(sub, Subscription)
  lunch3 = lunch_at_date(session, in7days)
  assert lunch3 is not None
  nose.tools.eq_(sub.lunch, lunch3)
  nose.tools.eq_(sub.user, get_current_user(session))
  nose.tools.eq_(sub.persons, 1)

  # can subscribe more than one
  sub = subscribe(session, in3days, 5)
  assert isinstance(sub, Subscription)
  lunch2 = lunch_at_date(session, in3days)
  assert lunch2 is not None
  nose.tools.eq_(sub.lunch, lunch2)
  nose.tools.eq_(sub.user, get_current_user(session))
  nose.tools.eq_(sub.persons, 5)

  sub = subscribe(session, in10days, 1) #should fail
  assert sub is None

def setup_lunches_and_subs():

  setup_lunches()

  subscribe(session, tomorrow, 1)
  subscribe(session, in3days, 5)

@nose.tools.with_setup(setup_lunches_and_subs)
def test_unsubscribe():

  lunch = lunch_at_date(session, tomorrow)
  nose.tools.eq_(len(lunch.subscriptions), 1)
  sub = unsubscribe(session, tomorrow) #unsubscribe from the next lunch
  nose.tools.eq_(len(lunch.subscriptions), 0)
  sub = unsubscribe(session, yesterday) #cannot unsubscribe from past lunches
  assert sub is None

@nose.tools.with_setup(setup_lunches_and_subs)
def test_list():

  lunches = lunches_in_range(session, today, datetime.date.max)
  nose.tools.eq_(lunches.count(), 3)
  nose.tools.eq_(lunches[0].total_subscribers(), 1)
  nose.tools.eq_(lunches[1].total_subscribers(), 5)
  nose.tools.eq_(lunches[2].total_subscribers(), 0)

  lunches = lunches_in_range(session, fivedaysago, twodaysago)
  nose.tools.eq_(lunches.count(), 0)

@nose.tools.with_setup(setup_lunches_and_subs)
def test_remove():

  lunch = remove(session, in7days)
  assert isinstance(lunch, Lunch)
  lunches = lunches_in_range(session, today, datetime.date.max)
  nose.tools.eq_(lunches.count(), 2)

  lunch = remove(session, tomorrow, force=True)
  assert isinstance(lunch, Lunch)
  nose.tools.eq_(lunches.count(), 1)

  lunch = remove(session, in3days, force=False) #should fail
  assert lunch is None
  nose.tools.eq_(lunches.count(), 1)
