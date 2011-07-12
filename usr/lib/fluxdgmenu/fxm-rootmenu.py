#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import fluxdgmenu

class FxmGlobalMenu(fluxdgmenu.FluXDGMenu):

    def print_menu(self, menu_file):
        print "[begin]\n"
        super(FxmGlobalMenu, self).print_menu(menu_file)
        print "\n[end]"

    def print_submenu(self, entry):
        if entry.Name == 'fxm-applications':
            self.print_app_menu(entry)
            return
        if entry.Name == 'fxm-bookmarks':
            self.print_bookmarks_menu(entry)
            return
        elif entry.Name == 'fluxbox':
            self.print_fluxbox_menu(entry)
            return
        super(FxmGlobalMenu, self).print_submenu(entry)

    def print_app_menu(self, entry):
        print '[include] (~/.fluxbox/fluxdgmenu/applications)'

    def print_bookmarks_menu(self, entry):
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        print '[submenu] (%s) <%s>' % (entry.getName().encode('utf-8'), icon)
        print '[include] (~/.fluxbox/fluxdgmenu/bookmarks)'
        print '[end]'

    def print_fluxbox_menu(self, entry):
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        print  """[submenu] (%s) <%s>
  [config] (Config)
  [submenu] (Themes)
    [stylesdir] (/usr/share/fluxbox/styles)
    [stylesdir] (~/.fluxbox/styles)
  [end]
  [reconfig]
  [restart]
  [exit]
[end]""" % (entry.getName().encode('utf-8'), icon)

###########################################################################
# MAIN
#--------------------------------------------------------------------------
if __name__ == "__main__":
    fluxdgmenu = FxmGlobalMenu()
    fluxdgmenu.print_menu('fxm-rootmenu.menu')
#--------------------------------------------------------------------------
# / MAIN
###########################################################################

