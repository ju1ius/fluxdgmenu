import os, sys, re
from . import base, adapters

class ApplicationsMenu(base.Menu):

    def __init__(self):
        super(ApplicationsMenu, self).__init__()
        self.adapter = self.get_default_adapter()
        #self.set_adapter('xdg')
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')

    def parse_config(self):
        super(ApplicationsMenu, self).parse_config()
        show_all = self.config.getboolean('Menu', 'show_all')
        if show_all:
            self.show_flags = adapters.SHOW_EMPTY
        self.terminal_emulator = self.config.get('Menu', 'terminal')

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file, self.show_flags)
        output = "".join( self.directory(root) )
        output = self.format_menu(output)
        return output

    def separator(self, entry, level):
        return self.format_separator(level)

    def directory(self, entry, level=0):
        for child in entry.get_contents():
            t = child.get_type()
            if t == adapters.TYPE_SEPARATOR:
                yield self.separator(child, level)
            elif t == adapters.TYPE_DIRECTORY:
                yield self.submenu(child, level)
            elif t == adapters.TYPE_ENTRY:
                yield self.application(child, level)

    def submenu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
        submenu = "".join( self.directory(entry, level+1) )
        return self.format_submenu(id, name, icon, submenu, level)

    def application(self, entry, level):
        # Skip Debian specific menu entries
        filepath = entry.get_desktop_file_path()
        if self.filter_debian and "/.local/share/applications/menu-xdg/" in filepath:
            return ''
        # Escape entry name
        name = entry.get_display_name()
        # Strip command arguments
        cmd = self.exe_regex.sub('', entry.get_exec())
        if entry.get_launch_in_terminal():
            cmd = self.terminal_emulator % {"title": name, "command": cmd}
        # Get icon
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''

        return self.format_application(name, cmd, icon, level)

    def get_default_adapter(self):
       return adapters.get_default_adapter()

    def get_adapter(self):
        return self.adapter

    def set_adapter(self, name):
        self.adapter = adapters.get_adapter(name)

