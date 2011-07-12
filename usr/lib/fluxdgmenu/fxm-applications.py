#!/usr/bin/python
# -*- coding: utf-8 -*-

import fluxdgmenu
import time

if __name__ == "__main__":
    start = time.time()
    fluxdgmenu = fluxdgmenu.FluXDGMenu()
    fluxdgmenu.print_menu('fxm-applications.menu')
    end = time.time()
    print "Generated in %s seconds..." % str(end - start)
