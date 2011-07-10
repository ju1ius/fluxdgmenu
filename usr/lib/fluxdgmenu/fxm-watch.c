#include <stdio.h>
#include <stdlib.h>
#include <syslog.h>
#include <unistd.h>
#include <signal.h>
#include <string.h>
#include <ctype.h>
#include <inotifytools/inotifytools.h>
#include <inotifytools/inotify.h>

/*
 * Compile with: gcc -linotifytools mom-watch.c -o mom-watch -W -Wall -pedantic
 */

void signal_handler(int signum);
void cleanup(void);


int main(int argc, char **argv)
{
  int option, i, res;
  /*
   * daemonize the process ?
   **/
  int daemonize = 0;
  /*
   * list of exclude patterns for inotify events
   **/
  int nb_excludes = 0;
  char **excludes;
  /*
   * command to execute on notification
   **/
  char *command;
  /*
   * log message
   **/
  char message[1024];
  /*
   * the notified event
   **/
  struct inotify_event *event;


  openlog("fxm-daemon", LOG_PID, LOG_USER);

  /*****************************************
   * Process Command line args
   ****************************************/

  excludes = malloc(argc * sizeof(char*));

  while((option = getopt(argc, argv, "c:e:d")) != -1)
  {
    switch(option)
    {
      case 'c':
        command = optarg;
        break;
      case 'd':
        daemonize = 1;
        break;
      case 'e':
        excludes[nb_excludes++] = optarg;
      case '?':
        if (optopt == 'c' || optopt == 'e')
        {
          fprintf (stderr, "Option -%c requires an argument.\n", optopt);
          exit(EXIT_FAILURE);
        }
        else if (isprint(optopt))
        {
          fprintf (stderr, "Unknown option 0\\x%x'.\n", optopt);
          exit(EXIT_FAILURE);
        }
      default:

        break;
    }
  }
  /******************************************
   * Daemonification steps
   *****************************************/
  if(daemonize) daemon(0,0);

  syslog(LOG_INFO, "Starting...");

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
  
  for (i = 0; i < nb_excludes; i++)
  {
    syslog(LOG_INFO, "Ignoring pattern %s", excludes[i]);

    inotifytools_ignore_events_by_regex(excludes[i], 0);  
  }
  /*
   * Loop on the remaining command-line args
   * Exit if a non-existent dir is given
   */
  for (i = optind; i < argc; i++)
  {
    syslog(LOG_INFO, "Watching %s", argv[i]);

    res = inotifytools_watch_recursively(argv[i], IN_CREATE | IN_DELETE | IN_MODIFY);
    if(!res)
    {
      syslog( LOG_ERR, "%s", strerror(inotifytools_error()) );
      exit(EXIT_FAILURE);
    }
  }

  /* Output all events as "<timestamp> <events> <path>" */
  event = inotifytools_next_event(-1);
  while (event)
  {
    inotifytools_snprintf(message, 1024, event, "%T %e %w%f\n");
    syslog(LOG_INFO, "%s", message);

    system(command);
    event = inotifytools_next_event(-1);
  }
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
