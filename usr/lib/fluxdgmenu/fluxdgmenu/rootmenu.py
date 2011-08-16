import os
import applications
import adapters
        
import gettext
gettext.install("fluxdgmenu", "/usr/share/locale", unicode=1)      

class RootMenu(applications.ApplicationsMenu):

    def parse_config(self):
        super(RootMenu, self).parse_config()
        self.as_submenu = self.config.getboolean("Menu", "as_submenu")

    def parse_menu_file(self, menu_file):
        root = self.adapter.get_root_directory(menu_file, adapters.SHOW_EMPTY)
        output = self.directory(root, 1)
        output = self.format_menu(output)
        return output

    def format_menu(self, content):
        return """[begin]\n%s[end]""" % content

    def submenu(self, entry, level=1):
        id = entry.get_menu_id()
        if id == 'fxm-applications':
            return self.app_menu(entry, level)
        if id == 'fxm-bookmarks':
            return self.bookmarks_menu(entry, level)
        if id == 'fxm-recently-used':
            return self.recently_used_menu(entry, level)
        elif id == 'fluxbox':
            return self.fluxbox_menu(entry, level)
        return super(RootMenu, self).submenu(entry, level)

    def app_menu(self, entry, level):
        filename = '~/.fluxbox/fluxdgmenu/applications'
        if self.as_submenu:
            name = entry.get_name()
            icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
            return self.format_submenu(
                'fxm-applications', name, icon,
                self.format_include(filename, level+1), level
            )
        else:
            return self.format_include(filename, level)

    def bookmarks_menu(self, entry, level):
        filename = "~/.fluxbox/fluxdgmenu/bookmarks"
        name = entry.get_name()
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
        return self.format_submenu(
            'fxm-bookmarks', name, icon,
            self.format_include(filename, level+1), level
        )

    def recently_used_menu(self, entry, level):
        filename = "~/.fluxbox/fluxdgmenu/recently-used"
        name = entry.get_name()
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
        return self.format_submenu(
            'fxm-recently-used', name, icon,
            self.format_include(filename, level+1), level
        )

    def fluxbox_menu(self, entry, level):
        name = entry.get_name()
        icon = self.find_icon(entry.get_icon()) if self.show_icons else ''
        update_cmd = "fxm-daemon update --progress"
        generate_cmd = "fxm-daemon generate-rootmenu --progress"
        indent = "  " * (level + 1)
        submenu = """%(i)s[submenu] (%(fxm)s)
%(i)s  [exec] (%(fxm-up-n)s) {%(fxm-up-c)s}
%(i)s  [exec] (%(fxm-gen-n)s) {%(fxm-gen-c)s}
%(i)s[end]
%(i)s[config] (%(conf)s)
%(i)s[submenu] (%(styles)s)
%(i)s  [stylesdir] (/usr/share/fluxbox/styles)
%(i)s  [stylesdir] (~/.fluxbox/styles)
%(i)s[end]
%(i)s[reconfig]
%(i)s[restart]
%(i)s[exit]
""" % {
            "fxm": _('Menu'),
            "fxm-up-n": _('Update'), "fxm-up-c": update_cmd,
            "fxm-gen-n": _('Generate'), "fxm-gen-c": generate_cmd,
            "conf": _('Configuration'),
            "styles": _('Themes'),
            "i": indent
        }
        return self.format_submenu('fluxbox', name, icon, submenu, level)
