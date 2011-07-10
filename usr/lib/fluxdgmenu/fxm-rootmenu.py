#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import fluxdgmenu

class FxmGlobalMenu(fluxdgmenu.FluXDGMenu):

    def before_print(self):
        print "[begin]\n"
    def after_print(self):
        print "\n[end]"

    def print_submenu(self, entry):
        if entry.getName() == 'fxm-applications':
            self.print_app_menu()
            return
        elif entry.getName() == 'fluxbox':
            self.print_fluxbox_menu()
            return
        super(FxmGlobalMenu, self).print_submenu(entry)

    def print_app_menu(self):
        print '[include] (~/.fluxbox/fluxdgmenu/menu)'

    def print_fluxbox_menu(self):
       print  """[submenu] (Fluxbox)
  [config] (Config)
  [submenu] (Themes)
    [stylesdir] (/usr/share/fluxbox/styles)
    [stylesdir] (~/.fluxbox/styles)
  [end]
  [reconfig]
  [restart]
  [exit]
[end]"""

###########################################################################
# MAIN
#--------------------------------------------------------------------------
if __name__ == "__main__":
    fluxdgmenu = FxmGlobalMenu('fxm-rootmenu.menu')
#--------------------------------------------------------------------------
# / MAIN
###########################################################################

