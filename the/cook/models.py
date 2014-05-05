#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 09:40:45 CEST

"""Models for database handling"""

import os
import logging
import subprocess
import datetime
import six

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker

Base = declarative_base()

def backquote(cmd):
  """Runs `cmd` and returns the answer"""

  return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

def format_date(date):
  """Standard date formatting"""
  return date.strftime("%A, %d/%m/%Y")

def format_datetime(date):
  """Standard date formatting"""
  return date.strftime("%A, %d/%m/%Y at %H:%M")

class User(Base):
  """A class that represents a unique user at Idiap"""

  __tablename__ = 'user'

  id = Column(Integer, primary_key=True)
  name = Column(String(16), unique=True)

  def __init__(self, id, name):
    """Constructor, simple"""

    self.id = int(backquote(['id', '-u', name]))
    self.name = name

  def phone(self):

    try:
      tel = '/idiap/resource/software/scripts/tel'
      data = backquote([tel, self.name]).split('\n')[1]
    except OSError as e:
      logging.error(e)
      return '+41277217XXX'
    return '+41277217' + data.split()[-1].strip()

  def email(self):

    return self.name + '@idiap.ch'

  def fullname(self):

    try:
      data = backquote(['getent', 'passwd', self.name]).split(':')[4]
    except OSError as e:
      logging.error(e)
      return six.u('Joe Doe')
    return as_unicode(data)

  def name_and_email(self):

    return '%s <%s>' % (self.fullname(), self.email())

  def __repr__(self):

    return 'User("%s", %d)' % (self.name, self.id)

def as_unicode(s):
  if not six.PY3 and isinstance(s, str): return s.decode('utf-8')
  return s

def as_str(s):
  if not six.PY3 and not isinstance(s, str): return s.encode('utf-8')
  return s

class Lunch(Base):
  """A particular lunch with a menu and subscribers"""

  __tablename__ = 'lunch'

  id = Column(Integer, primary_key=True)

  date = Column(Date, unique=True)

  menu_french = Column(String(128))

  menu_english = Column(String(128))

  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User, backref=backref('lunches', order_by=id))

  def __init__(self, date, menu_french, menu_english, user):

    self.date = date
    self.menu_french = as_unicode(menu_french)
    self.menu_english = as_unicode(menu_english)
    self.user = user
    self.user_id = user.id

  def __repr__(self):

    return as_str('Lunch(%s, "%s", %s)' % (format_date(self.date), self.menu_french, self.user))

  def total_subscribers(self):
    """Returns the total number of subscribers to a lunch"""

    return sum([k.persons for k in self.subscriptions])

class Subscription(Base):
  """A subscription to a particular lunch"""

  __tablename__ = 'subscription'

  id = Column(Integer, primary_key=True)

  persons = Column(Integer)

  date = Column(DateTime)

  lunch_id = Column(Integer, ForeignKey('lunch.id'))
  lunch = relationship(Lunch, backref=backref('subscriptions', order_by=id))

  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User, backref=backref('subscriptions', order_by=id))

  def __init__(self, lunch, user, persons, date=datetime.datetime.now()):

    self.lunch_id = lunch.id
    self.lunch = lunch
    self.user_id = user.id
    self.user = user
    self.persons = persons
    self.date = date

  def __repr__(self):

    ulunch = as_unicode(repr(self.lunch))
    return as_str('Subscription(%s, %s, %d, %s)' % \
        (ulunch, self.user, self.persons, self.date))

def create(dbfile, recreate=False):
  """Creates or re-creates this database"""

  if dbfile and recreate and os.path.exists(dbfile):
    logging.info("Erasing old database at `%s'..." % dbfile)
    os.unlink(dbfile)

  if dbfile: engine = create_engine('sqlite:///' + dbfile)
  else: engine = create_engine('sqlite://', echo=False) #in-memory
  Base.metadata.create_all(engine)

  return engine

def connect(dbfile):
  """Creates a new connection to the database and return it"""

  engine = create(dbfile)
  Session = sessionmaker()
  Session.configure(bind=engine)
  return Session()
