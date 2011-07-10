import os, sys, re, StringIO, sqlite3, ConfigParser
import xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.Menu, xdg.IconTheme
#from xdg.Exceptions import *

class FluXDGMenu(object):

    def __init__(self, menu_file):
        xdg.Config.setWindowManager('fluxbox')
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')
        self.parse_config()
        self.tree = xdg.Menu.parse(menu_file)
        self.print_all()

    def parse_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(StringIO.StringIO("""
[Icons]
show: True
themes: Mint-X,Minty,gnome-wise,gnome-colors-common,gnome,hicolor
default: application-x-executable
size: 24
"""))
        self.config.read([
            '/etc/fluxdgmenu/menu.conf',
            os.path.expanduser('~/.fluxbox/fluxdgmenu/menu.conf')
        ])

        self.show_icons = self.config.getboolean('Icons', 'show')
        if self.show_icons:
            self.default_icon = self.config.get('Icons', 'default')
            self.themes = [t.strip() for t in self.config.get('Icons','themes').split(',')]
            self.themes.reverse()
            self.themes_key = ':'.join(self.themes)
            self.icon_size = self.config.getint('Icons', 'size')

            for theme in self.themes:
                xdg.Config.setIconTheme(theme)
            xdg.Config.setIconSize(self.icon_size)


    def print_all(self):
        """Prints the menu to output"""
        self.before_print()
        self.open_cache()
        self.print_menu(self.tree)
        self.close_cache()
        self.after_print()

    def before_print(self):
        pass
    def after_print(self):
        pass

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
        name = entry.getName().encode('utf-8')
        if self.show_icons:
            print '[submenu] (%s) <%s>' % (
                name,
                self.find_icon(entry.getIcon().encode('utf-8'))
            )
        else:
            print '[submenu] (%s)' % name
        self.print_menu(entry)
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
            cmd = 'x-terminal-emulator -T "%s" -e "%s"' % (name, cmd)
        if self.show_icons:
            print '  [exec] (%s) {%s} <%s>' % (
                name, cmd,
                self.find_icon(de.getIcon().encode('utf-8'))
            )
        else:
            print '  [exec] (%s) {%s}' % (name, cmd)

  
    def find_icon(self, name):
        """Finds and cache icons"""
        if not name:
            name = self.default_icon
        key = name + '::' + self.themes_key
        self.cache_cursor.execute(
            'SELECT cache.key, cache.path FROM cache WHERE cache.key = ?',
            [key]
        )
        found = self.cache_cursor.fetchone()
        if found:
            return found['path'].encode('utf-8')
        else:
            # Fluxbox doesn't support svg in menu
            path = xdg.IconTheme.getIconPath(
                name, self.icon_size, None, ['png','xpm']
            )
            if not path or path.endswith('.svg'):
                path = xdg.IconTheme.getIconPath(
                    self.default_icon, self.icon_size, None, ['png', 'xpm']
                )
        if path:
            self.cache_cursor.execute(
                'INSERT INTO cache(key, path) VALUES(?,?)',
                [key, path]
            )
            return path.encode('utf-8')
        else:
            return ''
