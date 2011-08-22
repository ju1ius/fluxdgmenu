#! /usr/bin/env python

import os, sys, subprocess, optparse
import fxm.config as config
import fxm.daemon as daemon
import fxm.utils as utils

if __name__ == '__main__':
    usage = "%prog [options] command"
    description = """Commands:
  help                  prints the help message and exits
  start                 starts the menu daemon
  stop                  stops the menu daemon
  update                regenerates the applications menu
  update-bookmarks      regenerates the bookmarks menu
  update-recently-used  regenerates the recently used files menu
  update-icons          regenerates the icon cache,
                        then updates applications and bookmarks menus
  generate-rootmenu     generates a rootmenu
  enable-triggers       add dpkg-triggers
  disable-triggers      remove dpkg-triggers

About dpkg-triggers:
  dpkg-triggers are a Debian/Apt specific way to trigger actions
  when a new package is installed/removed.
  They allow updating the menu without the overhead
  of running a daemon.

  However, they only work with packages installed by apt or dpkg.
  This is why they are not enabled by default.

  If you wish to activate this feature, first stop the daemon:
  $ %prog stop
  Then execute:
  $ %prog enable-triggers

  From now on, if you install a program in a non-standard way,
  like compiling from source, or a wine application,
  you'll need to explicitly update the menu by executing:
  $ %prog update

  You can deactivate this feature later by executing:
  $ %prog disable-triggers
"""

    parser = config.OptionParser(
        usage = usage, epilog = description      
    )
    parser.add_option(
        '-v', '--verbose', action='store_true',
        help="be verbose and log inotify events to syslog"
    )
    parser.add_option(
        '-b', '--with-bookmarks', action='store_true',
        help="monitor GTK bookmarks"
    )
    parser.add_option(
        '-r', '--with-recently-used', action='store_true',
        help="monitor recently used files"
    )
    parser.add_option(
        '-p', '--progress', action='store_true',
        help="display a progress bar if zenity is installed"
    )
    ( options, args ) = parser.parse_args()

    if options.verbose:
        import time
        start_t = time.clock()
    if len(args) == 0:
        parser.print_usage()
        sys.exit(1)

    if options.progress:
        if not utils.which('zenity'):
            options.progress = False

    command = args[0]
    if command == 'start' or command == 'restart':
        daemon.start(options)
    elif command == 'stop':
        daemon.stop()
    elif command == 'update':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update()
    elif command == 'update-bookmarks':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update_bookmarks()
    elif command == 'update-recently-used':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update_recently_used()
    elif command == 'clear-recently-used':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.clear_recently_used()
    elif command == 'generate-rootmenu':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.generate_rootmenu()
    elif command == 'update-icons':
        if options.progress:
            utils.zenity_progress(command)
        else:
            daemon.update_icons()
    elif command == 'enable-triggers':
        daemon.enable_triggers()
    elif command == 'disable-triggers':
        daemon.disable_triggers()
    else:
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        end_t = time.clock()
        print "Executed in %s seconds" % str(end_t - start_t)

    sys.exit(0)
