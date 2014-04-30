#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.anjos@idiap.ch>
# Wed 30 Apr 2014 06:22:14 CEST

from .scripts.manage import main
import tempfile

dbfile = tempfile.NamedTemporaryFile()

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
      '30',
      'Magret de Canard et pâtes (Duck breast with pasta)',
      )
  assert main(cmdline) == 0

def test_subscribe():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      '30',
      )
  assert main(cmdline) == 0

def test_subscribe_again():

  cmdline = (
      '--dbfile=%s' % dbfile.name,
      'subscribe',
      '30',
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
      '30',
      )
  assert main(cmdline) == 0
