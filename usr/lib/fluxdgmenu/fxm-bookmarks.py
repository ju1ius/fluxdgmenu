#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, urllib
import fluxdgmenu

class FxmBookmarksMenu(fluxdgmenu.FluXDGMenu):

    def parse_config(self):
        super(FxmBookmarksMenu, self).parse_config()
        self.filemanager = self.config.get("Menu", "filemanager")
        self.bookmark_icon = self.config.get("Icons", "bookmark")

    def print_bookmarks(self):
        bookmarks = [ ('~', 'Home') ]
        with open(os.path.expanduser('~/.gtk-bookmarks')) as f
            for line in f:
                path, label = line.strip().partition(' ')[::2]
                if not label:
                    label = os.path.basename(os.path.normpath(path))
                bookmarks.append((path, label))
        if self.show_icons:
            self.open_cache()
            icon = self.find_icon(self.bookmark_icon)
            self.close_cache()
        else:
            icon = ''
        for path, label in bookmarks:
            print "[exec] (%s) {%s} <%s>" % (
                urllib.unquote(label),
                "%s %s" % (self.filemanager, path),
                icon
            )

if __name__ == "__main__":
    menu = FxmBookmarksMenu()
    menu.print_bookmarks()
