import os, sys, re, urllib
from . import base
try:
    from xml.etree import cElementTree as ElementTree
except:
    from xml.etree import ElementTree
try:
    import gio
    HAS_GIO = True
except:
    HAS_GIO = False

import gettext
__t = gettext.translation("fluxdgmenu", "/usr/share/locale")
_ = __t.ugettext

class RecentlyUsedMenu(base.Menu):

    def __init__(self):
        super(RecentlyUsedMenu, self).__init__()
        self.exe_regex = re.compile(r"'(.*) %[a-zA-Z]'")
        mime_ns = 'http://www.freedesktop.org/standards/shared-mime-info'
        bookmark_ns = 'http://www.freedesktop.org/standards/desktop-bookmarks' 
        self.find_mime = 'info/metadata/{%s}mime-type' % mime_ns
        self.find_bookmark = 'info/metadata/{%(ns)s}applications/{%(ns)s}application' % {
            "ns": bookmark_ns
        }

    def parse_config(self):
        super(RecentlyUsedMenu, self).parse_config()
        self.max_items = self.config.getint("Recently Used", "max_items")
        if self.show_icons and not HAS_GIO:
            self.file_icon = self.find_icon(self.config.get("Icons", "files"))

    def parse_bookmarks(self):
        source = os.path.expanduser("~/.recently-used.xbel")
        tree = ElementTree.parse(source)
        last_index = - (self.max_items -1)
        bookmarks = tree.findall('/bookmark')[last_index:-1]
        bookmarks.reverse()
        output = map(self.parse_item, bookmarks)
        output.extend([
            self.format_separator(0),
            self.format_application(
                _('Clear List'), 'fxm-daemon clear-recently-used',
                self.find_icon('gtk-clear') if self.show_icons else '', 
                0
            )
        ])
        return self.format_menu( "".join(output) )

    def parse_item(self, el):
        href = el.get('href')
        label = urllib.unquote( href.rsplit('/',1)[1] )
        cmd = el.find(self.find_bookmark).get('exec')
        cmd = self.exe_regex.sub(r'\1', cmd)
        cmd = '%s "%s"' % (cmd, href)
        mime_type = el.find(self.find_mime).get('type')
        icon = ''
        if self.show_icons:
            icon = self.find_icon_by_mime_type(mime_type) if HAS_GIO else self.file_icon
        return self.format_application(label, cmd, icon)

    def find_icon_by_mime_type(self, mime_type):
        for name in gio.content_type_get_icon(mime_type).get_names():
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

