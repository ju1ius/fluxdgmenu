#! /usr/bin/python
# -*- coding: utf-8 -*-

import os, urllib
import fluxdgmenu

class FxmBookmarksMenu(fluxdgmenu.FluXDGMenu):

    def parse_config(self):
        super(FxmBookmarksMenu, self).parse_config()
        self.filemanager = self.config.get("Menu", "filemanager")

    def print_bookmarks(self):
        bookmarks_file = open(os.path.expanduser('~/.gtk-bookmarks'))
        self.open_cache()
        icon = self.find_icon('user-bookmarks')
        self.close_cache()
        bookmarks = [ ('~', 'Home') ]
        for line in bookmarks_file:
            path, label = line.strip().partition(' ')[::2]
            if not label:
                label = os.path.basename(os.path.normpath(path))
            bookmarks.append((path, label))
        for path, label in bookmarks:
            print "[exec] (%s) {%s} <%s>" % (
                urllib.unquote(label),
                "%s %s" % (self.filemanager, path),
                icon
            )

if __name__ == "__main__":
    menu = FxmBookmarksMenu()
    menu.print_bookmarks()
