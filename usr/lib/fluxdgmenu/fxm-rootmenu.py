#!/usr/bin/python
# -*- coding: utf-8 -*-

import os, gettext, subprocess
import fluxdgmenu
from fluxdgmenu import which

class FxmRootMenu(fluxdgmenu.FluXDGMenu):

    def parse_config(self):
        super(FxmRootMenu, self).parse_config()
        self.as_submenu = self.config.getboolean("Menu", "submenu")
        self.has_zenity = True if which('zenity') else False

    def print_menu(self, menu_file):
        print "[begin]\n"
        super(FxmRootMenu, self).print_menu(menu_file)
        print "[end]"

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
        super(FxmRootMenu, self).print_submenu(entry)

    def print_app_menu(self, entry):
        if self.as_submenu:
            name = entry.getName().encode('utf-8')
            icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
            print '[submenu] (%s) <%s>' % (name, icon)
        print '[include] (~/.fluxbox/fluxdgmenu/applications)'
        if self.as_submenu:
            print '[end]'

    def print_bookmarks_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        print """
[submenu] (%s) <%s>
  [include] (~/.fluxbox/fluxdgmenu/bookmarks)
[end]
""" % (name, icon)

    def print_fluxbox_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        zenity_progress = '| zenity --progress --pulsate --auto-close'
        update_cmd = 'fxm-daemon update %s && fluxbox-remote reconfigure' % (
            zenity_progress if self.has_zenity else '')
        generate_cmd = 'fxm-daemon generate-rootmenu %s && fluxbox-remote reconfigure' % (
            zenity_progress if self.has_zenity else '')
        print  """
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

###########################################################################
# MAIN
#--------------------------------------------------------------------------
if __name__ == "__main__":
    # Initialize i18n
    gettext.install("fluxdgmenu", "/usr/share/locale", unicode=1)
    root_menu = FxmRootMenu()
    root_menu.print_menu('fxm-rootmenu.menu')
#--------------------------------------------------------------------------
# / MAIN
###########################################################################
