#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 04:53:34 CEST

"""Manage Idiap Lunch properties, send e-mails, reminders

Usage:
  %(prog)s [--dbfile=<s>] [-v ...] init [--recreate]
  %(prog)s [--dbfile=<s>] [-v ...] add <date> <menu>
  %(prog)s [--dbfile=<s>] [-v ...] remove [--force] <date>
  %(prog)s [--dbfile=<s>] [-v ...] list [--long] [<range>]
  %(prog)s [--dbfile=<s>] [-v ...] subscribe [<date>] [--persons=<n>]
  %(prog)s [--dbfile=<s>] [-v ...] call [--force] [<email>]
  %(prog)s [--dbfile=<s>] [-v ...] report [--force] [<email>]
  %(prog)s [--dbfile=<s>] [-v ...] reminder [--dry-run]
  %(prog)s (-h | --help)
  %(prog)s (-V | --version)


Arguments:
  <date>   The date a certain menu is concerned with. Dates must have the
           format dd.mm.yy
  <range>  A date range for listing menu entries and subscribers. The range
           should be formatted like <start-date>..<end-date>. <start-date> may
           be suppressed, in which case you mean from today. If <end-date> is
           not provided, it means all entries from the <start-date>.
  <menu>   The menu to be added to a certain date. Wrap the menu in quotes. You
           may use accents if required. For example: "menu en français (english
           translation)"
  <email>  The e-mail where to send reports or reminders. Two formats are
           allowed "user@example.com" or "User <user@example.com>". If an
           e-mail is not passed on commands that require such, then output is
           just printed to the screen.


Options:
  -h --help         Shows this screen.
  -V --version      Shows version.
  -l --long         When listing, use the "long" mode and get more information
                    displayed instead of a summarized output
  --recreate        When initializing, use this flag to remove an old database
                    and create a brand new one in place
  -d --dbfile=<s>   Use a different database file then the default, package
                    bound file. This is useful for testing purposes.
  -p --persons=<n>  If you'd like to subscribe (and vouche) for more than one
                    person, specify on this field how many. You will be
                    responsible for paying for those persons at the Vatel
                    Restaurant as only your name will figure on the final list
                    [default: 1].
  -n --dry-run      In reminder mode, instead of sending the messages, just
                    simulates what it would send.
  -f --force        Force the action, even if it has nasty consequences
  -v --verbose      Increases the verbosity level for this application.


Commands:
  init      Initializes the current repository for menus and subscribers
  add       Adds a new menu for a specific date
  remove    Removes the menu entry for that date
  list      Lists past and future menus, with subscribers
  subscribe Allows for the user to subscribe to the next lunches
  call      Calls idiapers for lunch subscription, with the menu
  report    Sends a PDF report to the Vatel Restaurant
  remind    Sends a reminder for subscribes of the day lunch


Examples:

  To add a new menu:

    $ %(prog)s add 28.04.14 "Risotto au champignon (Mushroom risotto)"

  To remove a menu:

    $ %(prog)s remove 28.04.14

  For help, type:

    $ %(prog)s --help

  For the program version, type:

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

from ..schema import validate_date, validate_email, validate_range, validate_menu

def main(argv=None):

  prog = sys.argv[0]
  arguments = docopt.docopt(
      __doc__ % {'prog': prog},
      argv=argv,
      version=__version__
      )

  # validate arguments
  s = schema.Schema({
    'init': object, #ignore
    'add': object, #ignore
    'remove': object, #ignore
    'list': object, #ignore
    'subscribe': object, #ignore
    'reminder': object, #ignore
    'report': object, #ignore
    'call': object, #ignore
    '<date>': schema.Use(validate_date),
    '<range>': schema.Use(validate_range),
    '<menu>': schema.Or(None, schema.Use(validate_menu)),
    '<email>': schema.Or(None, schema.Use(validate_email)),
    '--help'    : object, #ignore
    '--version' : object, #ignore
    '--long' : object, #ignore
    '--recreate': object, #ignore
    '--dbfile': object, #ignore
    '--persons': schema.And(schema.Use(int), lambda n: n > 0),
    '--dry-run': object, #ignore
    '--force': object, #ignore
    '--verbose': object, #ignore
    })

  if arguments['--verbose'] == 1: logging.getLogger().setLevel(logging.INFO)
  if arguments['--verbose'] >  1: logging.getLogger().setLevel(logging.DEBUG)

  arguments = s.validate(arguments)

  if arguments['--dbfile'] is None:
    arguments['--dbfile'] = __import__('pkg_resources').resource_filename(
        __name__,
        'thecook.sql3'
        )

  from ..models import create, connect
  from ..menu import add, remove, list_entries, subscribe
  from ..sendmail import remind, report, call

  if arguments['init']:
    create(arguments['--dbfile'], arguments['--recreate'])
  elif arguments['add']:
    session = connect(arguments['--dbfile'])
    add(session, arguments['<date>'],
        arguments['<menu>'][0], arguments['<menu>'][1])
  elif arguments['remove']:
    session = connect(arguments['--dbfile'])
    remove(session, arguments['<date>'], arguments['--force'])
  elif arguments['list']:
    session = connect(arguments['--dbfile'])
    to_print = list_entries(session,
        arguments['<range>'][0], arguments['<range>'][1], arguments['--long'])
    for k in to_print: print(k)
  elif arguments['subscribe']:
    session = connect(arguments['--dbfile'])
    subscribe(session, arguments['<date>'], arguments['--persons'])
  elif arguments['call']:
    session = connect(arguments['--dbfile'])
    call(session, [arguments['<email>']], arguments['--force'])
  elif arguments['report']:
    session = connect(arguments['--dbfile'])
    report(session, [arguments['<email>']], arguments['--force'])
  elif arguments['remind']:
    session = connect(arguments['--dbfile'])
    remind(session, arguments['--dry-run'], arguments['--force'])
  else:
    raise NotImplementedError("unknown command")

  return 0
