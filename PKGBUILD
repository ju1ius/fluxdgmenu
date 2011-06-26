# Contributor: David Spicer <azleifel at googlemail dot diddly dot dot com>

pkgname=fluxdgmenu-git
pkgver=20100313
pkgrel=1
pkgdesc="A Fluxbox automated XDG Menu"
arch=('any')
url="http://github.com/ju1ius/fluxdgmenu"
license=('GPL')
depends=('openbox' 'bash' 'libinotifytools0' 'python-xdg')
makedepends=('git')
provides=('fluxdgmenu')
conflicts=('fluxdgmenu')

_gitroot="git://github.com/ju1ius/fluxdgmenu.git"
_gitname="fluxdgmenu"

build() {
  cd "$srcdir"
  msg "Connecting to GIT server...."

  if [ -d $_gitname ] ; then
    cd $_gitname && git pull origin
    msg "The local files are updated."
  else
    git clone $_gitroot $_gitname
  fi

  msg "GIT checkout done or server timeout"
  msg "Starting make..."

  cd "$srcdir/$_gitname"
  make || return 1
  sudo make install
}

