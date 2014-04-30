#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to send e-mails"""

import os
import sys
import datetime
from .models import User, Lunch, Subscription, connect
from .menu import get_current_user

def reminder(args):
  "Sends a reminder for lunch subscription, with the menu"

  session = connect(args['--dbfile'])
  next_lunch = session.query(Lunch).filter(Lunch.date >= datetime.date.today()).first()
  user = get_current_user(session, args)
  path = os.path.dirname(sys.argv[0])
  session.close()

  # TODO: If next_lunch not tomorrow, abort

  message = [
      "Hello, next %s, the Vatel Restaurant will organise" % next_lunch.date.strftime("%A, %d/%m/%y"),
      "lunch for all Idiapers that subscribed by today 18h00. The menu is:",
      "",
      "Français: %s" % next_lunch.menu_french.encode('utf-8'),
      "English: %s" % next_lunch.menu_english.encode('utf-8'),
      "",
      "To subscribe to this lunch, execute the following command on a Linux",
      "workstation at Idiap:",
      "",
      "%s/lunch subscribe" % path,
      "",
      "Do this **before 18h00 of today** to be counted in! People that subscribe",
      "will be reminded of their subscription on the day of the lunch at ~11h30.",
      "",
      "For more options (including checking subscriptions), use:",
      "",
      "%s/lunch --help" % path,
      "",
      "**Payment**: Payment for your lunch should be done before you eat",
      "your lunch. The Vatel Restaurant accepts that you pay just before",
      "eating, so you can pay when you go down for the lunch.",
      "",
      "Yours faithfully, The Cook.",
      ]

  if args['<email>'] is None:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: Miscellaneous Varied Varieties <misc@idiap.ch>")
    print("Subject: [food] [%s] %s" % (next_lunch.date.strftime("%a, %d/%m/%y"), next_lunch.menu_french.encode('utf-8')))
    print("")
    for l in message: print(l)

  else:
    raise NotImplementedError("This bot cannot yet send messages")

def report(args):
  "Sends a PDF report to the Vatel Restaurant"

  session = connect(args['--dbfile'])
  next_lunch = session.query(Lunch).filter(Lunch.date >= datetime.date.today()).first()
  user = get_current_user(session, args)
  path = os.path.dirname(sys.argv[0])

  # TODO: If next_lunch not tomorrow, abort

  message = [
      "Menu proposé pour %s:" % next_lunch.date.strftime("%A, %d/%m/%Y"),
      "",
      "\"%s\"" % next_lunch.menu_french.encode('utf-8'),
      "",
      "Idiapers inscrits pour ce repas:",
      "",
      ]

  total = 0
  for s in next_lunch.subscriptions:
    total += s.persons
    message.append("%s (%s) <%s>: %d" % \
        (s.user.fullname(), s.user.phone(), s.user.email(), s.persons))

  message += [
      "",
      "Total: %d personne(s)" % s.persons,
      "",
      "Merci de nous confirmer la bonne récéption de ce couriel,"
      "",
      "%s <%s>" % (user.fullname(), user.email()),
      ]

  if args['<email>'] is None:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: Réception - Hotel Vatel <info@hotelvatel.ch>")
    print("Subject: Inscription pour le repas du %s" % (next_lunch.date.strftime('%A, %d/%m/%Y'),))
    print("")
    for l in message: print(l)

  else:
    raise NotImplementedError("This bot cannot yet send messages")

  session.close()

def call(args):
  "Sends a call for subscribes of the day lunch"

  session = connect(args['--dbfile'])
  next_lunch = session.query(Lunch).filter(Lunch.date >= datetime.date.today()).first()
  user = get_current_user(session, args)
  path = os.path.dirname(sys.argv[0])

  # TODO: If next_lunch not today, abort
  if (next_lunch.date != datetime.date.today()):
    print("There is no lunch scheduled for today, %s",
        datetime.date.today().strftime("%A, %d/%m/%Y"))
    return

  message = [
      "Hello,",
      ""
      "This is a reminder that you have subscribed for the Idiap lunch today:",
      "",
      "Français: %s" % next_lunch.menu_french.encode('utf-8'),
      "English: %s" % next_lunch.menu_english.encode('utf-8'),
      "",
      "There are %d people subscribed in total" % len(next_lunch.subscriptions),
      "",
      "**Payment**: Payment for your lunch should be done before you eat",
      "your lunch. The Vatel Restaurant accepts that you pay just before",
      "eating, so you can pay when you go down for the lunch.",
      "",
      "Where: Downstairs, at the Idiap kitchen by default. You should procure",
      "your own cutlery (a fork and a knife) and beverage and bring that with",
      "you. If you are the first to arrive and the meal is not set on the hot",
      "plates, please go the Vatel Restaurant reception and ask them to serve",
      "the meal. All others thank you in advance.",
      "",
      "Yours faithfully, The Cook.",
      ]

  print args
  if args['--dry-run']:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: %d users <...@idiap.ch>" % len(next_lunch.subscriptions))
    print("Subject: [food] [reminder] [%s] %s" % (next_lunch.date.strftime("%a, %d/%m/%y"), next_lunch.menu_french.encode('utf-8')))
    print("")
    for l in message: print(l)

  else:
    raise NotImplementedError("This bot cannot yet send messages")

  session.close()
