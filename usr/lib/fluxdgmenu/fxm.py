#!/usr/bin/python
# coding=utf-8

import os, sys, re

import xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.Menu
from xdg.Exceptions import *


def print_separator(entry):
  print '[separator] (-------------------------------)'

def print_submenu(entry):
  print '[submenu] (%s) <%s>' % (
    entry.getName().encode('utf-8'),
    entry.getIcon().encode('utf-8')
  )
  print_menu(entry)
  print '[end]'

def print_exec(entry):
  cmd = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', entry.DesktopEntry.getExec())
  if entry.DesktopEntry.getTerminal():
    cmd = 'x-terminal-emulator -T "%s" -e "%s"' % (
      entry.DesktopEntry.getName().encode('utf-8'),
      cmd
    )
  print '  [exec] (%s) {%s} <%s>' % (
    entry.DesktopEntry.getName().encode('utf-8'),
    cmd,
    entry.DesktopEntry.getIcon().encode('utf-8')
  )

def print_menu(menu):

  for entry in menu.getEntries():
    if isinstance(entry, xdg.Menu.Separator):
      print_separator(entry)
    elif isinstance(entry, xdg.Menu.Menu):
      print_submenu(entry)
    elif isinstance(entry, xdg.Menu.MenuEntry):
      print_exec(entry)



filename = 'fxm-applications.menu'
if len(sys.argv) > 1:
  filename = sys.argv[1]
  if not filename.endswith('.menu'): filename += '.menu'

xdg.Config.setWindowManager('fluxbox')
menu = xdg.Menu.parse(filename)

print_submenu(menu)

