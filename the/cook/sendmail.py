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
from .menu import get_current_user, lunch_at_date, next_lunch

SIGNATURE = [
    "",
    "--",
    "This e-mail was autogenerated by `the.cook'",
    "For issues, questions and other, please consult:",
    "http://github.com/anjos/the.cook",
    ]

SIGNATURE_FRENCH = [
    "",
    "--",
    "Ce couriel a eté auto-généré par le logiciel `the.cook'",
    "Pour des questions, bugs ou d'autre, SVP consulter:",
    "http://github.com/anjos/the.cook",
    ]

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

  msg = MIMEText('\n'.join(contents), 'plain', 'utf-8')

  msg['From'] = as_str(author.name_and_email())
  if to: msg['To']   = ', '.join(to)
  msg['Subject'] = as_str(subject)
  if cc: msg['Cc'] = ', '.join(cc)

  recipients = []
  if to: recipients += to
  if cc: recipients += cc

  if to:
    s = smtplib.SMTP_SSL('smtp.idiap.ch', 465)
    s.sendmail(author.name_and_email(), recipients, msg.as_string())
    s.quit()

  else:
    #emulate
    print(msg)
    print('\n'.join(contents))

  logging.info('E-mail sent for %d recipients' % len(recipients))

def call(session, address, date=None, cc=None):
  "Sends a reminder for lunch subscription, with the menu"

  tomorrow = datetime.date.today() + datetime.timedelta(days=1)
  if date is None: date = tomorrow #try it for tomorrow then

  lunch = lunch_at_date(session, date)

  if lunch is None:
    logging.error("There is no lunch planned for %s" % format_date(date))
    return False

  user = get_current_user(session)
  path = os.path.realpath(os.path.dirname(sys.argv[0]))
  home = os.path.realpath(os.path.expanduser('~'))
  path = as_str(path.replace(home, '/idiap/home/' + user.name))

  if lunch.date == (datetime.date.today() + datetime.timedelta(days=1)):
    relative_date = 'TODAY'
  else:
    relative_date = format_date(lunch.date - datetime.timedelta(days=1))

  message = [
      "Hello, next %s, the Vatel Restaurant will organise" % \
          format_date(lunch.date),
      "lunch for all Idiapers that subscribed by %s, 18h00." % relative_date,
      "",
      "The menu is:",
      "",
      "Français: %s" % as_str(lunch.menu_french),
      "English: %s" % as_str(lunch.menu_english),
      "",
      "To subscribe to this lunch, execute the following command on a Linux",
      "workstation at Idiap:",
      "",
      "%s/lunch add %s" % (path, lunch.date.strftime('%d.%m.%y')),
      "",
      "Do this **before 18h00 of %s** to be counted in!" % relative_date,
      "",
      "People that subscribe will be reminded of their subscription",
      "on the day of the lunch at ~11h30.",
      "",
      "For more options (including unsubscription), use:",
      "",
      "%s/lunch --help" % path,
      "",
      "**Payment**: Payment for your lunch should be done during the day",
      "of the lunch. Vatel asks people to **avoid** paying during peak"
      "restaurant working hours (i.e., between 12h00 and 13h30). The price",
      "each lunch is CHF 10.-.",
      "",
      "Where: Downstairs, at the Idiap kitchen by default. You should procure",
      "your own cutlery (a fork and a knife) and beverage and bring that with",
      "you. If you are the first to arrive and the meal is not set on the hot",
      "plates, please go the Vatel Restaurant reception and ask them to serve",
      "the meal. All others thank you in advance.",
      "",
      "Time: The semi-official lunch time is 12h30",
      "",
      "Yours faithfully, The Cook.",
      ]

  message += SIGNATURE

  subject = "[food] [%s] %s" % (format_date(lunch.date), lunch.menu_french)

  sendmail(user, address, subject, message, cc)

def in_french(func):
  """Decorator that sets the french locale so dates are printed right"""

  def inner(*args, **kwargs):
    import locale
    current_locale = locale.setlocale(locale.LC_TIME, '')
    try:
      locale.setlocale(locale.LC_TIME, "fr_FR.UTF-8") # french from France
      func(*args, **kwargs)
      locale.setlocale(locale.LC_TIME, current_locale) # reset
    except locale.Error as ex:
      pass

  return inner

@in_french
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
      "Comme convenu, vous trouverez ci-jointe, la liste de personnes",
      "inscrites pour le Repas/Idiap du `%s'" % format_date(lunch.date),
      "",
      "Menu proposé:",
      "",
      "\"%s\"" % as_str(lunch.menu_french),
      "",
      "Personnes inscrites pour ce repas:",
      "",
      ]

  for s in lunch.subscriptions:
    message.append(
        six.u("  - %s (%s) <%s>: %d personne(s) [CHF %d.-]") % \
        (s.user.fullname(), s.user.phone(), s.user.email(), s.persons,
          10*s.persons))
    message[-1] = as_str(message[-1])
    message[-1] += " Payé [ ]"

  message += [
      "",
      "Total: %d personne(s)" % lunch.total_subscribers(),
      "",
      "Merci de nous confirmer la bonne récéption de ce couriel,",
      "",
      "Cordialement, The Idiap Lunch Team.",
      ]

  message += SIGNATURE_FRENCH

  subject = "[Idiap] [food] Inscription consolidé pour le repas du %s" % format_date(lunch.date)

  sendmail(user, address, subject, message, cc)

def remind(session, dry_run, force, cc=None):
  "Sends a call for subscribes of the day lunch"

  lunch = next_lunch(session)
  user = get_current_user(session)
  path = os.path.dirname(sys.argv[0])

  if lunch.date != datetime.date.today() and not force:
    print("There is no lunch scheduled for today, %s" %
        format_date(datetime.date.today()))
    return

  message = [
      "Hello,",
      "",
      "This is a reminder that you have subscribed for the Idiap lunch today:",
      "",
      "Français: %s" % as_str(lunch.menu_french),
      "English: %s" % as_str(lunch.menu_english),
      "",
      "There are %d subscribed person(s):" % lunch.total_subscribers(),
      ""
      ]

  for s in lunch.subscriptions:
    message.append(as_str("  - %s: %d person(s)" % \
        (s.user.name_and_email(), s.persons)))

  message += [
      "",
      "**Payment**: Payment for your lunch should be done during the day",
      "of the lunch. Vatel asks people to **avoid** paying during peak"
      "restaurant working hours (i.e., between 12h00 and 13h30). The price",
      "each lunch is CHF 10.-.",
      "",
      "Note: If you subscribed for more people than just yourself, you are",
      "responsible for paying the total at the Vatel Restaurant for all the",
      "people you vouched for. When you pay, demand and keep a receipt of",
      "your payment. That is your sole proof of payment.",
      "",
      "Where: Downstairs, at the Idiap kitchen by default. You should procure",
      "your own cutlery (a fork and a knife) and beverage and bring that with",
      "you. If you are the first to arrive and the meal is not set on the hot",
      "plates, please go the Vatel Restaurant reception and ask them to serve",
      "the meal. All others thank you in advance.",
      "",
      "Time: The semi-official lunch time is 12h30",
      "",
      "Yours faithfully, The Cook.",
      ]

  message += SIGNATURE

  subject = "[food] [reminder] [%s] %s" % (format_date(lunch.date), as_str(lunch.menu_french))

  if dry_run:
    address = None

  else:
    address = [as_str(k.user.name_and_email()) for k in lunch.subscriptions]

  sendmail(user, address, subject, message, cc)
