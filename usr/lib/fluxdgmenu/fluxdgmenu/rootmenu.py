import os, gettext
import applications

class RootMenu(applications.ApplicationsMenu):

    def __init(self):
        super(RootMenu, self).__init__()
        import gettext
        gettext.install("fluxdgmenu", "/usr/share/locale", unicode=1)      

    def parse_config(self):
        super(RootMenu, self).parse_config()
        self.as_submenu = self.config.getboolean("Menu", "submenu")

    def format_menu(self, content):
        return """[begin]
%s
[end]""" % content

    def submenu(self, entry):
        if entry.Name == 'fxm-applications':
            return self.app_menu(entry)
        if entry.Name == 'fxm-bookmarks':
            return self.bookmarks_menu(entry)
        if entry.Name == 'fxm-recently-used':
            return self.recently_used_menu(entry)
        elif entry.Name == 'fluxbox':
            return self.fluxbox_menu(entry)
        return super(RootMenu, self).submenu(entry)

    def app_menu(self, entry):
        submenu = '[include] (~/.fluxbox/fluxdgmenu/applications)'
        if self.as_submenu:
            name = entry.getName().encode('utf-8')
            icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
            return self.format_submenu('', name, icon, '  ')
        else:
            return submenu

    def bookmarks_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        submenu = "[include] (~/.fluxbox/fluxdgmenu/bookmarks)"
        return self.format_submenu('', name, icon, submenu, '  ')

    def recently_used_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        submenu = "[include] (~/.fluxbox/fluxdgmenu/recently-used)"
        return self.format_submenu('', name, icon, submenu, '  ')

    def fluxbox_menu(self, entry):
        name = entry.getName().encode('utf-8')
        icon = self.find_icon(entry.getIcon().encode('utf-8')) if self.show_icons else ''
        update_cmd = "fxm-daemon update --progress"
        generate_cmd = "fxm-daemon generate-rootmenu --progress"
        submenu = """
[submenu] (%s)
  [exec] (%s) {%s}
  [exec] (%s) {%s}
[end]
[config] (%s)
[submenu] (%s)
  [stylesdir] (/usr/share/fluxbox/styles)
  [stylesdir] (~/.fluxbox/styles)
[end] '
[reconfig]
[restart]
[exit]
""" % (
            _('Menu'),
            _('Update'), update_cmd,
            _('Generate'), generate_cmd,
            _('Configuration'),
            _('Themes')
        )
        return self.format_submenu('', name, icon, submenu, '  ')
