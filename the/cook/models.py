#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 09:40:45 CEST

"""Models for database handling"""

import os
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, ForeignKey, Date, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref, sessionmaker
import subprocess
import datetime

Base = declarative_base()

def backquote(cmd):
  """Runs `cmd` and returns the answer"""

  return subprocess.Popen(cmd, stdout=subprocess.PIPE).communicate()[0]

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
      data = backquote(['tel', self.name]).split('\n')[1]
    except OSError as e:
      print(e)
      return '+41277217XXX'
    name, tel = data.rsplit(' ', 1)
    return '+41277217' + tel.strip()

  def email(self):

    return self.name + '@idiap.ch'

  def fullname(self):

    try:
      data = backquote(['tel', self.name]).split('\n')[1]
    except OSError as e:
      print(e)
      return 'Joe Doe'
    name, tel = data.rsplit(' ', 1)
    return name.strip()

  def name_and_email(self):

    return '%s <%s>' % (self.fullname(), self.email())

  def __repr__(self):

    return 'User("%s", %d)' % (self.name, self.id)

class Lunch(Base):
  """A particular lunch with a menu and subscribers"""

  __tablename__ = 'lunch'

  id = Column(Integer, primary_key=True)

  date = Column(Date)

  menu_french = Column(String(128), unique=True)

  menu_english = Column(String(128), unique=True)

  user_id = Column(Integer, ForeignKey('user.id'))
  user = relationship(User, backref=backref('lunches', order_by=id))

  def __init__(self, date, menu, user):

    self.date = date
    self.menu_french = menu[0].decode('utf-8')
    self.menu_english = menu[1].decode('utf-8')
    self.user = user
    self.user_id = user.id

  def __repr__(self):

    retval = 'Lunch(%s, "%s", %s)' % (self.date, self.menu_french, self.user)
    return retval.encode('utf-8')

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

  def __init__(self, lunch, user, persons):

    self.lunch_id = lunch.id
    self.lunch = lunch
    self.user_id = user.id
    self.user = user
    self.persons = persons
    self.date = datetime.datetime.now()

  def __repr__(self):
    retval = u"Subscription(%s, %s, %d)" % (str(self.lunch).decode('utf-8'),
        self.user, self.persons)
    return retval.encode('utf-8')

def create(args):
  """Creates or re-creates this database"""

  dbfile = args['--dbfile']
  if args['--recreate'] and os.path.exists(dbfile):
    print("Erasing old database at `%s'..." % dbfile)
    os.unlink(dbfile)

  engine = create_engine('sqlite:///' + dbfile)

  User.metadata.create_all(engine)
  Lunch.metadata.create_all(engine)
  Subscription.metadata.create_all(engine)

def connect(dbfile):
  """Creates a new connection to the database and return it"""

  Session = sessionmaker()
  engine = create_engine('sqlite:///' + dbfile)
  Session.configure(bind=engine)
  return Session()
