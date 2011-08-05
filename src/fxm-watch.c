#include <stdio.h>
#include <stdlib.h>
#include <getopt.h>
#include <syslog.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <ctype.h>
#include <inotifytools/inotifytools.h>
#include <inotifytools/inotify.h>

/*
 * Compile with: gcc -linotifytools fxm-watch.c -o fxm-watch -W -Wall -pedantic
 */

void signal_handler(int signum);
void cleanup(void);

int str_has_suffix(const char *str, const char *suffix);


int main(int argc, char **argv)
{
  int i;

  int next_option;
  /* list of short options */
  const char *short_options = "a:b:e:d";
  /* An array listing valid long options */
  static const struct option long_options[] =
  {
    {"apps-command", required_argument, NULL, 'a'},
    {"bookmarks-command", required_argument, NULL, 'b'},
    {"exclude", required_argument, NULL, 'e'},
    {"daemon", no_argument, NULL, 'd'},
    {NULL, 0, NULL, 0} /* End of array need by getopt_long do not delete it*/
  };

  /* ---------- FLAGS ---------- */

  /* daemonize the process ? */
  int daemonize = 0;
  /* watch gtk bookmarks ? */
  int watch_bookmarks = 0;
  int bookmarks_wd = -1;

  /*
   * list of exclude patterns for inotify events
   **/
  int nb_excludes = 0;
  char **excludes;

  /*
   * commands to execute on notification
   **/
  char *apps_command;
  char *bookmarks_command;
  const char *bookmarks_file = ".gtk-bookmarks";

  /* log message */
  char message_buf[1024];

  /*
   * the notified event
   **/
  struct inotify_event *event;

  const char *_home = getenv("HOME");
  size_t length = strlen(_home) + 1;
  char *home = (char*) malloc(length);
  strncat(home, _home, length);

  if(!str_has_suffix(_home, "/"))
  {
    length += 2;
    home = (char*) realloc(home, length);
    strncat(home, "/", length);
  }

  openlog("fxm-daemon", LOG_PID, LOG_USER);

  excludes = malloc(argc * sizeof(char*));
  if(excludes == NULL)
  {
    syslog(LOG_ERR, "Unable to allocate memory fo exclude patterns");
    exit(EXIT_FAILURE);
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
      case 'd':
        daemonize = 1;
        break;
      case 'e':
        excludes[nb_excludes++] = optarg;
      case '?':
        break;
      default:
        break;
    }
  }
  while(next_option != -1);


  /******************************************
   * Daemonification steps
   *****************************************/
  if(daemonize) daemon(0,0);

  syslog(LOG_INFO, "Starting in %s", _home);

  /* Setup signal handling */
  signal(SIGCHLD, SIG_IGN); /* ignore child */
  signal(SIGTSTP, SIG_IGN); /* ignore tty signals */
  signal(SIGTTOU, SIG_IGN);
  signal(SIGTTIN, SIG_IGN);
  signal(SIGHUP, signal_handler);
  signal(SIGINT, signal_handler);
  signal(SIGQUIT, signal_handler);
  signal(SIGTERM, signal_handler);


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
  }

  /* set time format to 24 hour time, HH:MM:SS */
  inotifytools_set_printf_timefmt( "%T" );

  for(i = 0; i < nb_excludes; i++)
  {
    if(!inotifytools_ignore_events_by_regex(excludes[i], 0))
    {
      syslog(LOG_ERR, "Invalid exclude pattern: %s", excludes[i]);
    }
    else
    {
      syslog(LOG_INFO, "Ignoring pattern: %s", excludes[i]);
    }
  }
  free(excludes);

  /*
   * Loop on the remaining command-line args
   * Exit if a non-existent dir is given
   */
  for (i = optind; i < argc; i++)
  {
    if(!inotifytools_watch_recursively(argv[i], IN_CREATE|IN_DELETE|IN_MODIFY))
    {
      syslog( LOG_ERR, "Cannot watch %s: %s", argv[i], strerror(inotifytools_error()) );
    }
    else
    {
      syslog(LOG_INFO, "Watching %s", argv[i]);
    }
  }

  /*
   * Add a watch on ~/.gtk-bookmarks
   */
  if(watch_bookmarks)
  {
    if(!inotifytools_watch_file(home, IN_CLOSE_WRITE))
    {
      syslog( LOG_ERR, "%s: %s", home, strerror(inotifytools_error()) );
    }
    else
    {
      bookmarks_wd = inotifytools_wd_from_filename(home);
      syslog(LOG_INFO, "Watching %s%s", home, bookmarks_file);
    }
  }

  /*
   * Main event loop
   * Output events as "<timestamp> <events> <path>"
   */
  event = inotifytools_next_event(-1);
  while (event)
  {
    if(watch_bookmarks
        && event->wd == bookmarks_wd
        && !strcmp(event->name, bookmarks_file)
    ){
      system(bookmarks_command);
      inotifytools_snprintf(message_buf, 1024, event, "%T %e %w%f\n");
      syslog(LOG_INFO, "%s", message_buf);
    }
    else if(event->wd != bookmarks_wd)
    {
      system(apps_command);
      inotifytools_snprintf(message_buf, 1024, event, "%T %e %w%f\n");
      syslog(LOG_INFO, "%s", message_buf);
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
    return 1;

  str_len = strlen(str);
  suffix_len = strlen(suffix);

  if (str_len < suffix_len)
    return 1;

  return strcmp(str + str_len - suffix_len, suffix) == 0;
}
