import os, sys, re, StringIO, sqlite3, ConfigParser
import xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.Menu, xdg.IconTheme
#from xdg.Exceptions import *

class FluXDGMenu(object):

    default_config = """
[Menu]
filemanager: nautilus --no-desktop
terminal: x-terminal-emulator -T '%(title)s' -e '%(command)s'
[Icons]
show: yes
use_gtk_theme: yes
theme: Mint-X
default: application-x-executable
size: 24
"""

    window_manager = "Fluxbox"

    def __init__(self):
        xdg.Config.setWindowManager(self.window_manager)
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')
        self.parse_config()

    def parse_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(StringIO.StringIO(self.default_config))
        self.config.read([
            '/etc/fluxdgmenu/menu.conf',
            os.path.expanduser('~/.fluxbox/fluxdgmenu/menu.conf')
        ])

        self.terminal_emulator = self.config.get('Menu', 'terminal')
        self.show_icons = self.config.getboolean('Icons', 'show')

        if self.show_icons:
            self.default_icon = self.config.get('Icons', 'default')
            self.icon_size = self.config.getint('Icons', 'size')
            self.use_gtk_theme = self.config.getboolean('Icons', 'use_gtk_theme')
            if self.use_gtk_theme:
                try:
                    import pygtk
                    pygtk.require('2.0')
                    import gtk
                    gtk_settings = gtk.settings_get_default()
                    self.theme = gtk_settings.get_property('gtk-icon-theme-name')
                except:
                    self.use_gtk_theme = False
                    self.theme = self.config.get('Icons','theme')
            else:
                self.theme = self.config.get('Icons','theme')

    def print_menu(self, menu_file):
        if self.show_icons:
            self.open_cache()
        menu = xdg.Menu.parse(menu_file)
        self.print_menu_entry(menu)
        if self.show_icons:
            self.close_cache()

    def open_cache(self):
        self.cache_conn = sqlite3.connect(
            os.path.expanduser('~/.fluxbox/fluxdgmenu/icons.db')
        )
        self.cache_conn.execute(
            "CREATE TABLE IF NOT EXISTS cache(key TEXT, path TEXT)"
        )
        self.cache_conn.row_factory = sqlite3.Row
        self.cache_cursor = self.cache_conn.cursor()

    def close_cache(self):
        self.cache_conn.commit()
        self.cache_cursor.close()
    
    def print_menu_entry(self, menu):
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
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        print '[submenu] (%s) <%s>' % (name, icon)
        self.print_menu_entry(entry)
        print '[end]'

    def print_exec(self, entry):
        de = entry.DesktopEntry
        # Skip Debian specific menu entries
        if self.filter_debian and de.get('Categories', list=False).startswith('X-Debian'):
            return
        # Escape entry name
        name = de.getName().replace('(', '- ').replace(')',' -').encode('utf-8')
        # Strip command arguments
        cmd = re.sub(' [^ ]*%[fFuUdDnNickvm]', '', de.getExec())
        if de.getTerminal():
            cmd = self.terminal_emulator % {"title": name, "command": cmd}
        # Get icon
        icon = self.find_icon(de.getIcon().encode('utf-8')) if self.show_icons else ''
        print '  [exec] (%s) {%s} <%s>' % (name, cmd, icon)


  
    def find_icon(self, name):
        """Finds and cache icons"""
        if not name:
            name = self.default_icon
        if os.path.isabs(name):
            key = name
        else:
            key = name + '::' + self.theme
        self.cache_cursor.execute(
            'SELECT cache.key, cache.path FROM cache WHERE cache.key = ?',
            [key]
        )
        cached = self.cache_cursor.fetchone()
        if cached:
            return cached['path'].encode('utf-8')
        else:
            # Fluxbox doesn't support svg in menu
            path = xdg.IconTheme.getIconPath(
                name, self.icon_size, self.theme, ['png','xpm']
            )
            if not path or path.endswith('.svg'):
                path = xdg.IconTheme.getIconPath(
                    self.default_icon, self.icon_size, self.theme, ['png', 'xpm']
                )
        if path:
            self.cache_cursor.execute(
                'INSERT INTO cache(key, path) VALUES(?,?)',
                [key, path]
            )
            return path.encode('utf-8')
        else:
            return ''
