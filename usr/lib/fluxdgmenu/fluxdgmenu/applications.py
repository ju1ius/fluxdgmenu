import os, sys, re
import xdg.Config
import base
import adapters

class ApplicationsMenu(base.Menu):

    def __init__(self):
        super(ApplicationsMenu, self).__init__()
        self.adapter = self.get_default_adapter()
        #self.set_adapter('xdg')
        xdg.Config.setWindowManager('fluxbox')
        self.filter_debian = os.path.isfile('/usr/bin/update-menus')

    def parse_config(self):
        super(ApplicationsMenu, self).parse_config()
        self.terminal_emulator = self.config.get('Menu', 'terminal')

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file)
        output = self.directory(root)
        output = self.format_menu(output)
        return output

    def separator(self, entry, level):
        return self.format_separator(level)

    def directory(self, entry, level=0):
        output = []
        append = output.append
        for child in entry.get_contents():
            t = child.get_type()
            if t == adapters.TYPE_SEPARATOR:
                append( self.separator(child, level) )
            elif t == adapters.TYPE_DIRECTORY:
                append( self.submenu(child, level) )
            elif t == adapters.TYPE_ENTRY:
                append( self.application(child, level) )
        return "".join(output)

    def submenu(self, entry, level):
        id = entry.get_menu_id()
        name = entry.get_name()
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
        submenu = self.directory(entry, level+1)
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
       return adapters.get_default()

    def set_adapter(self, name):
        try:
            self.adapter = adapters.get_adapter(name)
        except:
            self.adapter = self.get_default_adapter()
