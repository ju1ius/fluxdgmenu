import os, pwd, subprocess
from . import config

def list_real_users():
    """Finds real users by reading /etc/pswd
        returns a Tuple containing the username and home dir"""
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

def zenity_progress(cmd, opts_str=' '):
    """Displays a zenity progress bar for the given command"""
    subprocess.call(
        "(%s%s%s) | zenity --progress --pulsate --auto-close" % (
            config.APP_DAEMON, opts_str, cmd
        ),
        shell=True
    )

def get_options_for_progress(options):
    # Remember to leave spaces around options !!!
    if options.all:
        return ' -a '
    opt_str = ' '
    if options.with_bookmarks:
        opt_str += '-b '
    if options.with_recently_used:
        opt_str += '-r '
    return opt_str
