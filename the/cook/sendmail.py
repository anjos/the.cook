#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to send e-mails"""

import os
import sys
import datetime
import logging
from .models import User, Lunch, Subscription, connect, format_date
from .menu import get_current_user, next_lunch

def reminder(session, email):
  "Sends a reminder for lunch subscription, with the menu"

  lunch = next_lunch(session)

  if lunch is None:
    logging.error("There are no further lunches planned as of today, %s" % format_date(datetime.datetime.now()))
    return False

  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])
  session.close()

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  if (lunch.date != tomorrow):
    logging.error("There is no lunch scheduled for tomorrow, as of today, %s" % format_date(tomorrow))
    return False

  message = [
      "Hello, next %s, the Vatel Restaurant will organise" % format_date(lunch.date),
      "lunch for all Idiapers that subscribed by today 18h00. The menu is:",
      "",
      "Français: %s" % lunch.menu_french.encode('utf-8'),
      "English: %s" % lunch.menu_english.encode('utf-8'),
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

  if email is None:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: Miscellaneous Varied Varieties <misc@idiap.ch>")
    print("Subject: [food] [%s] %s" % (format_date(lunch.date), lunch.menu_french.encode('utf-8')))
    print("")
    for l in message: print(l)

  else:
    raise NotImplementedError("This bot cannot yet send messages")

def report(session, email):
  "Sends a PDF report to the Vatel Restaurant"

  lunch = next_lunch(session)
  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  if (lunch.date != tomorrow):
    print("There is no lunch scheduled for tomorrow, %s" % format_date(tomorrow))
    return

  message = [
      "Menu proposé pour %s:" % format_date(lunch.date),
      "",
      "\"%s\"" % lunch.menu_french.encode('utf-8'),
      "",
      "Idiapers inscrits pour ce repas:",
      "",
      ]

  for s in lunch.subscriptions:
    message.append("%s (%s) <%s>: %d (CHF %d.-)" % \
        (s.user.fullname(), s.user.phone(), s.user.email(), s.persons,
          10*s.persons))

  message += [
      "",
      "Total: %d personne(s)" % lunch.total_subscribers(),
      "",
      "Merci de nous confirmer la bonne récéption de ce couriel,"
      "",
      "%s <%s>" % (user.fullname(), user.email()),
      ]

  if email is None:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: Réception - Hotel Vatel <info@hotelvatel.ch>")
    print("Subject: Inscription pour le repas du %s" % format_date(lunch.date))
    print("")
    for l in message: print(l)

  else:
    raise NotImplementedError("This bot cannot yet send messages")

  session.close()

def call(session, dry_run):
  "Sends a call for subscribes of the day lunch"

  lunch = next_lunch(session)
  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])

  if (lunch.date != datetime.date.today()):
    print("There is no lunch scheduled for today, %s" %
        format_date(datetime.date.today()))
    return

  message = [
      "Hello,",
      ""
      "This is a reminder that you have subscribed for the Idiap lunch today:",
      "",
      "Français: %s" % lunch.menu_french.encode('utf-8'),
      "English: %s" % lunch.menu_english.encode('utf-8'),
      "",
      "There are %d people subscribed in total" % len(lunch.subscriptions),
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

  if dry_run:
    print("From: %s <%s>" % (user.fullname(), user.email()))
    print("To: %d users <...@idiap.ch>" % len(lunch.subscriptions))
    print("Subject: [food] [reminder] [%s] %s" % (format_date(lunch.date), lunch.menu_french.encode('utf-8')))
    print("")
    for l in message: print(l)

  else:
    # TODO: Tell the person the number of subscribes and the total to pay
    raise NotImplementedError("This bot cannot yet send messages")

  session.close()
