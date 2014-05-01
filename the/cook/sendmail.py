#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 07:49:21 CEST

"""Functions to send e-mails"""

import os
import sys
import six
import datetime
import logging
from .models import format_date, as_str, as_unicode
from .menu import get_current_user, next_lunch

def sendmail(author, to, subject, contents, cc=None):
  """Sends an e-mail using the Idiap SMTP server

  author - A 'User' object that corresponds to the author of the message
  to - A list, containing the parties that will receive the message
  subject - The message subject
  contents - The actual contents of the message, as a list w/o newlines
  cc - An optional list of people to carbon-copy the message to
  """

  import smtplib
  from email.mime.text import MIMEText

  import ipdb; ipdb.set_trace()

  msg = MIMEText('\n'.join(contents))

  msg['From'] = as_str(author.name_and_email())
  msg['To']   = ', '.join(to)
  msg['Subject'] = as_str(subject)
  if cc: msg['Cc'] = ', '.join(cc)

  s = smtplib.SMTP_SSL('smtp.idiap.ch', 465)
  recipients = to
  if cc: recipients += cc
  s.sendmail(author.name_and_email(), recipients, msg.as_string())
  s.quit()

def call(session, address, force, cc=None):
  "Sends a reminder for lunch subscription, with the menu"

  lunch = next_lunch(session)

  if lunch is None:
    logging.error("There are no further lunches planned as of today, %s" % format_date(datetime.datetime.now()))
    return False

  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  if (lunch.date != tomorrow) and not force:
    logging.error("There is no lunch scheduled for tomorrow, as of today, %s" % format_date(tomorrow))
    return False

  message = [
      "Hello, next %s, the Vatel Restaurant will organise" % \
          format_date(lunch.date),
      "lunch for all Idiapers that subscribed by today 18h00. The menu is:",
      "",
      "Français: %s" % as_str(lunch.menu_french),
      "English: %s" % as_str(lunch.menu_english),
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

  subject = "[food] [%s] %s" % (format_date(lunch.date), lunch.menu_french)

  if not address:
    print("From: %s" % user.name_and_email())
    print("Subject: %s" % subject)
    if cc: print("Cc: %s" % ", ".join(cc))
    print("")
    for l in message: print(l)

  else:
    sendmail(user, address, subject, message, cc)

def report(session, address, force, cc=None):
  "Sends a PDF report to the Vatel Restaurant"

  lunch = next_lunch(session)
  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  if (lunch.date != tomorrow) and not force:
    print("There is no lunch scheduled for tomorrow, %s" % format_date(tomorrow))
    return

  message = [
      "Bonjour,",
      "",
      "Menu proposé pour %s:" % format_date(lunch.date),
      "",
      "\"%s\"" % as_str(lunch.menu_french),
      "",
      "Idiapers inscrits pour ce repas:",
      "",
      ]

  for s in lunch.subscriptions:
    message.append("  - %s (%s) <%s>: %d personne(s) [CHF %d.-]" % \
        (s.user.fullname(), s.user.phone(), s.user.email(), s.persons,
          10*s.persons))

  message += [
      "",
      "Total: %d personne(s)" % lunch.total_subscribers(),
      "",
      "Merci de nous confirmer la bonne récéption de ce couriel,",
      "",
      "%s" % user.name_and_email(),
      ]

  subject = "Inscription pour le repas du %s" % format_date(lunch.date)

  if not address:
    print("From: %s" % user.name_and_email())
    print("Subject: %s" % subject)
    if cc: print("Cc: %s" % ", ".join(cc))
    print("")
    for l in message: print(l)

  else:
    sendmail(user, address, subject, message, cc)

def remind(session, dry_run, force):
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
      "Français: %s" % as_str(lunch.menu_french),
      "English: %s" % as_str(lunch.menu_english),
      "",
      "There are %d people subscribed in total:" % lunch.total_subscribers(),
      ""
      ]

  for s in lunch.subscriptions:
    message2.append("  - %s: %d person(s)" % \
        (s.user.name_and_email(), s.persons))

  message = [
      "",
      "**Payment**: Payment for your lunch should be done before you eat",
      "your lunch. The Vatel Restaurant accepts that you pay just before",
      "eating, so you can pay when you go down for the lunch.",
      "",
      "Note: If you subscribed for more people than just yourself, you are",
      "responsible for paying the total at the Vatel Restaurant for all the",
      "people you vouched for. When you pay, demand and keep a receipt of",
      "your payment. That is your sole proof of payment.",
      "",
      ]

  message += [
      "",
      "Where: Downstairs, at the Idiap kitchen by default. You should procure",
      "your own cutlery (a fork and a knife) and beverage and bring that with",
      "you. If you are the first to arrive and the meal is not set on the hot",
      "plates, please go the Vatel Restaurant reception and ask them to serve",
      "the meal. All others thank you in advance.",
      ""
      "Time: The semi-official lunch time is 12h30",
      "",
      "Yours faithfully, The Cook.",
      ]

  subject = "[food] [reminder] [%s] %s" % (format_date(lunch.date), as_str(lunch.menu_french))

  if dry_run:
    print("From: %s" % user.name_and_email())
    print("Subject: %s" % subject)
    if cc: print("Cc: %s" % ", ".join(cc))
    print("")
    for l in message: print(l)

  else:
    address = [k.user.name_and_email() for k in lunch.subscriptions]
    sendmail(user, address, subject, message, cc)
