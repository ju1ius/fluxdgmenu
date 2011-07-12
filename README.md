About
=====

FluXDGMenu is an automated XDG Menu system for Fluxbox.

FluXDGMenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.

FluXDGMenu is written in C, bash and python and only requires the following packages:

* fluxbox
* libinotifytools0
* python-xdg

Install
=======

Install dependencies (assuming you already have fluxbox bash and python...):

    sudo aptitude install libinotifytools0 libinotifytools0-dev python-xdg

Optionally, If you want Fluxdgmenu to use your current GTK theme:

    sudo aptitude install python-gtk2

Clone the git repository if you haven't already

    git clone git://github.com/ju1ius/marchobmenu.git
    cd fluxdgmenu

Build and install

    make && sudo make install

Next
====

[Check the wiki](http://github.com/ju1ius/fluxdgmenu/wiki)

-----------------------------------------------------------------------
FluXDGMenu is heavily inspired by:

* [xdg-menu](http://cvs.fedoraproject.org/viewvc/devel/openbox/xdg-menu)
* [mint-fm2](http://packages.linuxmint.com/pool/main/m/mint-fm2/)

