#! /usr/bin/env python

import os, time
import fxm.applications, fxm.config, fxm.cache
import cProfile, pstats, resource

def profile_parse_menu():
    pass
    #xdg_0_19.Menu.parse('fxm-applications.menu')
    #etree.parse('fxm-applications.menu')

def profile_applications():
    m = fxm.applications.ApplicationsMenu()
    m.set_adapter('gmenu')
    print m.parse_menu_file('fxm-applications.menu')


def clear_cache():
    fxm.cache.clear()

def do_profile(function, stats_file):
    cProfile.run(function, stats_file)
    p = pstats.Stats(stats_file)
    p.strip_dirs()
    p.sort_stats('time')
    p.print_stats(20)

if __name__ == "__main__":

    h1 = "#" * 80
    h2 = "=" * 60
    h3 = "-" * 40

    #do_profile('profile_parse_menu()', 'parse_menu_stats')
    clear_cache()
    do_profile('profile_applications()',
            'profiles/profile_applications.1.profile')
    do_profile('profile_applications()',
            'profiles/profile_applications.2.profile')

