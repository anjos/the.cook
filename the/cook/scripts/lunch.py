#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 04:53:34 CEST

"""Subscribe, unsubscribe and list menu options

Usage:
  %(prog)s add [<date>] [--persons=<n>]
  %(prog)s remove [<date>]
  %(prog)s mine
  %(prog)s list
  %(prog)s (-h | --help)
  %(prog)s (-V | --version)


Arguments:
  <date>      The date a certain menu is concerned with. Dates must have the
              format 'dd.mm.yy'. If the date is not specified, it is assumed to
              refer to the next viable subscribeable lunch. You can use
              keywords like 'next' to refer to the next possible lunch, 'today'
              to refer to today and 'tomorrow', to refer to the day after
              today. Weekdays can also be passed either in long ('tuesday') or
              short formats ('tue').


Options:
  -h --help         Shows this screen.
  -V --version      Shows version.
  -l --long         When listing, use the "long" mode and get more information
                    displayed instead of a summarized output
  -p --persons=<n>  If you'd like to subscribe (and vouche) for more than one
                    person, specify on this field how many. You will be
                    responsible for paying for those persons at the Vatel
                    Restaurant as only your name will figure on the final list
                    [default: 1].


Commands:
  add     Subscribes the user to one of the next lunches
  remove  Unsubscribes the user from one of the next lunches
  mine    Shows your own subscriptions for next lunches
  list    Shows next lunches and who is subscribed


Examples:

  To to subscribe yourself for the next possible lunch:

    $ %(prog)s add

  To unsubscribe (specify a specific lunch date):

    $ %(prog)s remove 28.04.14

  To see next lunches and who is subscribed:

    $ %(prog)s list

  To see which lunches you're subscribed to next:

    $ %(prog)s mine

  To change a subscription (i.e. add more people), first unsubscribe and then
  re-subscribe with the correct number of parties you wish to vouch for:

    $ %(prog)s remove tuesday
    $ %(prog)s add tuesday --persons=2

  For help and other command options type:

    $ %(prog)s --help

  For the program version type:

    $ %(prog)s --version
"""

import logging
from .. import __logging_format__, __version__
logging.basicConfig(format=__logging_format__)

import os
import sys
import docopt
import schema
import datetime

from ..schema import validate_date

def main(argv=None):

  prog = sys.argv[0]
  arguments = docopt.docopt(
      __doc__ % {'prog': prog},
      argv=argv,
      version=__version__
      )

  # validate arguments
  s = schema.Schema({
    'add': object, #ignore
    'remove': object, #ignore
    'list': object, #ignore
    'mine': object, #ignore
    '<date>': schema.Use(validate_date),
    '--help'    : object, #ignore
    '--version' : object, #ignore
    '--persons': schema.And(schema.Use(int), lambda n: n > 0),
    })

  arguments = s.validate(arguments)

  from pkg_resources import resource_filename
  from .. import data
  dbfile = resource_filename(data.__name__, 'thecook.sql3')

  today = datetime.datetime.today()

  from ..models import connect
  from ..menu import lunch_list, user_list, subscribe, unsubscribe, get_current_user, format_date

  if arguments['add']:
    session = connect(dbfile)
    sub = subscribe(session, arguments['<date>'], arguments['--persons'])
    if sub:
      print("User `%s' successfuly subscribed for lunch `%s' at `%s'" % \
          (sub.user.name, sub.lunch.menu_english, format_date(sub.lunch.date)))
  elif arguments['remove']:
    session = connect(dbfile)
    sub = unsubscribe(session, arguments['<date>'])
    if sub:
      print("User `%s' successfuly unsubscribed from lunch `%s' at `%s'" % \
          (sub.user.name, sub.lunch.menu_english, format_date(sub.lunch.date)))
  elif arguments['list']:
    session = connect(dbfile)
    to_print = lunch_list(session, today, datetime.date.max, long_desc=True)
    if not to_print:
      print("No lunches programmed as of this time")
    else:
      for k in to_print: print(k)
  elif arguments['mine']:
    session = connect(dbfile)
    user = get_current_user(session)
    to_print = user_list(session, user.name, today, datetime.date.max, long_desc=True)
    if len(to_print) == 1:
      print("User `%s' is not registered to any upcoming lunches" % user.name)
    else:
      for k in to_print: print(k)
  else:
    raise NotImplementedError("unknown command")

  return 0
