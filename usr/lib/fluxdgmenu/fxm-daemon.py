#! /usr/bin/env python

import os, sys, subprocess, optparse

################################################################################
#		CONSTANTS
#-------------------------------------------------------------------------------
APP_DAEMON = "fxm-daemon"
APP_WATCH = "fluxdgmenud"
PKG_NAME = "fluxdgmenu"
TRIGGERS_DB = "/var/lib/dpkg/triggers/File"

CACHE_DIR = os.path.expanduser('~/.fluxbox/fluxdgmenu')
if not os.path.isdir(CACHE_DIR):
    try:
        os.makedirs(CACHE_DIR)
    except OSError, why:
        sys.exit("Could not create %s: %s" % (CACHE_DIR, why))

ICONS_CACHE = os.path.join(CACHE_DIR, 'icons.db')
MENU_CACHE = os.path.join(CACHE_DIR, 'applications')
BOOKMARKS_CACHE = os.path.join(CACHE_DIR, 'bookmarks')
RECENTLY_USED_CACHE = os.path.join(CACHE_DIR, 'recently-used')

# List of directories to monitor
# fxm-watch will only respond to events on files
# having one of these extensions: .desktop|.directory|.menu
MONITORED = [
    # .directory files
    "/usr/share/desktop-directories",
    "/usr/local/share/desktop-directories",
    "~/.local/share/desktop-directories",
    # .desktop files
    "/usr/share/applications",
    "/usr/local/share/applications",
    "~/.local/share/applications",
    # .menu files
    "/etc/xdg/menus",
    "~/.config/menus"
]
# List of regex patterns to exclude
# note that theses are C POSIX extended regex patterns,
# so literal special characters must be double escaped !
EXCLUDED = [
    # Debian menu entries
    "/.local/share/applications/menu-xdg/"
]
#-------------------------------------------------------------------------------
#		/CONSTANTS
################################################################################



################################################################################
#		FUNCTIONS
#-------------------------------------------------------------------------------

# ---------- Public API ----------#

def start(opts):
    """starts the daemon"""
    check_triggers()
    stop()
    update()
    cmd = [APP_WATCH, '--daemon',
        '--apps-command', '"%s update"' % APP_DAEMON
    ]
    # Add exclude patterns
    cmd.extend(['--exclude', "|".join(EXCLUDED)])
    # Log events
    if opts.verbose:
        cmd.append('--verbose')
    # Gtk Bookmarks)
    if opts.with_bookmarks:
        cmd.extend([
            '--bookmarks-command',
            '"%s update-bookmarks"' % APP_DAEMON
        ])
    # Recently Used items
    if opts.with_recently_used:
        cmd.extend([
            '--recently-used-command',
            '"%s update-recently-used"' % APP_DAEMON]
        )
    # Add monitored dirs
    for d in MONITORED:
        cmd.append(os.path.expanduser(d))

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop():
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], APP_WATCH])

def update():
    """updates the menu"""
    import fluxdgmenu.applications
    menu = fluxdgmenu.applications.ApplicationsMenu()
    with open(MENU_CACHE, 'w+') as fp:
        fp.write(menu.parse_menu_file("fxm-applications.menu"))

def update_icons():
    """Updates the menu and flush the icon cache"""
    try:
        os.remove(ICONS_CACHE)
    except OSError, why:
        sys.exit("Could not remove %s: %s" % (ICONS_CACHE, why))
    update()

def update_bookmarks():
    import fluxdgmenu.bookmarks
    menu = fluxdgmenu.bookmarks.BookmarksMenu()
    with open(BOOKMARKS_CACHE, 'w+') as fp:
        fp.write(menu.parse_bookmarks())

def update_recently_used():
    import fluxdgmenu.recently_used
    menu = fluxdgmenu.recently_used.RecentlyUsedMenu()
    with open(RECENTLY_USED_CACHE, 'w+') as fp:
        fp.write(menu.parse_bookmarks())

def clear_recently_used():
    with open(os.path.expanduser('~/.recently-used.xbel'), 'w') as f:
        f.write("""<?xml version="1.0" encoding="UTF-8"?>
<xbel version="1.0"
      xmlns:bookmark="http://www.freedesktop.org/standards/desktop-bookmarks"
      xmlns:mime="http://www.freedesktop.org/standards/shared-mime-info"
>
</xbel>""")
    update_recently_used()

def generate_rootmenu():
    update_icons()
    update_bookmarks()
    update_recently_used()
    rootmenu = os.path.expanduser('~/.fluxbox/menu')
    if os.path.isfile(rootmenu):
        try:
            os.rename(rootmenu, "%s.bak" % rootmenu)
        except OSError, why:
            sys.exit("Could not backup previous rootmenu: %s" % why)
    import fluxdgmenu.rootmenu
    menu = fluxdgmenu.rootmenu.RootMenu()
    with open(rootmenu, 'w+') as fp:
        fp.write(menu.parse_menu_file('fxm-rootmenu.menu'))

def disable_triggers():
    if not os.path.isfile(TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    subprocess.call(
        'sudo sed -i -e "/%s$/d" %s' % (PKG_NAME, TRIGGERS_DB),
        shell=True
    )

def enable_triggers():
    """Add dpkg interests for the monitored directories
        If the directory is in userspace (under '~'),
        we attempt to add an interest for all existing real users."""
    if not os.path.isfile(TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    stop()
    disable_triggers()
    interests = []
    for d in MONITORED:
        if d.startswith('~'):
            for (user, home) in list_real_users():
                interests.append(d.replace('~', home, 1))
        else:
            interests.append(d)
    for i in interests:
        subprocess.call(
            "echo %s %s | sudo tee -a %s" % (i, PKG_NAME, TRIGGERS_DB),
            shell=True
        )


# ---------- Utilities ----------#

def check_triggers():
    """Checks for presence of dpkg-triggers"""
    r = subprocess.call(
        "grep %s %s > /dev/null" % ( PKG_NAME, TRIGGERS_DB ),
        shell=True
    )
    if r == 0:
        print """
It seems you have dpkg-triggers running for %(p)s !
You must disable them before starting the daemon by running:
    %(d)s disable-triggers
If you want to know more about dpkg-triggers, run:
    %(d)s --help
""" % { "p": PKG_NAME, "d": APP_DAEMON }
        sys.exit(1)

def list_real_users():
    """Finds real users by reading /etc/pswd
        returns a Tuple containing the username and home dir"""
    import pwd
    for p in pwd.getpwall():
        if p[5].startswith('/home') and p[6] != "/bin/false":
            yield (p[0], p[5])

def which(program):
    """Check for external modules or programs"""
    def is_exe(fpath):
        return os.path.exists(fpath) and os.access(fpath, os.X_OK)
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def zenity_progress(cmd):
    """Displays a zenity progress bar for the given command"""
    subprocess.call(
        "(%s %s) | zenity --progress --pulsate --auto-close" % (APP_DAEMON, cmd),
        shell=True
    )

class MyOptionParser(optparse.OptionParser):
    """Custom Option parser for better help formatting"""
    def format_epilog(self, formatter):
        return "\n%s\n" % self.expand_prog_name(self.epilog)

#-------------------------------------------------------------------------------
#		/FUNCTIONS)
################################################################################



################################################################################
#		MAIN
#-------------------------------------------------------------------------------
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

    parser = MyOptionParser(
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
        if not which('zenity'):
            options.progress = False

    command = args[0]
    if command == 'start' or command == 'restart':
        start(options)
    elif command == 'stop':
        stop()
    elif command == 'update':
        if options.progress:
            zenity_progress(command)
        else:
            update()
    elif command == 'update-bookmarks':
        if options.progress:
            zenity_progress(command)
        else:
            update_bookmarks()
    elif command == 'update-recently-used':
        if options.progress:
            zenity_progress(command)
        else:
            update_recently_used()
    elif command == 'clear-recently-used':
        if options.progress:
            zenity_progress(command)
        else:
            clear_recently_used()
    elif command == 'generate-rootmenu':
        if options.progress:
            zenity_progress(command)
        else:
            generate_rootmenu()
    elif command == 'update-icons':
        if options.progress:
            zenity_progress(command)
        else:
            update_icons()
    elif command == 'enable-triggers':
        enable_triggers()
    elif command == 'disable-triggers':
        disable_triggers()
    else:
        parser.print_help()
        sys.exit(1)

    if options.verbose:
        end_t = time.clock()
        print "Executed in %s seconds" % str(end_t - start_t)

    sys.exit(0)
