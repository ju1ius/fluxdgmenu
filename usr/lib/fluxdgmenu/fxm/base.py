import os, sys, stat, re, sqlite3, ConfigParser
import cStringIO as StringIO
import xdg.IconTheme as IconTheme
from . import config, cache

class Menu(object):

    def __init__(self):
        self.parse_config()
        self.exe_regex = re.compile(r' [^ ]*%[fFuUdDnNickvm]')
        if self.show_icons:
            self.cache = cache.Cache()
            self.cache.open()

    def __del__(self):
        if self.show_icons:
            self.cache.close()

    def parse_config(self):
        self.config = ConfigParser.RawConfigParser()
        self.config.readfp(StringIO.StringIO(config.DEFAULT_CONFIG))
        self.config.read([config.SYSTEM_CONFIG_FILE, config.USER_CONFIG_FILE])

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
                    #self.gtk_theme = gtk.icon_theme_get_default()
                    #self.gtk_icon_flags = gtk.ICON_LOOKUP_NO_SVG
                except:
                    self.use_gtk_theme = False
                    self.theme = self.config.get('Icons','theme')
            else:
                self.theme = self.config.get('Icons','theme')

    
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
        cache_key = self.icon_name_get_cache_key(name)      
        cached = self.cache.get_icon(cache_key)
        if cached:
            return cached['path'].encode('utf-8')
        else:
            path = self.lookup_icon(name)
            if path:
                self.cache.add_icon(cache_key, path)
                return path.encode('utf-8')
            return self.lookup_default_icon().encode('utf-8')

    def icon_name_get_cache_key(self, name):
        if not name:
            name = self.default_icon
        if os.path.isabs(name):
            return name
        return name + '::' + self.theme

    def lookup_icon(self, name):
        # Use xdg.IconTheme icon lookup, omitting svg icons
        path = IconTheme.getIconPath(
            name, self.icon_size, self.theme, ['png','xpm']
        )
        if path and not path.endswith('.svg'):
            return path
        # Use gtk.IconTheme icon lookup
        # Way faster but less accurate at finding icons :(
        #if self.use_gtk_theme:
            #icon = self.gtk_theme.lookup_icon(
                #name, self.icon_size, self.gtk_icon_flags
            #)
            #if not icon:
                #icon = self.gtk_theme.lookup_icon(
                    #self.default_icon, self.icon_size, self.gtk_icon_flags
                #)
            #return icon.get_filename() if icon is not None else ''

    def lookup_default_icon(self):
        return IconTheme.getIconPath(
            self.default_icon, self.icon_size, self.theme, ['png', 'xpm']
        )
