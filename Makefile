package="fluxdgmenu"
version="1.0"

export prefix=/usr/local
export sysconfdir=/etc

CC=gcc
CFLAGS=-W -Wall -pedantic
LDFLAGS=-linotifytools
EXEC=usr/bin/fluxdgmenud
SRC=src/fluxdgmenud/fluxdgmenud.c

all: fluxdgmenud cXdg locale

fluxdgmenud:
	${CC} ${SRC} -o ${EXEC} ${LDFLAGS} ${CFLAGS}

locale:
	./scripts/make-locale.sh

cXdg:
	./scripts/make-cXdg.sh 0.19


.PHONY: clean install uninstall

clean:
	rm ${EXEC}
	rm -rf usr/share/locale/* 2> /dev/null
	rm -rf usr/lib/fluxdgmenu/cXdg 2> /dev/null

install:
	# lib
	install -d ${prefix}/lib/fluxdgmenu/fluxdgmenu/adapters
	install -m 0755 usr/lib/fluxdgmenu/*.py ${prefix}/lib/fluxdgmenu
	install -m 0755 usr/lib/fluxdgmenu/fluxdgmenu/*.py ${prefix}/lib/fluxdgmenu/fluxdgmenu
	install -m 0755 usr/lib/fluxdgmenu/fluxdgmenu/adapters/*.py ${prefix}/lib/fluxdgmenu/fluxdgmenu/adapters
	# cXdg module
	install -d ${prefix}/lib/fluxdgmenu/cXdg
	install -m 0755 usr/lib/fluxdgmenu/cXdg/*.py ${prefix}/lib/fluxdgmenu/cXdg
	install -m 0755 usr/lib/fluxdgmenu/cXdg/*.so ${prefix}/lib/fluxdgmenu/cXdg
	# bin
	install -d ${prefix}/bin
	install -m 0755 usr/bin/* ${prefix}/bin
	ln -sf -T ${prefix}/lib/fluxdgmenu/fxm-daemon.py ${prefix}/bin/fxm-daemon
	# share
	install -d ${prefix}/share/applications
	install -m 0755 usr/share/applications/* ${prefix}/share/applications
	install -d ${prefix}/share/desktop-directories
	install -m 0755 usr/share/desktop-directories/* ${prefix}/share/desktop-directories
	install -d ${prefix}/share/locale
	cp -R usr/share/locale/* ${prefix}/share/locale
	# etc
	install -d ${sysconfdir}/xdg/menus
	install -m 0755 etc/xdg/menus/* ${sysconfdir}/xdg/menus
	install -d ${sysconfdir}/fluxdgmenu
	install -m 0755 etc/fluxdgmenu/* ${sysconfdir}/fluxdgmenu
	# postinst
	install -m 0755 debian/postinst /var/lib/dpkg/info/fluxdgmenu.postinst
	install -m 0755 debian/postrm /var/lib/dpkg/info/fluxdgmenu.postrm

uninstall:
	-rm -rf ${prefix}/lib/fluxdgmenu
	-rm -rf ${prefix}/share/locale/*/LC_MESSAGES/fluxdgmenu.mo
	-rm -f ${prefix}/share/desktop-directories/fxm-*.directory
	-rm -rf ${sysconfdir}/fluxdgmenu
	-rm -f ${sysconfdir}/xdg/menus/fxm-applications.menu
	-rm -f ${sysconfdir}/xdg/menus/fxm-rootmenu.menu
	-rm -f ${prefix}/bin/fxm-daemon
	-rm -f ${prefix}/bin/fluxdgmenud
	-rm -f /var/lib/dpkg/info/fluxdgmenu.postinst
	-rm -f /var/lib/dpkg/info/fluxdgmenu.postrm
