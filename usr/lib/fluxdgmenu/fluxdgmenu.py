import os, sys, re, StringIO, sqlite3, ConfigParser, urllib
import xdg.Config, xdg.BaseDirectory, xdg.DesktopEntry, xdg.Menu, xdg.IconTheme
#from xdg.Exceptions import *


###########################################################
# The base menu class
#
class ApplicationsMenu(object):

    default_config = """
[Menu]
submenu: no
filemanager: thunar
terminal: x-terminal-emulator -T '%(title)s' -e '%(command)s'
[Icons]
show: yes
use_gtk_theme: yes
theme: Mint-X
size: 24
default: application-x-executable
bookmarks: user-bookmarks
"""

    window_manager = "Fluxbox"

    def __init__(self):
        xdg.Config.setWindowManager(self.window_manager)
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')
        self.parse_config()
        self.exe_regex = re.compile(r' [^ ]*%[fFuUdDnNickvm]')

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

    def parse_menu_file(self, menu_file):
        if self.show_icons:
            self.open_cache()
        menu = xdg.Menu.parse(menu_file)
        output = self.menu_entry(menu)
        output = self.format_menu(output)
        if self.show_icons:
            self.close_cache()
        return output

    def format_menu(self, content):
        return content

    def format_separator(self, indent):
        return "%s[separator] (---------------------)" % indent

    def format_application(self, name, cmd, icon, indent):
        name = name.replace('(', ':: ').replace(')',' ::')
        return "%s[exec] (%s) {%s} <%s>" % (indent, name, cmd, icon)

    def format_submenu(self, id, name, icon, submenu, indent):
        return "%s[submenu] (%s) <%s>\n%s%s\n[end]" % (indent, name, icon, submenu, indent)
    
    def menu_entry(self, menu, level=0):
        output = []
        append = output.append
        for entry in menu.getEntries():
            if isinstance(entry, xdg.Menu.Separator):
                append(self.separator(entry, level))
            elif isinstance(entry, xdg.Menu.Menu):
                append(self.submenu(entry, level))
            elif isinstance(entry, xdg.Menu.MenuEntry):
                append(self.application(entry, level))
        return "\n".join(output)

    def separator(self, entry, level):
        indent = "  " * level
        return self.format_separator(indent)

    def submenu(self, entry, level):
        id = entry.Name.encode('utf-8')
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        submenu = self.menu_entry(entry, level+1)
        indent = "  " * level
        return self.format_submenu(id, name, icon, submenu, indent)

    def application(self, entry, level):
        de = entry.DesktopEntry
        # Skip Debian specific menu entries
        if self.filter_debian and de.get('Categories', list=False).startswith('X-Debian'):
            return
        # Escape entry name
        name = de.getName().encode('utf-8')
        # Strip command arguments
        cmd = self.exe_regex.sub('', de.getExec())
        if de.getTerminal():
            cmd = self.terminal_emulator % {"title": name, "command": cmd}
        # Get icon
        icon = self.find_icon(de.getIcon().encode('utf-8')) if self.show_icons else ''

        indent = "  " * level
        return self.format_application(name, cmd, icon, indent)

    def open_cache(self):
        self.cache_conn = sqlite3.connect(
            os.path.expanduser('~/.cache/uxdgmenu/icons.db')
        )
        self.cache_conn.execute(
            "CREATE TABLE IF NOT EXISTS cache(key TEXT, path TEXT)"
        )
        self.cache_conn.row_factory = sqlite3.Row
        self.cache_cursor = self.cache_conn.cursor()

    def close_cache(self):
        self.cache_conn.commit()
        self.cache_cursor.close()

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
        # Fluxbox doesn't support svg in menu
        path = xdg.IconTheme.getIconPath(
            name, self.icon_size, self.theme, ['png','xpm']
        )
        if not path or path.endswith('.svg'):
            path = xdg.IconTheme.getIconPath(
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

###########################################################
# The rootmenu menu class
#
class RootMenu(ApplicationsMenu):

    def __init(self):
        super(RootMenu, self).__init__()
        import gettext
        gettext.install("fluxdgmenu", "/usr/share/locale", unicode=1)
        

    def parse_config(self):
        super(RootMenu, self).parse_config()
        self.as_submenu = self.config.getboolean("Menu", "submenu")

    def format_menu(self, content):
        return """[begin]
%s
[end]""" % content

    def submenu(self, entry):
        if entry.Name == 'fxm-applications':
            return self.app_menu(entry)
        if entry.Name == 'fxm-bookmarks':
            return self.bookmarks_menu(entry)
        elif entry.Name == 'fluxbox':
            return self.fluxbox_menu(entry)
        return super(RootMenu, self).submenu(entry)

    def app_menu(self, entry):
        output = []
        if self.as_submenu:
            name = entry.getName().encode('utf-8')
            icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
            output.append( '[submenu] (%s) <%s>\n  ' % (name, icon) )
        output.append('[include] (~/.fluxbox/fluxdgmenu/applications)\n')
        if self.as_submenu:
            output.append('[end]\n')
        return "".join(output)

    def bookmarks_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        return """
[submenu] (%s) <%s>
  [include] (~/.fl'xbox/fluxdgmenu/bookmarks)
[end]
""" % (name, icon)

    def fluxbox_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        update_cmd = "fxm-daemon update --progress"
        generate_cmd = "fxm-daemon generate-rootmenu --progress"
        return  """
[submenu] (%s) <%s>
  [submenu] (%s)
    [exec] (%s) {%s}
    [exec] (%s) {%s}
  [end]
  [config] (%s)
  [submenu] (%s)
    [stylesdir] (/usr/share/fluxbox/styles)
    [stylesdir] (~/.fluxbox/styles)
  [end]
  [reconfig]
  [restart]
  [exit]
[end]
""" % (
    name, icon,
    _('Menu'),
    _('Update'), update_cmd,
    _('Generate'), generate_cmd,
    _('Configuration'),
    _('Themes')
)



###########################################################
# The bookmarks menu class
#
class BookmarksMenu(ApplicationsMenu):

    def parse_config(self):
        super(BookmarksMenu, self).parse_config()
        self.filemanager = self.config.get("Menu", "filemanager")
        self.bookmark_icon = self.config.get("Icons", "bookmarks")

    def parse_bookmarks(self):
        bookmarks = [ ('~', 'Home') ]
        append = bookmarks.append
        with open(os.path.expanduser('~/.gtk-bookmarks')) as f:
            for line in f:
                path, label = line.strip().partition(' ')[::2]
                if not label:
                    label = os.path.basename(os.path.normpath(path))
                append((path, label))
        if self.show_icons:
            self.open_cache()
            icon = self.find_icon(self.bookmark_icon)
            self.close_cache()
        else:
            icon = ''
        output = ["[exec] (%s) {%s} <%s>" % (
                urllib.unquote(label),
                "%s %s" % (self.filemanager, path),
                icon
            ) for path, label in bookmarks]
        return "\n".join(output)
