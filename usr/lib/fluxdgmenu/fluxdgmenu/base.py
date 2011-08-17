import os, sys, stat, re, StringIO, sqlite3, ConfigParser
import xdg.IconTheme as IconTheme
#import cXdg.IconTheme as IconTheme


class Menu(object):

    default_config = """
[Menu]
filemanager: thunar
terminal: x-terminal-emulator -T '%(title)s' -e '%(command)s'
as_submenu: no
[Recently Used]
max_items: 20
[Icons]
show: yes
use_gtk_theme: yes
theme: Mint-X
size: 24
default: application-default-icon
bookmarks: user-bookmarks
folders: folder
files: gtk-file
"""

    def __init__(self):
        self.parse_config()
        self.exe_regex = re.compile(r' [^ ]*%[fFuUdDnNickvm]')
        if self.show_icons:
            self.open_cache()

    def __del__(self):
        if self.show_icons:
            self.close_cache()

    def parse_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(StringIO.StringIO(self.default_config))
        self.config.read([
            '/etc/marchobmenu/menu.conf',
            os.path.expanduser('~/.config/marchobmenu/menu.conf')
        ])

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
                    self.gtk_theme = gtk.icon_theme_get_default()
                    self.gtk_icon_flags = gtk.ICON_LOOKUP_NO_SVG
                except:
                    self.use_gtk_theme = False
                    self.theme = self.config.get('Icons','theme')
            else:
                self.theme = self.config.get('Icons','theme')

    def open_cache(self):
        db_file = os.path.expanduser('~/.fluxbox/fluxdgmenu/icons.db')
        self.cache_conn = sqlite3.connect(db_file)
        self.cache_conn.execute(
            "CREATE TABLE IF NOT EXISTS cache(key TEXT, path TEXT)"
        )
        self.cache_conn.row_factory = sqlite3.Row
        self.cache_cursor = self.cache_conn.cursor()

    def close_cache(self):
        self.cache_conn.commit()
        self.cache_cursor.close()
    
    def format_menu(self, content):
      return content

    def format_text_item(self, txt, level=0):
        return "%s[nop] (%s)\n" % (
            "  " * level,
            self.escape_label(txt.encode('utf-8'))
        )

    def format_include(self, filepath, level=0):
        return "%s[include] (%s)\n" % (
            "  " * level,
            self.escape_label(filepath.encode('utf-8'))
        )

    def format_separator(self, level=0):
        return "%s[separator] (---------------------)\n" % ("  " * level)

    def format_application(self, name, cmd, icon, level=0):
        return "%s[exec] (%s) {%s} <%s>\n" % (
            "  " * level, self.escape_label(name.encode('utf-8')),
            cmd.encode('utf-8'),
            icon.encode('utf-8')
        )

    def format_submenu(self, id, name, icon, submenu, level=0):
        return """%(i)s[submenu] (%(n)s) <%(icn)s>\n%(sub)s%(i)s[end]\n""" % {
            "i": "  " * level,
            "n": self.escape_label(name.encode('utf-8')),
            "icn": icon.encode('utf-8'),
            "sub": submenu
        }

    def escape_label(self, label):
        return label.replace('(', ':: ').replace(')', ' ::')

    def find_icon(self, name):
        """Finds and cache icons"""
        if not name:
            name = self.default_icon
        if os.path.isabs(name):
            key = name
        else:
            key = name + '::' + self.theme      
        cached = self.fetch_cache_key(key)
        if cached:
            return cached['path'].encode('utf-8')
        else:
            path = self.get_icon_path(name)
            if path:
                self.add_cache_key(key, path)
                return path.encode('utf-8')
        return ''

    def get_icon_path(self, name):
        # Use gtk.IconTheme icon lookup => faster !
        if self.use_gtk_theme:
            icon = self.gtk_theme.lookup_icon(
                name, self.icon_size, self.gtk_icon_flags
            )
            if not icon:
                icon = self.gtk_theme.lookup_icon(
                    self.default_icon, self.icon_size, self.gtk_icon_flags
                )
            return icon.get_filename() if icon is not None else ''
        # Use xdg.IconTheme icon lookup, omitting svg icons
        path = IconTheme.getIconPath(
            name, self.icon_size, self.theme, ['png','xpm']
        )
        if not path or path.endswith('.svg'):
            path = IconTheme.getIconPath(
                self.default_icon, self.icon_size, self.theme, ['png', 'xpm']
            )
        return path

    def fetch_cache_key(self, key):
        self.cache_cursor.execute(
            'SELECT cache.key, cache.path FROM cache WHERE cache.key = ?',
            [key]
        )
        return self.cache_cursor.fetchone()

    def add_cache_key(self, key, path):
        self.cache_cursor.execute(
            'INSERT INTO cache(key, path) VALUES(?,?)',
            [key, path]
        )
