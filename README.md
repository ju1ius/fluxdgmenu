h2. About

FluXDGMenu is an automated XDG Menu system for Fluxbox.

FluXDGMenu monitors for newly installed/removed applications,
and maintains a submenu, listing and categorizing them like the Gnome/Xfce/Lxde menu.

FluXDGMenu is written in C, bash and python and only requires the following packages:
- fluxbox
- libinotifytools0
- python-xdg

h2. Install

Install dependencies (assuming you already have fluxbox bash and python...):
```bash
sudo aptitude install libinotifytools0 libinotifytools0-dev python-xdg
git clone git://github.com/ju1ius/marchobmenu.git
cd fluxdgmenu
make
sudo make install
```

h2. Next

Check the wiki: http://github.com/ju1ius/fluxdgmenu/wiki


-----------------------------------------------------------------------
FluXDGMenu is heavily inspired by:

* xdg-menu (http://cvs.fedoraproject.org/viewvc/devel/openbox/xdg-menu)
* mint-fm2 (http://packages.linuxmint.com/pool/main/m/mint-fm2/)

