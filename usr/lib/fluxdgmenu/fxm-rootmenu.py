#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, gettext
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
        print  """[submenu] (%s)
  [exec] (%s) {fxm-daemon update}
  [exec] (%s) {fxm daemon generate-rootmenu}
[end]
[submenu] (%s) <%s>
  [config] (%s)
  [submenu] (%s)
    [stylesdir] (/usr/share/fluxbox/styles)
    [stylesdir] (~/.fluxbox/styles)
  [end]
  [reconfig]
  [restart]
  [exit]
[end]""" % (
    _('Menu'), _('Update'), _('Generate'),
    entry.getName().encode('utf-8'), icon,
    _('Configuration'), _('Themes')
)

###########################################################################
# MAIN
#--------------------------------------------------------------------------
if __name__ == "__main__":
    # Initialize i18n
    gettext.install(
        "fluxdgmenu",
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "locale"),
        unicode=1
    )
    fluxdgmenu = FxmGlobalMenu()
    fluxdgmenu.print_menu('fxm-rootmenu.menu')
#--------------------------------------------------------------------------
# / MAIN
###########################################################################

