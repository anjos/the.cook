#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 04:53:34 CEST

"""Manage Idiap Lunch properties, send e-mails, reminders

Usage:
  %(prog)s [--dbfile=<s>] init [-r]
  %(prog)s [--dbfile=<s>] add <date> <menu>
  %(prog)s [--dbfile=<s>] remove <date>
  %(prog)s [--dbfile=<s>] list [-s|-l] [<range>]
  %(prog)s [--dbfile=<s>] subscribe [<date>] [--persons=<n>]
  %(prog)s [--dbfile=<s>] reminder [<email>]
  %(prog)s [--dbfile=<s>] report [<email>]
  %(prog)s [--dbfile=<s>] call [--dry-run|-n]
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
  -h --help      Shows this screen.
  -V --version   Shows version.
  -s --short     When listing, prints only dates and # of subscribers
  -l --long      When listing, prints menus and names of subscribers
  -r --recreate  When initializing, use this flag to remove an old database and
                 create a brand new one in place
  --dbfile=<s>   Use a different database file then the default, package bound
                 file. This is useful for testing purposes.
  --persons=<n>  If you'd like to subscribe (and vouche) for more than one
                 person, specify on this field how many. You will be
                 responsible for paying for those persons at the Vatel
                 Restaurant as only your name will figure on the final list
                 [default: 1].
  -n --dry-run   In reminder mode, instead of sending the messages, just
                 simulates what it would send.


Commands:
  init      Initializes the current repository for menus and subscribers
  add       Adds a new menu for a specific date
  remove    Removes the menu entry for that date
  list      Lists past and future menus, with subscribers
  reminder  Sends a reminder for lunch subscription, with the menu
  report    Sends a PDF report to the Vatel Restaurant
  call      Sends a call for subscribes of the day lunch


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
    '<date>': schema.Or(None, schema.Use(validate_date)),
    '<range>': schema.Or(None, schema.Use(validate_range)),
    '<menu>': schema.Or(None, schema.Use(validate_menu)),
    '<email>': schema.Or(None, schema.Use(validate_email)),
    '--help'    : object, #ignore
    '--version' : object, #ignore
    '--short' : object, #ignore
    '--long' : object, #ignore
    '--recreate': object, #ignore
    '--dbfile': object, #ignore
    '--persons': schema.And(schema.Use(int), lambda n: n > 0),
    '--dry-run': object, #ignore
    })

  arguments = s.validate(arguments)

  if arguments['--dbfile'] is None:
    arguments['--dbfile'] = __import__('pkg_resources').resource_filename(
        __name__,
        'thecook.sql3'
        )

  if arguments['<range>'] is None:
    arguments['<range>'] = (datetime.date.min, datetime.date.max)

  if arguments['init']:
    from ..models import create
    create(arguments)
  elif arguments['add']:
    from ..menu import add
    add(arguments)
  elif arguments['remove']:
    from ..menu import remove
    remove(arguments)
  elif arguments['list']:
    from ..menu import list_entries
    list_entries(arguments)
  elif arguments['subscribe']:
    from ..menu import subscribe
    subscribe(arguments)
  elif arguments['reminder']:
    from ..sendmail import reminder
    reminder(arguments)
  elif arguments['report']:
    from ..sendmail import report
    report(arguments)
  elif arguments['call']:
    from ..sendmail import call
    call(arguments)
  else:
    raise NotImplementedError("unknown command - debug me")

  return 0
