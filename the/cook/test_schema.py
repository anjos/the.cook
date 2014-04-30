#!/usr/bin/env python
# encoding: utf-8
# Andre Anjos <andre.dos.anjos@gmail.com>
# Wed 30 Apr 2014 05:54:29 CEST

import nose.tools
from .schema import validate_email, validate_date, validate_range, validate_menu

def test_valid_email():

  n = validate_email('André Anjos <andre.anjos@idiap.ch')
  nose.tools.eq_(len(n), 2)
  assert n[1].count('@') == 1
  assert n[0].count('@') == 0

def test_invalid_email():

  n = validate_email(']andre!anjos')
  assert not n[0] and  not n[1]

def test_valid_date():

  import datetime
  today = datetime.date.today()

  d = validate_date('today')
  nose.tools.eq_(d, today)

  d = validate_date('12')
  nose.tools.eq_(d.day, 12)
  nose.tools.eq_(d.month, today.month)
  nose.tools.eq_(d.year, today.year)

  d = validate_date('12.3')
  nose.tools.eq_(d.day, 12)
  nose.tools.eq_(d.month, 3)
  nose.tools.eq_(d.year, today.year)

  d = validate_date('12.3.04')
  nose.tools.eq_(d.day, 12)
  nose.tools.eq_(d.month, 3)
  nose.tools.eq_(d.year, 2004)

def test_valid_ranges():

  assert validate_range('..')
  assert validate_range('1..20')
  assert validate_range('1..')
  assert validate_range('..20')
  assert validate_range('today..20')
  assert validate_range('today..')
  assert validate_range('..today')

@nose.tools.raises(ValueError)
def test_invalid_date_1():

  d = validate_date('12.3.4')

@nose.tools.raises(ValueError)
def test_invalid_date_2():

  d = validate_date('12.3.4.5')

def test_valid_menu():

  french, english = validate_menu('menu en français (english menu)')
  assert french
  assert not french.count('(')
  assert not french.count(')')
  assert english
  assert not english.count('(')
  assert not english.count(')')

  french, english = validate_menu('seulement en français')
  assert french
  assert not english
