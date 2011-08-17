#! /usr/bin/env python
import sys
#try:
import cXdg.BaseDirectory
import cXdg.Config
import cXdg.DesktopEntry
import cXdg.Exceptions
import cXdg.IconTheme
import cXdg.IniFile
import cXdg.Locale
import cXdg.Menu
import cXdg.MenuEditor
import cXdg.Mime
import cXdg.RecentFiles

cXdg.Config.setIconTheme('Mint-X')
print cXdg.IconTheme.getIconPath('firefox');
    #sys.exit(0)
#except:
    #sys.exit(1)
