About
=====

Fluxdgmenu is an automated XDG Menu system for Fluxbox.

Fluxdgmenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.

Fluxdgmenu is written in C and Python and only requires the following packages:

* fluxbox
* libinotifytools0
* python-xdg

Install
=======

Install dependencies (assuming you already have fluxbox bash and python...):

    sudo aptitude install libinotifytools0 libinotifytools0-dev python-xdg

You can also optionally install the following packages:

* python-gtk2: enables fluxdgmenu to use your current GTK icon theme
* python-gmenu: makes menu generation 2 to 10 times faster

Clone the git repository if you haven't already

    git clone git://github.com/ju1ius/marchobmenu.git
    cd fluxdgmenu

Build and install

    make && sudo make install

Next
====

[Check the wiki](http://github.com/ju1ius/fluxdgmenu/wiki)

-----------------------------------------------------------------------
Fluxdgmenu is heavily inspired by:

* [xdg-menu](http://cvs.fedoraproject.org/viewvc/devel/openbox/xdg-menu)
* [mint-fm2](http://packages.linuxmint.com/pool/main/m/mint-fm2/)

