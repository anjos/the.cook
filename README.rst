.. vim: set fileencoding=utf-8 :
.. Andre Anjos <andre.anjos@idiap.ch>
.. Thu 24 Apr 17:24:10 2014 CEST

.. image:: https://travis-ci.org/anjos/the.cook.svg?branch=master
   :target: https://travis-ci.org/anjos/the.cook
.. image:: https://coveralls.io/repos/anjos/the.cook/badge.png
   :target: https://coveralls.io/r/anjos/the.cook
.. image:: http://img.shields.io/github/tag/anjos/the.cook.png
   :target: https://github.com/anjos/the.cook

================================
 Idiap Lunch Management Utility
================================

This package contains an utility program called ``lunch``, that can be used to
manage Idiap Lunches organised by the Vatel Restaurant. It was developped with
the intent of easing management of menus and subscriptions, allowing for
interested parties to dump statistics and automate announcement tasks.

Installation
------------

You normally don't need to install this package at Idiap, to make use of it.
Just call ``~aanjos/the.cook/bin/lunch`` for help and commands.

If you still need to install this package locally, for maintenance reasons, do
it by clonning it locally and running buildout::

  $ python bootstrap.py
  $ ./bin/buildout

Usage
-----

Usage is pretty simple. Here is what you can do with the ``lunch`` command line
utility:

  * List next available menus (``show``)
  * Subscribe for lunch (``sub``)
  * Unsubscribe for lunch (``unsub``)

There is also a management utility called ``manage``, that allows for managing
the available menus, sending reminders for lunch subscriptions and other
management tasks:

  * Add a new menu for a specific date (``add``)
  * Remove a menu for a specific date (``remove``)
  * List past subscriptions and menus (``list``)
  * Send a call for subscription (``call``)
  * Send a PDF report to the Vatel Restaurant (``report``)
  * Send a reminder for subscribers of the day lunch (``remind``)

You can use the flag ``--help`` on both utilities to see more options.

Tests
-----

A suite of test units is available by running::

  $ ./bin/nosetests -sv
