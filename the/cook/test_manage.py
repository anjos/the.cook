#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 06:22:14 CEST

from .scripts.manage import main
import tempfile
import datetime

dbfile = tempfile.NamedTemporaryFile()
today = str(datetime.date.today().day)
tomorrow = (datetime.date.today() + datetime.timedelta(days=1)).strftime('%d.%m.%y')
in3days = (datetime.date.today() + datetime.timedelta(days=3)).strftime('%d.%m.%y')

def test_init():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'init',
      )
  assert main(cmdline) == 0

def test_add():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'add',
      tomorrow,
      'Magret de Canard et pâtes (Duck breast with pasta)',
      )
  assert main(cmdline) == 0

def test_subscribe():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      )
  assert main(cmdline) == 0

def test_subscribe_tomorrow():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      tomorrow,
      )
  assert main(cmdline) == 0

def test_subscribe_unexisting():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      '01.01.20',
      )
  assert main(cmdline) == 0

def test_subscribe_past():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      '01.01.70',
      )
  assert main(cmdline) == 0

def test_subscribe_again():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      tomorrow,
      )
  assert main(cmdline) == 0

def test_list_short():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'list',
      '--short',
      )
  assert main(cmdline) == 0

def test_list_long():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'list',
      '--long',
      )
  assert main(cmdline) == 0

def test_reminder():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'reminder',
      )
  assert main(cmdline) == 0

def test_report():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'report',
      )
  assert main(cmdline) == 0

def test_call():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'call',
      '--dry-run',
      )
  assert main(cmdline) == 0

def test_remove():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'remove',
      tomorrow,
      )
  assert main(cmdline) == 0

def test_add_in3days():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'add',
      in3days,
      'Magret de Canard et pâtes (Duck breast with pasta)',
      )
  assert main(cmdline) == 0

def test_reminder_fails():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'reminder',
      )
  assert main(cmdline) == 0

def test_report_in3days():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'report',
      )
  assert main(cmdline) == 0

def test_remove_in3days():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'remove',
      in3days,
      )
  assert main(cmdline) == 0
