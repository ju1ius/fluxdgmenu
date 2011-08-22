import os, sys, subprocess
from . import config, utils, cache

def start(opts):
    """starts the daemon"""
    check_triggers()
    stop()
    update()
    cmd = [config.APP_WATCH, '--daemon',
        '--apps-command', '"%s update"' % config.APP_DAEMON
    ]
    # Add exclude patterns
    cmd.extend(['--exclude', "|".join(config.EXCLUDED)])
    # Log events
    if opts.verbose:
        cmd.append('--verbose')
    # Gtk Bookmarks)
    if opts.with_bookmarks:
        cmd.extend([
            '--bookmarks-command',
            '"%s update-bookmarks"' % config.APP_DAEMON
        ])
    # Recently Used items
    if opts.with_recently_used:
        cmd.extend([
            '--recently-used-command',
            '"%s update-recently-used"' % config.APP_DAEMON
        ])
    # Add monitored dirs
    for d in config.MONITORED:
        cmd.append(os.path.expanduser(d))

    if opts.verbose:
        print "Starting daemon..."
        print cmd
    subprocess.call(cmd)

def stop():
    """stops the daemon"""
    subprocess.call(['pkill', '-u', os.environ['USER'], config.APP_WATCH])

def update():
    """updates the menu"""
    import fxm.applications
    menu = fxm.applications.ApplicationsMenu()
    with open(config.MENU_CACHE, 'w+') as fp:
        fp.write(menu.parse_menu_file(config.MENU_FILE))

def update_icons():
    """Updates the menu and flush the icon cache"""
    try:
        cache.clear()
    except OSError, why:
        sys.exit("Could not remove %s: %s" % (config.CACHE_DB, why))
    update()

def update_bookmarks():
    import fxm.bookmarks
    menu = fxm.bookmarks.BookmarksMenu()
    with open(config.BOOKMARKS_CACHE, 'w+') as fp:
        fp.write(menu.parse_bookmarks())

def update_recently_used():
    import fxm.recently_used
    menu = fxm.recently_used.RecentlyUsedMenu()
    with open(config.RECENTLY_USED_CACHE, 'w+') as fp:
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
    import fxm.rootmenu
    menu = fxm.rootmenu.RootMenu()
    with open(rootmenu, 'w+') as fp:
        fp.write(menu.parse_menu_file(config.ROOTMENU_FILE))

def disable_triggers():
    if not os.path.isfile(config.TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    subprocess.call(
        'sudo sed -i -e "/%s$/d" %s' % (config.PKG_NAME, config.TRIGGERS_DB),
        shell=True
    )

def enable_triggers():
    """Add dpkg interests for the monitored directories
        If the directory is in userspace (under '~'),
        we attempt to add an interest for all existing real users."""
    if not os.path.isfile(config.TRIGGERS_DB):
        sys.exit("Your system doesn't support dpkg-triggers. Please use the daemon instead.")
    stop()
    disable_triggers()
    interests = []
    for d in config.MONITORED:
        if d.startswith('~'):
            for (user, home) in utils.list_real_users():
                interests.append(d.replace('~', home, 1))
        else:
            interests.append(d)
    for i in interests:
        subprocess.call(
            "echo %s %s | sudo tee -a %s" % (
                i, config.PKG_NAME, config.TRIGGERS_DB
            ),
            shell=True
        )

def check_triggers():
    """Checks for presence of dpkg-triggers"""
    r = subprocess.call(
        "grep %s %s > /dev/null" % (config.PKG_NAME, config.TRIGGERS_DB),
        shell=True
    )
    if r == 0:
        print """
It seems you have dpkg-triggers running for %(p)s !
You must disable them before starting the daemon by running:
    %(d)s disable-triggers
If you want to know more about dpkg-triggers, run:
    %(d)s --help
""" % { "p": config.PKG_NAME, "d": config.APP_DAEMON }
        sys.exit(1)

