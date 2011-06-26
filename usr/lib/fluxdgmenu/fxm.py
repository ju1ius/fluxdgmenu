#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, sys, re, StringIO, sqlite3, ConfigParser

import xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.Menu, xdg.IconTheme
#from xdg.Exceptions import *

class FluXDGMenu(object):

  def __init__(self, output):
    self.parse_config()
    self.tree = xdg.Menu.parse('fxm-applications.menu')
    self.print_all()
    self.output.close()

  def parse_config(self):
    self.config = ConfigParser.RawConfigParser()
    self.config.readfp(StringIO.StringIO("""
[Icons]
show: True
themes: Minty,gnome-wise,hicolor
size: 24
"""))
    self.config.read([
      '/etc/fluxdgmenu/menu.conf',
      os.path.expanduser('~/.fluxbox/fluxdgmenu/menu.conf')
    ])

    self.show_icons = self.config.getboolean('Icons', 'show')
    self.themes = [t.strip() for t in self.config.get('Icons','themes').split(',')]
    self.themes.reverse()
    self.themes_key = '-'.join(self.themes)
    self.icon_size = self.config.getint('Icons', 'size')

    xdg.Config.setWindowManager('fluxbox')
    for theme in self.themes:
      xdg.Config.setIconTheme(theme)
    xdg.Config.setIconSize(self.icon_size)

    self.filter_debian = os.path.isfile('/usr/bin/update-menus')

  def print_all(self):
    """Prints the menu to output"""
    self.open_cache()
    self.print_menu(self.tree)
    self.close_cache()

  def open_cache(self):
    if self.show_icons:
      self.cache_conn = sqlite3.connect(
        os.path.expanduser('~/.fluxbox/fluxdgmenu/icons.db')
      )
      self.cache_conn.execute(
        "CREATE TABLE IF NOT EXISTS cache(key TEXT, path TEXT)"
      )

      self.cache_conn.row_factory = sqlite3.Row
      self.cache_cursor = self.cache_conn.cursor()

  def close_cache(self):
    if self.show_icons:
      self.cache_conn.commit()
      self.cache_cursor.close()

  def print_menu(self, menu):
    for entry in menu.getEntries():
      if isinstance(entry, xdg.Menu.Separator):
        self.print_separator(entry)
      elif isinstance(entry, xdg.Menu.Menu):
        self.print_submenu(entry)
      elif isinstance(entry, xdg.Menu.MenuEntry):
        self.print_exec(entry)

  def print_separator(self, entry):
    print '[separator] (-------------------------------)'

  def print_submenu(self, entry):
    if self.show_icons:
      print '[submenu] (%s) <%s>' % (
        entry.getName().encode('utf-8'),
        self.find_icon(entry.getIcon().encode('utf-8'))
      )
    else:
      print '[submenu] (%s)' % entry.getName().encode('utf-8')
    self.print_menu(entry)
    print '[end]'

  def print_exec(self, entry):
    de = entry.DesktopEntry
    # Skip Debian specific menu entries
    if self.filter_debian and de.get('Categories', list=False).startswith('X-Debian'):
      return
    # Strip command arguments
    cmd = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', de.getExec())
    if de.getTerminal():
      cmd = 'x-terminal-emulator -T "%s" -e "%s"' % (
        de.getName().encode('utf-8'),
        cmd
      )
    if self.show_icons:
      print '  [exec] (%s) {%s} <%s>' % (
        de.getName().encode('utf-8'),
        cmd,
        self.find_icon(de.getIcon().encode('utf-8'))
      )
    else:
      print '  [exec] (%s) {%s}' % (
        de.getName().encode('utf-8'),
        cmd
      )

  def find_icon(self, name):
    """Finds and cache icons"""
    key = self.themes_key + ':' + name
    self.cache_cursor.execute(
      'SELECT cache.key, cache.path FROM cache WHERE cache.key = ?',
      [key]
    )
    found = self.cache_cursor.fetchone()
    if found:
      return found['path'].encode('utf-8')
    else:
      path = xdg.IconTheme.getIconPath(name)
      if path:
        self.cache_cursor.execute(
          'INSERT INTO cache(key, path) VALUES(?,?)',
          [key, path]
        )
        return path.encode('utf-8')
      else:
        return ''



###########################################################################
# MAIN
#--------------------------------------------------------------------------
if __name__ == "__main__":
  
  fluxdgmenu = FluXDGMenu(sys.argv[1])
#--------------------------------------------------------------------------
# / MAIN
###########################################################################

