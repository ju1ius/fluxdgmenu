#! /usr/bin/env python

import os, glob, optparse, subprocess, time

if __name__ == "__main__":
    path = os.path.abspath(os.path.dirname(__file__))
    po_strings = {
        "menu": 'gtk+',
        "_update": 'gnome-applets',
        "_generate": 'gnome-system-tools',
        "configuration": 'libgnomeprintui',
        "themes": 'gnome-applets',
        "_clear list": "gtk+"
        }
    ini_strings = {
        "recently used": ("gtk+","fxm-menu-recently-used.directory"),
        "bookmarks": ('nautilus','fxm-menu-bookmarks.directory')
    }

    usage = """%prog [options]"""
    op = optparse.OptionParser(usage)
    op.add_option(
        '-p','--po', action='store_true',
        help="Regenerates all .po files"
    )
    op.add_option(
        '-d','--dir', action='store_true',
        help="Regenerates all .directory files"
    )
    op.add_option(
        '-a', '--all', action='store_true',
        help="Same as %prog -pd"
    )
    opts, args = op.parse_args()

    start = time.clock()

    if opts.po or opts.all:
        po_path = os.path.normpath('%s/../po' % path)
        for f in glob.iglob('%s/*.po' % po_path):
            os.remove(f)
        for k,v in po_strings.items():
            subprocess.call('/home/ju1ius/code/locale/mkpo.py "%s" "%s" "%s"' %(
                k, v, po_path
            ), shell=True)

    if opts.dir or opts.all:
        desktop_path = os.path.normpath('%s/../usr/share/applications' % path)
        dir_path = os.path.normpath('%s/../usr/share/desktop-directories' % path)
        for k,v in ini_strings.items():
            proj = v[0]
            filename = v[1]
            if filename.endswith('.desktop'):
                filepath = os.path.join(desktop_path, filename)
            elif filename.endswith('.directory'):
                filepath = os.path.join(dir_path, filename)
            else:
                filepath = os.path.join(path, filename)
            subprocess.call('/home/ju1ius/code/locale/mkdesktop.py "%s" "%s" "%s"' % (
                k, proj, filepath
            ), shell=True)

    print "Executed in %s seconds..." % str(time.clock() - start)
