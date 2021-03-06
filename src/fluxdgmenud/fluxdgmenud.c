#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <regex.h>
#include <syslog.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <inotifytools/inotifytools.h>
#include <inotifytools/inotify.h>

/*
 * Compile with: gcc -linotifytools fluxdgmenud.c -o fluxdgmenud -W -Wall -pedantic
 */

#define DAEMON_NAME           "fluxdgmenud"
#define DESKTOP_FILE_EXT      ".desktop"
#define DIRECTORY_FILE_EXT    ".directory"
#define MENU_FILE_EXT         ".menu"
#define BOOKMARKS_FILE        ".gtk-bookmarks"
#define RECENTLY_USED_FILE    ".recently-used.xbel"
#define APPS_EVENTS           IN_CLOSE_WRITE|IN_DELETE|IN_MOVE
#define BOOKMARKS_EVENTS      IN_CLOSE_WRITE
#define HOME                  getenv("HOME")

void signal_handler(int signum);
void cleanup(void);
int str_has_suffix(const char *str, const char *suffix);


int main(int argc, char **argv)
{
  int i;
  int next_option;
  /* list of short options */
  const char *short_options = "a:b:r:e:dv";
  /* An array listing valid long options */
  static const struct option long_options[] =
  {
    {"apps-command", required_argument, NULL, 'a'},
    {"bookmarks-command", required_argument, NULL, 'b'},
    {"recently-used-command", required_argument, NULL, 'r'},
    {"exclude", required_argument, NULL, 'e'},
    {"daemon", no_argument, NULL, 'd'},
    {"verbose", no_argument, NULL, 'v'},
    {NULL, 0, NULL, 0} /* End of array need by getopt_long do not delete it*/
  };

  /* ---------- OPTIONS ---------- */

  /* daemonize the process ? */
  int daemonize = 0;
  /* verbose output ? */
  int verbose = 0;
  /* watch gtk bookmarks ? */
  int watch_bookmarks = 0;
  /* watch recently_used ? */
  int watch_recently_used = 0;
  /* HOME watch descriptor */
  int home_wd = -1;
  /*
   * exclude pattern for inotify events
   **/
  char *exclude_pattern = NULL;
  /*
   * commands to execute on notification
   **/
  char *apps_command;
  char *bookmarks_command;
  char *recently_used_command;

  /* ---------- VARS ---------- */

  /* log message */
  char message_buf[1024];
  /*
   * the notified event
   **/
  struct inotify_event *event;

  size_t length = strlen(HOME) + 1;
  char *home = (char*) malloc(length);

  strncat(home, HOME, length);
  if(!str_has_suffix(HOME, "/"))
  {
    length += 2;
    home = (char*) realloc(home, length);
    strncat(home, "/", length);
  }

  /*****************************************
   * Process Command line args
   ****************************************/

  do
  {
    next_option = getopt_long(argc, argv, short_options, long_options, NULL);
    switch(next_option)
    {
      case 'a':
        apps_command = optarg;
        break;
      case 'b':
        watch_bookmarks = 1;
        bookmarks_command = optarg;
        break;
      case 'r':
        watch_recently_used = 1;
        recently_used_command = optarg;
        break;
      case 'd':
        daemonize = 1;
        break;
      case 'e':
        exclude_pattern = optarg;
      case 'v':
        verbose = 1;
      case '?':
        break;
      default:
        break;
    }
  }
  while(next_option != -1);

  if(argc - optind == 0)
  {
    printf("Not enough arguments... Please provide at least one file to watch !\n");
    exit(EXIT_FAILURE);
  }

  if(daemonize) daemon(0,0);

  openlog(DAEMON_NAME, LOG_PID, LOG_USER);
  syslog(LOG_INFO, "Starting in %s", HOME);

  /* Setup signal handling */
  signal(SIGCHLD, SIG_IGN); /* ignore child */
  signal(SIGTSTP, SIG_IGN); /* ignore tty signals */
  signal(SIGTTOU, SIG_IGN);
  signal(SIGTTIN, SIG_IGN);
  signal(SIGHUP, signal_handler);
  signal(SIGINT, signal_handler);
  signal(SIGQUIT, signal_handler);
  signal(SIGTERM, signal_handler);
  signal(SIGKILL, signal_handler);


  /*****************************************
   *  Core Functionnalities
   ****************************************/

  /*
   * initialize and watch the entire directory tree from the current working
   * directory downwards for all events
   */
  if(!inotifytools_initialize())
  {
    syslog( LOG_ERR, "%s", strerror(inotifytools_error()) );
    exit(EXIT_FAILURE);
  }

  /* set time format to 24 hour time, HH:MM:SS */
  inotifytools_set_printf_timefmt( "%T" );

  if(exclude_pattern)
  {
    if(!inotifytools_ignore_events_by_regex(exclude_pattern, REG_EXTENDED))
    {
      syslog(LOG_ERR, "Invalid exclude pattern: %s", exclude_pattern);
    }
    else if (verbose)
    {
      syslog(LOG_INFO, "Ignoring pattern: %s", exclude_pattern);
    }
  }
  /*
   * Loop on the remaining command-line args
   */
  for (i = optind; i < argc; i++)
  {
    if(!inotifytools_watch_recursively(argv[i], APPS_EVENTS))
    {
      syslog( LOG_ERR, "Cannot watch %s: %s", argv[i], strerror(inotifytools_error()) );
    }
    else if (verbose)
    {
      syslog(LOG_INFO, "Watching %s", argv[i]);
    }
  }
  /*
   * Add a watch on ~/.gtk-bookmarks
   */
  if(watch_bookmarks || watch_recently_used)
  {
    if(!inotifytools_watch_file(home, BOOKMARKS_EVENTS))
    {
      syslog( LOG_ERR, "%s: %s", home, strerror(inotifytools_error()) );
    }
    else
    {
      home_wd = inotifytools_wd_from_filename(home);
      if (verbose)
      {
        syslog(LOG_INFO, "Watching %s", home);
      }
    }
  }

  /*
   * Main event loop
   * Output events as "<timestamp> <events> <path>"
   */
  event = inotifytools_next_event(-1);
  while (event)
  {
    if(
        (watch_bookmarks || watch_recently_used)
        && event->wd == home_wd
    ){
      if(strcmp(event->name, RECENTLY_USED_FILE) == 0)
      {
        if (verbose)
        {
          inotifytools_snprintf(message_buf, 1024, event, "%T %e %w%f\n");
          syslog(LOG_INFO, "%s >>> %s", message_buf, recently_used_command);
        }
        system(recently_used_command);
      }
      else if(strcmp(event->name, BOOKMARKS_FILE) == 0)
      {
        if (verbose)
        {
          inotifytools_snprintf(message_buf, 1024, event, "%T %e %w%f\n");
          syslog(LOG_INFO, "%s >>> %s", message_buf, bookmarks_command);
        }
        system(bookmarks_command);
      }
    }
    else if(
      event->wd != home_wd
      && (str_has_suffix(event->name, DESKTOP_FILE_EXT)
        || str_has_suffix(event->name, DIRECTORY_FILE_EXT)
        || str_has_suffix(event->name, MENU_FILE_EXT)
      )
    ){
      if (verbose)
      {
        inotifytools_snprintf(message_buf, 1024, event, "%T %e %w%f\n");
          syslog(LOG_INFO, "%s >>> %s", message_buf, apps_command);
      }
      system(apps_command);
    }
    event = inotifytools_next_event(-1);
  }

  /*
   * Cleanup
   */
  free(home);
  cleanup();

  return 0;
}

void cleanup(void)
{
  inotifytools_cleanup();
  syslog(LOG_INFO, "Exiting...");
  closelog();
}

void signal_handler(int signum)
{
  (void) signum;
  cleanup();
  exit(0);
}


/*
 * String utilities
 **/

int str_has_suffix(const char *str, const char *suffix)
{
  size_t str_len;
  size_t suffix_len;

  if(str == NULL || suffix == NULL)
    return 0;

  str_len = strlen(str);
  suffix_len = strlen(suffix);

  if (str_len < suffix_len)
    return 0;

  return strcmp(str + str_len - suffix_len, suffix) == 0;
}
